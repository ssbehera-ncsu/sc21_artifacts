import simpy
import random
import pickle
class Failure:
    def __init__(self, id, frequency, meanleadtime, stddev, startphrase, endphrase, failure_type):
        self.frequency = frequency
        self.meanleadtime = meanleadtime
        self.stddev = stddev
        self.startphrase = startphrase
        self.endphrase = endphrase
        self.id = id
        self.failure_type = failure_type


class System_Failure:
    def __init__(self, env, tbf_distr, nodes, node_failures, soft_failures, live_migration_threshold):
        self.env = env
        self.tbf_distr = tbf_distr
        #self.ckpt_plcmnt = ckpt_plcmnt
        self.nodes = nodes
        self.fail_time = []
        self.fail_client_ids = []
        self.failure_ids = []
        self.failures_generated = []
        self.node_failures = node_failures
        self.soft_failures = soft_failures
        #self.latest_failure = None
        self.live_migration_threshold = live_migration_threshold
        self.latest_leadtime = 0

        total_count = 0
        for node_failure in self.node_failures:
            total_count += node_failure.frequency
        for soft_failure in self.soft_failures:
            total_count += soft_failure.frequency

        for node_failure in self.node_failures:
            node_failure.probability = node_failure.frequency / total_count

        for soft_failure in self.soft_failures:
            soft_failure.probability = soft_failure.frequency / total_count

        self.failures = []
        self.probabilities = []

        index = 0
        for failure in self.node_failures + self.soft_failures:
            self.failures.append(failure)
            if index == 0:
                self.probabilities.append(failure.probability)
            else:
                self.probabilities.append(failure.probability + self.probabilities[index - 1])
            index += 1

        self.new_failure_leadtimes = pickle.load(open("failureleadtime", "rb"))
        self.failure_leadtimes_len = []

        index = 0
        for failure_leadtimes in self.new_failure_leadtimes:
            if index == 0:
                self.failure_leadtimes_len.append(len (failure_leadtimes))
            else:
                self.failure_leadtimes_len.append(len (failure_leadtimes) + self.failure_leadtimes_len[index - 1])
            index += 1

        self.all_failure_leadtimes = [j for sub in self.new_failure_leadtimes for j in sub]
        self.all_failure_leadtimes = [element for element in self.all_failure_leadtimes]

    def lm_pct1(self, live_migration_threshold):
        count = 0
        for failure in self.node_failures + self.soft_failures:
            if (failure.meanleadtime / 3600) >= live_migration_threshold:
                count += failure.frequency
            #print (failure.meanleadtime/3600, live_migration_threshold, count, failure.frequency)
        return float(count / len (self.all_failure_leadtimes))

    def lm_pct(self, live_migration_threshold):
        count = 0
        for failure_leadtime in self.all_failure_leadtimes:
            if failure_leadtime >= (live_migration_threshold * 3600):
                count += 1
        return float(count / len (self.all_failure_leadtimes))

    def run(self, apps, bb, pfs):
        while True:
            operation_start_time = self.env.now

            probability = random.randint (0, len(self.all_failure_leadtimes) - 1)

            self.latest_leadtime = self.all_failure_leadtimes[probability]

            #print('failure lead time', self.latest_leadtime)

            index = 0
            for failure_leadtimes in self.new_failure_leadtimes:
                if self.failure_leadtimes_len[index] >= probability:
                    self.latest_failure = self.failures[index]
                    self.failure_ids.append(self.latest_failure.id)
                    break
                index += 1
            '''    
            index = 0
            for failure in self.failures:
                if self.probabilities[index] >= probability:
                    self.latest_failure = failure
                    #print('failure generated', failure.id, 'with lead time', failure.meanleadtime / 3600, 'hrs')
                    self.failure_ids.append(failure.id)
                    break
                index += 1
            '''
            tbf = self.tbf_distr.draw()

            fail_client_id = random.randint(0, self.nodes-1)

            # wait till the alarm.
            #print('failure model: tbf:', tbf)
            #print('failure model: waiting till the alarm time:', tbf - (self.latest_failure.meanleadtime / 3600))

            if (tbf >= (self.latest_leadtime / 3600)):
                yield self.env.timeout(tbf - (self.latest_leadtime / 3600))

                for app_proc in self.app_procs:
                    if app_proc.get_exe().is_alive and app_proc.get_app().client_belong_to(fail_client_id):
                        failed_app = app_proc.get_app()
                        #print('alarming app:', failed_app.id)
                        app_proc.get_exe().interrupt('alarm')

                # wait for the lead time.
                #print('waiting for the failure:', self.latest_failure.meanleadtime / 3600)
                yield self.env.timeout((self.latest_leadtime / 3600))
            else:
                yield self.env.timeout(tbf)


            for app_proc in self.app_procs:
                if app_proc.get_exe().is_alive and app_proc.get_app().client_belong_to(fail_client_id):
                    if self.latest_leadtime / 3600 < app_proc.get_app().live_migration_threshold:
                        app_proc.get_exe().interrupt('failure')
                        failed_app = app_proc.get_app()
                        self.fail_time.append(operation_start_time + tbf)
                        self.failures_generated.append(self.latest_failure)
                        self.fail_client_ids.append(failed_app.id)

    def run1(self, apps, bb, pfs):
        while True:
            operation_start_time = self.env.now

            probability = random.random()
            index = 0
            for failure in self.failures:
                if self.probabilities[index] >= probability:
                    self.latest_failure = failure
                    #print('failure generated', failure.id, 'with lead time', failure.meanleadtime / 3600, 'hrs')
                    self.failure_ids.append(failure.id)
                    break
                index += 1

            tbf = self.tbf_distr.draw()

            fail_client_id = random.randint(0, self.nodes-1)

            # wait till the alarm.
            #print('failure model: tbf:', tbf)
            #print('failure model: waiting till the alarm time:', tbf - (self.latest_failure.meanleadtime / 3600))

            if (tbf >= (self.latest_failure.meanleadtime / 3600)):
                yield self.env.timeout(tbf - (self.latest_failure.meanleadtime / 3600))

                for app_proc in self.app_procs:
                    if app_proc.get_exe().is_alive and app_proc.get_app().client_belong_to(fail_client_id):
                        failed_app = app_proc.get_app()
                        #print('alarming app:', failed_app.id)
                        app_proc.get_exe().interrupt('alarm')

                # wait for the lead time.
                #print('waiting for the failure:', self.latest_failure.meanleadtime / 3600)
                yield self.env.timeout((self.latest_failure.meanleadtime / 3600))
            else:
                yield self.env.timeout(tbf)



            for app_proc in self.app_procs:
                if app_proc.get_exe().is_alive and app_proc.get_app().client_belong_to(fail_client_id):
                    if self.latest_failure.meanleadtime / 3600 < app_proc.get_app().live_migration_threshold:
                        app_proc.get_exe().interrupt('failure')
                        failed_app = app_proc.get_app()
                        self.fail_time.append(operation_start_time + tbf)
                        self.failures_generated.append(self.latest_failure)
                        self.fail_client_ids.append(failed_app.id)


            #self.ckpt_plcmnt.run(apps, self, bb, pfs)

    def get_fail_time(self):
        return self.fail_time

    def get_num_fail(self):
        return len(self.fail_time)

    def get_last_fail_time(self):
        if self.fail_time:
            return self.fail_time[-1]
        else:
            return 0

    def get_tbf_distr(self):
        return self.tbf_distr

    def get_nodes_num(self):
        return self.nodes

import simpy
import random
import time
import threading
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
    def __init__(self, env, tbf_distr, nodes, node_failures, soft_failures):
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
        self.latest_failure = None
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

    def run(self, apps, bb, pfs):
        while True:
            operation_start_time = self.env.now

            probability = random.random()
            #print('pro', probability)
            index = 0
            for failure in self.failures:
                if self.probabilities[index] >= probability:
                    self.latest_failure = failure
                    #print('failure assigned')
                    self.failure_ids.append(failure.id)
                    break
                index += 1

            tbf = self.tbf_distr.draw()
            yield self.env.timeout(tbf)

            #print(self.number_of_clients)

            fail_client_id = random.randint(0, self.nodes - 1)

            for app_proc in self.app_procs:
                if app_proc.get_exe().is_alive and app_proc.get_app().client_belong_to(fail_client_id):
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

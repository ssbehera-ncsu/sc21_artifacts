import simpy
import random
from random import randint
import heapq
from collections import deque

class Scientific_App():
    def __init__(self, env, resource, name, id, start_time, comp_period, ckpt_size, clients, client_id_start, client_id_end, total_comp_time, ckpt2bb_percnt):
        self.env = env
        self.resource = resource
        self.name = name
        self.id = id
        self.start_time = start_time
        self.comp_period = comp_period
        self.ckpt_size = ckpt_size
        self.clients = clients
        self.client_id_start = client_id_start
        self.client_id_end = client_id_end
        self.total_comp_time = total_comp_time
        self.comp_intvs = []
        self.ckpt_intvs = []
        self.waste_intvs = []
        self.restart_intvs = []
        self.comp_saved_ckpt_intvs = []
        self.ckpt_intervals = []
        self.ckpt_2bb_percentages = []
        self.no_of_ckpts = 0
        self.last_ckpt_id = -1
        self.ckpt_loc = deque([])
        #self.ckpt_loc = []
        self.curnt_ckpt_loc = 'BB'
        self.interruptions = 0
        self.status = ''
        self.ckpt2bb_percnt = ckpt2bb_percnt
        self.sys_fail = None
        self.failure_alarm = False
        self.comp_start_time = 0
        self.ckpt_start_time = 0
        self.ckpt_period = 0
        self.rand = 0
        self.ckpt_in_progress = False
        self.pckpt_in_progress = False
        self.p_queue = []
        self.sp_queue = []
        self.pckpt_start_time = -1
        #self.pckpt_bb_start_time = -1
        self.pckpt_pfs_start_time = -1
        self.pckpt_end_time = -1
        #self.pckpt_bb_end_time = -1
        self.pckpt_pfs_end_time = -1
        self.last_ckpt_pfs = False
        self.time_to_failure = -1
        self.failed_client_id = -1
        self.pckpt_pfs_commit_count = 0
        #self.pckpt_bb_in_progress = False
        self.pckpt_pfs_in_progress = False
        self.failured_handled = False
        self.calculate = False
        self.pckpt_fake_failure_alarm = False
        self.fake_failure_alarm = False

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id

    def client_belong_to(self, client_id):
        if client_id >= self.client_id_start and client_id <= self.client_id_end:
            return True
        else:
            return False

    def get_random_node(self):
        client_id = randint(0, self.clients - 1)
        return self.client_id_start + client_id

    def get_comp_period(self):
        return self.comp_period

    def get_ckpt_size(self):
        return self.ckpt_size

    def add_ckpt_loc(self, ckpt_loc):
        self.ckpt_loc.append(ckpt_loc)
    #def add_ckpt_loc(self, idx, ckpt_loc):
    #    self.ckpt_loc.insert(idx, ckpt_loc)

    def pop_ckpt_loc(self):
        return self.ckpt_loc.popleft()

    def clear_ckpt_loc(self):
        return self.ckpt_loc.clear()

    def pckpt_reset(self, pfs):
        #print(self.name, 'pckpt reset')
        if self.failured_handled == True:
            #print(self.name, 'failure handled')
            if self.calculate == True:
                #print (self.name, 'calculated')
                if self.ckpt_intvs:
                    if self.comp_intvs and self.ckpt_intvs[-1][1] < self.comp_intvs[-1][1]:
                        if self.pckpt_fake_failure_alarm == False:
                            self.comp_saved_ckpt_intvs.append([self.comp_intvs[-1][0], self.comp_intvs[-1][1]])
                    else:
                        if self.comp_intvs and self.ckpt_intvs[-1][1] + self.pfs_ckpt_period > self.pckpt_start_time:
                            comp_period = self.pckpt_start_time - self.comp_start_time
                            if self.pckpt_fake_failure_alarm == False:
                                self.comp_saved_ckpt_intvs.append([self.comp_intvs[-1][0], self.comp_intvs[-1][1]])
                                self.comp_saved_ckpt_intvs.append(
                                    [self.comp_start_time, self.comp_start_time + comp_period])
                            self.comp_intvs.append([self.comp_start_time, self.comp_start_time + comp_period])
                            #print(self.name, 'pckpt reset', self.comp_intvs[-1])
                        else:
                            comp_period = self.pckpt_start_time - self.comp_start_time
                            self.comp_intvs.append([self.comp_start_time, self.comp_start_time + comp_period])
                            if self.pckpt_fake_failure_alarm == False:
                                self.comp_saved_ckpt_intvs.append(
                                    [self.comp_start_time, self.comp_start_time + comp_period])
                            #print(self.name, 'pckpt reset', self.comp_intvs[-1])
                else:
                    if self.comp_intvs:
                        if self.pckpt_fake_failure_alarm == False:
                            self.comp_saved_ckpt_intvs.append([self.comp_intvs[-1][0], self.comp_intvs[-1][1]])
                    else:
                        self.comp_intvs.append([0, self.pckpt_start_time])
                        #print(self.name, 'pckpt reset', self.comp_intvs[-1])
                        if self.pckpt_fake_failure_alarm == False:
                            self.comp_saved_ckpt_intvs.append([0, self.pckpt_start_time])

        self.calculate = False
        self.pckpt_start_time = -1
        #self.pckpt_bb_start_time = -1
        self.pckpt_pfs_start_time = -1
        self.pckpt_end_time = -1
        #self.pckpt_bb_end_time = -1
        self.pckpt_pfs_end_time = -1
        self.pckpt_in_progress = False
        #self.pckpt_bb_in_progress = False
        self.pckpt_pfs_in_progress = False
        self.p_queue.clear()
        self.sp_queue.clear()
        self.pckpt_fake_failure_alarm = False

    def pckpt_start(self, time_to_failure):
        self.pckpt_start_time = -1
        #self.pckpt_bb_start_time = -1
        self.pckpt_pfs_start_time = -1
        self.pckpt_end_time = -1
        #self.pckpt_bb_end_time = -1
        self.pckpt_pfs_end_time = -1
        self.pckpt_in_progress = True
        self.pckpt_start_time = self.env.now
        self.p_queue.clear()
        self.sp_queue.clear()
        heapq.heappush(self.p_queue, (time_to_failure, self.failed_client_id))
        #print('pckpt start', self.failed_client_id)

    def pckpt_end(self, bb, pfs):
        #print(self.name, 'pckpt ended')
        self.pckpt_in_progress = False
        self.pckpt_end_time = self.env.now
        #print (self.name, 'pckpt ended')
        if self.ckpt_intvs:
            if self.ckpt_intvs[-1][1] < self.comp_intvs[-1][1]:
                if self.pckpt_fake_failure_alarm == False:
                    self.comp_saved_ckpt_intvs.append([self.comp_intvs[-1][0], self.comp_intvs[-1][1]])
            else:
                if self.ckpt_intvs[-1][1] + self.pfs_ckpt_period > self.pckpt_start_time:
                    comp_period = self.pckpt_start_time - self.comp_start_time
                    if self.pckpt_fake_failure_alarm == False:
                        self.comp_saved_ckpt_intvs.append([self.comp_intvs[-1][0], self.comp_intvs[-1][1]])
                        self.comp_saved_ckpt_intvs.append(
                            [self.comp_start_time, self.comp_start_time + comp_period])
                    self.comp_intvs.append([self.comp_start_time, self.comp_start_time + comp_period])
                    #print(self.name, 'pckpt end', self.comp_intvs[-1])
                else:
                    comp_period = self.pckpt_start_time - self.comp_start_time
                    self.comp_intvs.append([self.comp_start_time, self.comp_start_time + comp_period])
                    if self.pckpt_fake_failure_alarm == False:
                        self.comp_saved_ckpt_intvs.append(
                            [self.comp_start_time, self.comp_start_time + comp_period])
                    #print(self.name, 'pckpt end', self.comp_intvs[-1])
        else:
            if self.comp_intvs:
                if self.pckpt_fake_failure_alarm == False:
                    self.comp_saved_ckpt_intvs.append([self.comp_intvs[-1][0], self.comp_intvs[-1][1]])
            else:
                self.comp_intvs.append([0, self.pckpt_start_time])
                if self.pckpt_fake_failure_alarm == False:
                    self.comp_saved_ckpt_intvs.append([0, self.pckpt_start_time])
                #print(self.name, 'pckpt end', self.comp_intvs[-1])
        self.ckpt_intvs.append([self.pckpt_start_time, self.env.now])
        self.last_ckpt_id += 1
        pfs.store_ckpt(self.name, self.last_ckpt_id, self.ckpt_size)
        self.no_of_ckpts += 1
        self.last_ckpt_pfs = True
        self.sp_queue.clear()
        self.p_queue.clear()
        self.calculate = False
        self.pckpt_fake_failure_alarm = False
        #print(self.name, 'got saved')
        #print('pckpt end')
        #print(self.name, 'made saving with pckpt_0')

    def pckpt_start_pfs(self, start_time):
        #print('start pfs')
        self.pckpt_pfs_in_progress = True
        self.pckpt_pfs_start_time = start_time
        #print('pfscommit start time ', self.pckpt_pfs_start_time)
        self.pckpt_pfs_commit_count = 0


    def pckpt_continue_pfs(self, pfs):
        #print ('why not')
        #print (len(self.p_queue))
        #print (float(self.ckpt_size) / self.clients / pfs.get_real_wrt_thrpt_single(self.ckpt_size/self.clients) / 3600)

        while len(self.p_queue) > 0:
            #yield_time = float(self.ckpt_size) / self.clients / pfs.get_real_wrt_thrpt_single(self.ckpt_size/self.clients) / 3600
            #yield  self.env.timeout (yield_time)
            rank = heapq.heappop(self.p_queue)
            self.sp_queue.append(rank[1])
            #print ('committed ', rank[1])
            self.pckpt_pfs_commit_count += 1
        #print ('done')

    def pckpt_end_pfs(self, end_time):
        self.pckpt_pfs_in_progress = False
        self.pckpt_pfs_end_time = end_time
        self.pckpt_pfs_commit_count = 0
        #print('pfscommit end time ', self.pckpt_pfs_end_time)
        #print('end pfs')

    def run(self, bb, pfs):
        #with self.resource.request(priority=0) as req:
        #    yield req
        #    yield self.env.timeout(self.start_time)
        #print (self.name+' started at: '+str(self.start_time))
        self.status = 'active'
        self.single_pfs_ckpt_period = float(self.ckpt_size) / self.clients / pfs.get_real_wrt_thrpt_single(
            self.ckpt_size / self.clients) / 3600
        self.pfs_ckpt_period = float(self.ckpt_size) / float(
            pfs.get_real_wrt_thrpt(self.clients, self.ckpt_size)) / 3600
        #print (self.pfs_ckpt_period, self.single_pfs_ckpt_period)
        while True:
            try:
                if sum([x[1]-x[0] for x in self.comp_intvs]) >= self.total_comp_time:
                    #print (self.name+', computation finished!')
                    self.status = 'terminated'
                    return
                #print(self.name, 'progress', self.pckpt_in_progress)
                if self.pckpt_in_progress == True:
                    #with self.resource.request(priority=0) as req:
                    #    yield req
                    #another node faced failure prediction
                    if self.failure_alarm == True:
                        self.failure_alarm = False

                    if self.pckpt_pfs_in_progress == True:
                        if len (self.p_queue) > 0:
                            self.pckpt_continue_pfs(pfs)
                            ckpt_time = len (self.p_queue) *  (float(self.ckpt_size) / self.clients / pfs.get_real_wrt_thrpt_single(self.ckpt_size/self.clients) / 3600)
                            yield  self.env.timeout (len (self.p_queue) * ckpt_time)
                        pckpt_time_pfs = float(self.ckpt_size) / float(
                            pfs.get_real_wrt_thrpt(self.clients - self.pckpt_pfs_commit_count, self.ckpt_size)) / 3600
                        #print(self.ckpt_size, self.pckpt_pfs_commit_count, pckpt_time_pfs, self.env.now, self.pckpt_pfs_start_time)
                        if pckpt_time_pfs - (self.env.now - self.pckpt_pfs_start_time) > 0:
                            yield self.env.timeout((pckpt_time_pfs - (self.env.now - self.pckpt_pfs_start_time)))
                        self.pckpt_end_pfs(self.env.now)
                        self.pckpt_end(bb, pfs)
                    else:
                        self.pckpt_start_pfs(self.env.now)
                        self.pckpt_continue_pfs(pfs)
                        ckpt_time = len(self.p_queue) * (
                                    float(self.ckpt_size) / self.clients / pfs.get_real_wrt_thrpt_single(
                                self.ckpt_size / self.clients) / 3600)
                        yield self.env.timeout(len(self.p_queue) * ckpt_time)
                        pckpt_time_pfs = float(self.ckpt_size) / float(
                            pfs.get_real_wrt_thrpt(self.clients - self.pckpt_pfs_commit_count, self.ckpt_size)) / 3600
                        #print(self.ckpt_size, self.pckpt_pfs_commit_count, pckpt_time_pfs, self.env.now,
                        #      self.pckpt_pfs_start_time)
                        yield self.env.timeout((pckpt_time_pfs - (self.env.now - self.pckpt_pfs_start_time)))
                        self.pckpt_end_pfs(self.env.now)
                        self.pckpt_end(bb, pfs)
                #print(self.failure_alarm, self.ckpt_in_progress, self.env.now)

                if (self.failure_alarm == True and self.ckpt_in_progress == False) or (self.failure_alarm == False):
                    if self.failure_alarm == False:
                        self.rand = random.random()
                        self.comp_start_time = self.env.now
                        with self.resource.request(priority=0) as req:
                            yield req
                        comp_period = self.comp_period
                        yield self.env.timeout(comp_period)
                        #print (self.name+', comp started: '+str(self.comp_start_time)+', ended: '+str(self.comp_start_time+comp_period))
                        self.comp_intvs.append([self.comp_start_time, self.comp_start_time+comp_period])
                    else:
                        #print('inside')
                        self.failure_alarm = False

                        # calculate how much time needed to write checkpoint data.
                        self.ckpt_period = float(self.ckpt_size) / float(bb.get_real_wrt_thrpt(self.clients)) / 3600
                        self.pfs_ckpt_period = float(self.ckpt_size) / float(
                            pfs.get_real_wrt_thrpt(self.clients, self.ckpt_size)) / 3600
                        self.single_pfs_ckpt_period = float(
                            self.ckpt_size) / self.clients / pfs.get_real_wrt_thrpt_single(
                            self.ckpt_size / self.clients) / 3600
                        ckpt_time = self.single_pfs_ckpt_period
                        # ckpt_time += (5 / 3600)
                        yield_time = self.time_to_failure - ckpt_time

                        # print (self.name, float(self.ckpt_size) / self.clients / pfs.get_real_wrt_thrpt_single(self.ckpt_size/self.clients) / 3600, self.ckpt_period, self.ckpt_size/self.clients, pfs.get_real_wrt_thrpt_single(self.ckpt_size/self.clients))
                        # print(yield_time, self.time_to_failure, self.ckpt_period)

                        # print(self.name, 'failure prediction during comp', self.time_to_failure, self.ckpt_period, self.pfs_ckpt_period)

                        # print('sleeping after failure alarm:', yield_time)

                        if self.time_to_failure < ckpt_time:
                            if self.fake_failure_alarm == True:
                                tmp = self.comp_period - (self.env.now - self.comp_start_time)
                                if tmp > 0:
                                    yield self.env.timeout(tmp)
                                    self.comp_intvs.append([self.comp_start_time, self.env.now])
                                else:
                                    self.comp_intvs.append([self.comp_start_time, self.env.now])
                                self.fake_failure_alarm = False
                            else:
                                timeout_val = self.time_to_failure
                                yield self.env.timeout(timeout_val)
                        else:

                            comp_period = self.time_to_failure - (ckpt_time)

                            yield self.env.timeout(comp_period)

                            self.calculate = True

                            if self.fake_failure_alarm == True:
                                self.pckpt_fake_failure_alarm = True
                                self.fake_failure_alarm = False
                            self.pckpt_start(self.time_to_failure)
                            # print(self.name, 'pckpt started 1a')
                            self.pckpt_start_pfs(self.env.now)
                            self.pckpt_continue_pfs(pfs)
                            yield self.env.timeout(ckpt_time)
                            # print (self.name, 'pckpt started 1')

                            pckpt_time_pfs = float(self.ckpt_size) / float(
                                pfs.get_real_wrt_thrpt(self.clients - self.pckpt_pfs_commit_count,
                                                       self.ckpt_size)) / 3600

                            if ((pckpt_time_pfs - (self.env.now - self.pckpt_pfs_start_time)) > 0):
                                yield self.env.timeout((pckpt_time_pfs - (self.env.now - self.pckpt_pfs_start_time)))

                            self.pckpt_end_pfs(self.env.now)

                            self.pckpt_end(bb, pfs)
                        continue

                if (self.failure_alarm == True and self.ckpt_in_progress == True) or (self.failure_alarm == False):
                    if self.failure_alarm == False:
                        self.ckpt_start_time = self.env.now
                        #with self.resource.request(priority=0) as req:
                        #    yield req
                        self.ckpt_in_progress = True
                        # only BB ckpt.
                        self.ckpt_period = float(self.ckpt_size) / float(bb.get_real_wrt_thrpt(self.clients)) / 3600
                        self.pfs_ckpt_period = float(self.ckpt_size) / float(
                            pfs.get_real_wrt_thrpt(self.clients, self.ckpt_size)) / 3600
                        self.curnt_ckpt_loc = 'BB'
                        yield self.env.timeout(self.ckpt_period)
                        self.last_ckpt_id += 1
                        bb.store_ckpt(self.name, self.last_ckpt_id, self.ckpt_size, self.clients)
                        # print (self.name+', ckpt started: '+str(self.ckpt_start_time)+', ended: '+str(self.ckpt_start_time+self.ckpt_period))
                        self.ckpt_intvs.append([self.ckpt_start_time, self.ckpt_start_time + self.ckpt_period])
                        self.no_of_ckpts += 1
                        self.ckpt_in_progress = False
                        self.last_ckpt_pfs = False
                    else:
                        self.failure_alarm = False

                        #with self.resource.request(priority=0) as req:
                        #    yield req
                        self.single_pfs_ckpt_period = float(
                            self.ckpt_size) / self.clients / pfs.get_real_wrt_thrpt_single(
                            self.ckpt_size / self.clients) / 3600
                        ckpt_time = self.single_pfs_ckpt_period
                        #ckpt_time += (5 / 3600)
                        #self.time_to_failure = self.sys_fail.latest_leadtime

                        if self.time_to_failure < ckpt_time:
                            if self.fake_failure_alarm == True:
                                yield self.env.timeout(self.ckpt_period - (self.env.now - self.ckpt_start_time))
                                self.last_ckpt_id += 1
                                bb.store_ckpt(self.name, self.last_ckpt_id, self.ckpt_size, self.clients)
                                self.ckpt_intvs.append([self.ckpt_start_time, self.ckpt_start_time + self.ckpt_period])
                                self.no_of_ckpts += 1
                                self.fake_failure_alarm = False
                            else:
                                yield self.env.timeout(self.time_to_failure)

                            self.ckpt_in_progress = False
                        else:

                            self.comp_start_time = self.env.now
                            comp_period = self.time_to_failure - (ckpt_time)
                            self.ckpt_in_progress = False
                            yield self.env.timeout(comp_period)
                            self.comp_intvs.append([self.comp_start_time, self.comp_start_time + comp_period])
                            #self.comp_saved_ckpt_intvs.append(
                            #    [self.comp_start_time, self.comp_start_time + comp_period])

                            self.calculate = True


                            if self.fake_failure_alarm == True:
                                self.pckpt_fake_failure_alarm = True
                                self.fake_failure_alarm = False
                            self.pckpt_start(self.time_to_failure)
                            #print(self.name, 'pckpt started 2a')
                            self.pckpt_start_pfs(self.env.now)
                            self.pckpt_continue_pfs(pfs)
                            yield self.env.timeout(ckpt_time)
                            #print(self.name, 'pckpt started 2')
                            # print(self.env.now)
                            pckpt_time_pfs = float(self.ckpt_size) / float(
                                pfs.get_real_wrt_thrpt(self.clients - self.pckpt_pfs_commit_count,
                                                       self.ckpt_size)) / 3600

                            # print ('hello4', self.env.now, (pckpt_time_pfs - (self.env.now - self.pckpt_pfs_start_time)))
                            if ((pckpt_time_pfs - (self.env.now - self.pckpt_pfs_start_time)) > 0):
                                yield self.env.timeout((pckpt_time_pfs - (self.env.now - self.pckpt_pfs_start_time)))

                            # print('hello5', self.env.now)
                            self.pckpt_end_pfs(self.env.now)

                            self.pckpt_end(bb, pfs)
                #self.set_ckpt_loc('BB')
            except simpy.Interrupt as interrupt:
                if 'alarm' in interrupt.cause and 'fakealarm' not in interrupt.cause:
                    self.failed_client_id = int(interrupt.cause.split(":")[1])
                    self.time_to_failure = float(interrupt.cause.split(":")[2])
                    #print(interrupt.cause, self.env.now)
                    if self.pckpt_in_progress == True:
                        if self.pckpt_fake_failure_alarm == True:
                            self.pckpt_fake_failure_alarm = False
                        heapq.heappush(self.p_queue, (self.time_to_failure, self.failed_client_id))
                        #print ('added node ' + str(self.failed_client_id) + ' with time to failure' + str(self.time_to_failure))
                    self.failure_alarm = True
                    #print(self.name, 'alarm ' + self.name + ' interrupted at ' + str(
                    #    self.env.now) + ': ' + interrupt.cause, self.single_pfs_ckpt_period <= self.time_to_failure)
                    continue
                elif 'fakealarm' in interrupt.cause:
                    self.failure_alarm = True
                    self.fake_failure_alarm = True
                    if self.pckpt_in_progress == True:
                        heapq.heappush(self.p_queue, (self.time_to_failure, self.sys_fail.fail_client_id))
                    continue
                elif 'failure' in interrupt.cause:
                    #print(self.env.now, ' ', interrupt.cause)
                    self.ckpt_in_progress = False
                    self.interruptions += 1
                    self.failed_client_id = int(interrupt.cause.split(":")[1])
                    #print (self.name, 'failure', interrupt.cause)
                    if self.pckpt_in_progress == True:
                        if self.failed_client_id in self.p_queue and self.failed_client_id not in self.sp_queue:
                            #wastage should be calculated in pckpt_reset() function
                            #print ('unexpected failure')
                            #print('actual failure ' + self.name + ' interrupted at ' + str(
                            #    self.env.now) + ': ' + interrupt.cause)
                            self.failured_handled = False
                            self.pckpt_reset(pfs)
                        elif self.failed_client_id in self.sp_queue:
                            #print('handled failure 1' + self.name + ' interrupted at ' + str(
                            #    self.env.now) + ': ' + interrupt.cause)
                            pckpt_time_pfs = float(self.ckpt_size) / float(
                                pfs.get_real_wrt_thrpt(self.clients - self.pckpt_pfs_commit_count,
                                                       self.ckpt_size)) / 3600
                            self.ckpt_intvs.append([self.pckpt_start_time, self.env.now])
                            self.last_ckpt_id += 1
                            pfs.store_ckpt(self.name, self.last_ckpt_id, self.ckpt_size)
                            self.no_of_ckpts += 1
                            self.last_ckpt_pfs = True
                            self.failured_handled = True
                            self.pckpt_reset(pfs)
                            if pckpt_time_pfs - (self.env.now - self.pckpt_pfs_start_time) > 0:
                                try:
                                    yield self.env.timeout((pckpt_time_pfs - (self.env.now - self.pckpt_pfs_start_time)))
                                except simpy.Interrupt as interrupt:

                                    self.failed_client_id = int(interrupt.cause.split(":")[1])
                                    self.time_to_failure = float(interrupt.cause.split(":")[2])
                                    heapq.heappush(self.p_queue, (self.time_to_failure, self.failed_client_id))
                                    # print ('added node ' + str(self.failed_client_id) + ' with time to failure' + str(self.time_to_failure))
                                    self.failure_alarm = True
                                    #print(self.name, 'alarm1 ' + self.name + ' interrupted at ' + str(
                                    #      self.env.now) + ': ' + interrupt.cause,
                                    #      self.single_pfs_ckpt_period >= self.time_to_failure)
                                    self.pckpt_start(self.time_to_failure)

                        elif self.failed_client_id not in self.p_queue and self.failed_client_id not in self.sp_queue:
                            #print ('previously handled failure')
                            pckpt_time_pfs = float(self.ckpt_size) / float(
                                pfs.get_real_wrt_thrpt(self.clients - self.pckpt_pfs_commit_count,
                                                       self.ckpt_size)) / 3600
                            self.ckpt_intvs.append([self.pckpt_start_time, self.env.now])
                            self.last_ckpt_id += 1
                            pfs.store_ckpt(self.name, self.last_ckpt_id, self.ckpt_size)
                            self.no_of_ckpts += 1
                            self.last_ckpt_pfs = True
                            self.failured_handled = True
                            self.pckpt_reset(pfs)
                            if pckpt_time_pfs - (self.env.now - self.pckpt_pfs_start_time) > 0:
                                try:
                                    yield self.env.timeout((pckpt_time_pfs - (self.env.now - self.pckpt_pfs_start_time)))
                                except simpy.Interrupt as interrupt:
                                    self.failed_client_id = int(interrupt.cause.split(":")[1])
                                    self.time_to_failure = float(interrupt.cause.split(":")[2])
                                    heapq.heappush(self.p_queue, (self.time_to_failure, self.failed_client_id))
                                        # print ('added node ' + str(self.failed_client_id) + ' with time to failure' + str(self.time_to_failure))
                                    self.failure_alarm = True
                                    #print(self.name, 'alarm2 ' + self.name + ' interrupted at ' + str(
                                    #    self.env.now) + ': ' + interrupt.cause,
                                    #      self.single_pfs_ckpt_period >= self.time_to_failure)
                                    self.pckpt_start(self.time_to_failure)
                    else:
                        self.failured_handled = False
                        #print(self.name, False)
                        #print (self.name, 'not handled', self.env.now)
                    #print(self.id, 'failure happened')
                restart_time = self.env.now
                #print ('execution of '+self.name+' interrupted at '+str(restart_time)+': '+ interrupt.cause)
                if self.failured_handled == False:
                    #print ('waste calculation')
                    if self.ckpt_intvs:
                        if self.ckpt_intvs[-1][1] < self.comp_intvs[-1][1]:
                            self.waste_intvs.append([self.comp_intvs[-1][0], restart_time])
                            self.comp_intvs.pop()
                        elif self.ckpt_intvs[-1][1] + self.pfs_ckpt_period > self.env.now and self.last_ckpt_pfs == False:
                            # that means failure happened during dumping to the PFS.
                            #this is the previous computation waste deemed complete.
                            self.waste_intvs.append([self.comp_intvs[-1][0], self.comp_intvs[-1][1]])
                            self.comp_intvs.pop()
                            #this is the last checkpoint and current computation time waste.
                            self.waste_intvs.append([self.ckpt_intvs[-1][0], restart_time])
                            self.ckpt_intvs.pop()
                            #remove the last checkpoint from BB data.
                            bb.delete_ckpt(self.name, self.last_ckpt_id, self.ckpt_size)
                            self.last_ckpt_id -= 1
                            self.no_of_ckpts -= 1
                        else:
                            #this is during computation but not during pfs write.
                            self.waste_intvs.append([self.ckpt_intvs[-1][1], restart_time])
                    else:
                        if self.comp_intvs:
                            self.waste_intvs.append([self.comp_intvs[-1][0], restart_time])
                            self.comp_intvs.pop()
                        else:
                            self.waste_intvs.append([0, restart_time])
                    self.pckpt_in_progress = False

                #print 'last comp intv: '+str(self.comp_intvs[-1])
                #print 'last ckpt intv: '+str(self.ckpt_intvs[-1])              
                #print 'last waste intv: '+str(self.waste_intvs[-1])
                while self.interruptions > 0:
                    self.interruptions -= 1
                    # for only BB, with and without limits.
                    if bb.search_ckpt(self.name, self.last_ckpt_id) or self.last_ckpt_pfs == False:
                        restart_period_bb = float(self.ckpt_size)/float(bb.get_real_rd_thrpt(self.clients))/3600
                        restart_period = restart_period_bb
                    elif pfs.search_ckpt(self.name, self.last_ckpt_id):
                        restart_period_pfs = float(self.ckpt_size)/float(pfs.get_real_rd_thrpt(self.clients, self.ckpt_size)) / 3600
                        #print(self.name, restart_period_pfs)
                        restart_period = restart_period_pfs
                    else:
                        #ckpt doesn't exist continue to computation.
                        continue
                    try:
                        #print (self.name+', recover started: '+str(restart_time))
                        yield self.env.timeout(restart_period)
                        self.restart_intvs.append([restart_time, restart_time+restart_period])
                        #print (self.name+', recover ended: '+str(restart_time+restart_period))
                    except simpy.Interrupt as i:
                        recover_intrpt = self.env.now
                        #print ('recover of '+self.name+' interrupted at '+str(recover_intrpt)+': '+ i.cause)
                        self.interruptions += 1
                        self.waste_intvs.append([restart_time, recover_intrpt])
                        #print ('recover during ['+str(restart_time)+', '+str(recover_intrpt)+'] is wasted')
                '''
                while self.interruptions > 0:
                    self.interruptions -= 1
                    #for both BB and PFS.

                    #for only BB, with and without limits.
                    if bb.search_ckpt(self.name, self.last_ckpt_id):
                        restart_period_bb = float(self.ckpt_size)/float(bb.get_real_rd_thrpt(self.clients))/3600
                        restart_period = restart_period_bb
                    elif pfs.search_ckpt(self.name, self.last_ckpt_id):
                        restart_period_pfs = float(self.ckpt_size)/float(pfs.get_real_rd_thrpt(self.clients, self.ckpt_size)) / 3600
                        #print(self.name, restart_period_pfs)
                        restart_period = restart_period_pfs
                    else:
                        #ckpt doesn't exist continue to computation.
                        continue
                    try:
                        #print (self.name+', recover started: '+str(restart_time))
                        #with self.resource.request(priority=0) as req:
                        #    yield req
                        yield self.env.timeout(restart_period)
                        self.restart_intvs.append([restart_time, restart_time+restart_period])
                        self.failured_handled = False
                        #print (self.name+', recover ended: '+str(restart_time+restart_period))
                    except simpy.Interrupt as i:
                        recover_intrpt = self.env.now
                        #print (self.name, 'recovery')

                        if 'alarm' in i.cause:
                            self.failed_client_id = int(i.cause.split(":")[1])
                            self.time_to_failure = float(i.cause.split(":")[2])
                            heapq.heappush(self.p_queue, (self.time_to_failure, self.failed_client_id))
                            #print ('added node ' + str(self.failed_client_id) + ' with time to failure' + str(self.time_to_failure))
                            self.failure_alarm = True
                            #print(self.name, 'alarm3 ' + self.name + ' interrupted at ' + str(
                              #self.env.now) + ': ' + i.cause,
                              #self.single_pfs_ckpt_period >= self.time_to_failure)
                            self.pckpt_start(self.time_to_failure)
                            break
                        #print ('recover of '+self.name+' interrupted at '+str(recover_intrpt)+': '+ i.cause)
                        self.interruptions += 1
                        self.waste_intvs.append([restart_time, recover_intrpt])
                        #print ('recover during ['+str(restart_time)+', '+str(recover_intrpt)+'] is wasted')
                '''

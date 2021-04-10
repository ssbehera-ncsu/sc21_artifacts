import simpy
import random
from random import randint
from collections import deque
import heapq

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
        self.comp_saved_lm_intvs = []
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
        self.pckpt_pfs_start_time = -1
        self.pckpt_end_time = -1
        self.pckpt_pfs_end_time = -1
        self.last_ckpt_pfs = False
        self.time_to_failure = -1
        self.failed_client_id = -1
        self.pckpt_pfs_commit_count = 0
        self.pckpt_pfs_in_progress = False
        self.interval_to_be_saved = []
        self.comp_intvs_to_be_added = []
        self.interval_to_saved = []
        self.failured_handled = False
        if self.ckpt_size / self.clients * 3 > 512:
            self.live_migration_threshold = 512 / 12.5 / 3600
        else:
            self.live_migration_threshold = self.ckpt_size * 3 / self.clients / 12.5 / 3600

        self.live_migration_percentage = 0
        self.calculate = False

    def set_sys_fail (self, sys_fail):
        self.sys_fail = sys_fail
        self.live_migration_percentage = self.sys_fail.lm_pct (self.live_migration_threshold)
        #print (self.name, self.live_migration_percentage, self.live_migration_threshold, self.ckpt_size/self.clients)

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
                        self.comp_saved_ckpt_intvs.append([self.comp_intvs[-1][0], self.comp_intvs[-1][1]])
                    else:
                        if self.comp_intvs and self.ckpt_intvs[-1][1] + self.pfs_ckpt_period > self.pckpt_start_time:
                            comp_period = self.pckpt_start_time - self.comp_start_time
                            self.comp_saved_ckpt_intvs.append([self.comp_intvs[-1][0], self.comp_intvs[-1][1]])
                            self.comp_saved_ckpt_intvs.append(
                                [self.comp_start_time, self.comp_start_time + comp_period])
                            self.comp_intvs.append([self.comp_start_time, self.comp_start_time + comp_period])
                            #print(self.name, 'pckpt reset', self.comp_intvs[-1])
                        else:
                            comp_period = self.pckpt_start_time - self.comp_start_time
                            self.comp_intvs.append([self.comp_start_time, self.comp_start_time + comp_period])
                            self.comp_saved_ckpt_intvs.append(
                                [self.comp_start_time, self.comp_start_time + comp_period])
                            #print(self.name, 'pckpt reset', self.comp_intvs[-1])
                else:
                    if self.comp_intvs:
                        self.comp_saved_ckpt_intvs.append([self.comp_intvs[-1][0], self.comp_intvs[-1][1]])
                    else:
                        self.comp_intvs.append([0, self.pckpt_start_time])
                        #print(self.name, 'pckpt reset', self.comp_intvs[-1])
                        self.comp_saved_ckpt_intvs.append([0, self.pckpt_start_time])

        self.calculate = False
        self.pckpt_start_time = -1
        self.pckpt_pfs_start_time = -1
        self.pckpt_end_time = -1
        self.pckpt_pfs_end_time = -1
        self.pckpt_in_progress = False
        self.pckpt_pfs_in_progress = False
        self.p_queue.clear()
        self.sp_queue.clear()

    def pckpt_start(self, time_to_failure):
        self.pckpt_start_time = -1
        self.pckpt_pfs_start_time = -1
        self.pckpt_end_time = -1
        self.pckpt_pfs_end_time = -1
        self.pckpt_in_progress = True
        self.pckpt_start_time = self.env.now
        self.p_queue.clear()
        self.sp_queue.clear()
        heapq.heappush(self.p_queue, (time_to_failure, self.failed_client_id))

    def pckpt_end(self, bb, pfs):
        self.pckpt_in_progress = False
        self.pckpt_end_time = self.env.now
        if self.ckpt_intvs:
            if self.ckpt_intvs[-1][1] < self.comp_intvs[-1][1]:
                self.comp_saved_ckpt_intvs.append([self.comp_intvs[-1][0], self.comp_intvs[-1][1]])
            else:
                if self.ckpt_intvs[-1][1] + self.pfs_ckpt_period > self.pckpt_start_time:
                    comp_period = self.pckpt_start_time - self.comp_start_time
                    self.comp_saved_ckpt_intvs.append([self.comp_intvs[-1][0], self.comp_intvs[-1][1]])
                    self.comp_saved_ckpt_intvs.append(
                        [self.comp_start_time, self.comp_start_time + comp_period])
                    self.comp_intvs.append([self.comp_start_time, self.comp_start_time + comp_period])
                else:
                    comp_period = self.pckpt_start_time - self.comp_start_time
                    self.comp_intvs.append([self.comp_start_time, self.comp_start_time + comp_period])
                    self.comp_saved_ckpt_intvs.append(
                        [self.comp_start_time, self.comp_start_time + comp_period])
        else:
            if self.comp_intvs:
                self.comp_saved_ckpt_intvs.append([self.comp_intvs[-1][0], self.comp_intvs[-1][1]])
            else:
                self.comp_intvs.append([0, self.pckpt_start_time])
                self.comp_saved_ckpt_intvs.append([0, self.pckpt_start_time])
        self.ckpt_intvs.append([self.pckpt_start_time, self.env.now])
        self.last_ckpt_id += 1
        pfs.store_ckpt(self.name, self.last_ckpt_id, self.ckpt_size)
        self.no_of_ckpts += 1
        self.last_ckpt_pfs = True
        self.sp_queue.clear()
        self.p_queue.clear()
        #print(self.name, 'made saving with pckpt')

    def pckpt_start_pfs(self, start_time):

        self.pckpt_pfs_in_progress = True
        self.pckpt_pfs_start_time = start_time
        self.pckpt_pfs_commit_count = 0


    def pckpt_continue_pfs(self, pfs):
        #with self.resource.request(priority=0) as req:
        #    yield req
        while self.p_queue:
            rank = heapq.heappop(self.p_queue)
            self.sp_queue.append(rank[1])
            self.pckpt_pfs_commit_count += 1

    def pckpt_end_pfs(self, end_time):
        self.pckpt_pfs_in_progress = False
        self.pckpt_pfs_end_time = end_time
        self.pckpt_pfs_commit_count = 0

    #def pop_ckpt_loc(self):
    #    return self.ckpt_loc.pop(0)    

    def run(self, bb, pfs):
        #with self.resource.request(priority=0) as req:
        #    yield req
        #    yield self.env.timeout(self.start_time)
        #print (self.name+' started at: '+str(self.start_time))
        self.ckpt_period = float(self.ckpt_size) / float(bb.get_real_wrt_thrpt(self.clients)) / 3600
        self.pfs_ckpt_period = float(self.ckpt_size) / float(
            pfs.get_real_wrt_thrpt(self.clients, self.ckpt_size)) / 3600
        self.status = 'active'
        while True:
            try:
                if sum([x[1]-x[0] for x in self.comp_intvs]) >= self.total_comp_time:
                    #print (self.name+', computation finished!')
                    self.status = 'terminated'
                    return

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
                '''
                if self.pckpt_in_progress == True:

                    if self.failure_alarm == True:
                        self.failure_alarm = False
                    if self.pckpt_pfs_in_progress == True:
                        self.pckpt_continue_pfs(pfs)
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
                        pckpt_time_pfs = float(self.ckpt_size) / float(
                            pfs.get_real_wrt_thrpt(self.clients - self.pckpt_pfs_commit_count, self.ckpt_size)) / 3600
                        #print(self.ckpt_size, self.pckpt_pfs_commit_count, pckpt_time_pfs, self.env.now,
                        #      self.pckpt_pfs_start_time)
                        yield self.env.timeout((pckpt_time_pfs - (self.env.now - self.pckpt_pfs_start_time)))
                        self.pckpt_end_pfs(self.env.now)
                        self.pckpt_end(bb, pfs)
                '''
                #print(self.failure_alarm, self.ckpt_in_progress)
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
                        self.failure_alarm = False

                        #with self.resource.request(priority=0) as req:
                        #    yield req

                        #print(self.env.now, self.name, 'FAILURE ALARM', time_to_failure)
                        #if we have enough time to perform live migration.
                        if self.time_to_failure >= self.live_migration_threshold:
                            #find next checkpoint start time.
                            next_ckpt_time = self.comp_start_time + self.comp_period
                            #find failure time
                            failure_time = self.time_to_failure + self.env.now
                            #if next checkpoint is after failure then wait till next checkpoint.
                            if next_ckpt_time > failure_time:
                                if bb.search_ckpt(self.name, self.last_ckpt_id):
                                    restart_period_bb = float(self.ckpt_size) / float(bb.get_real_rd_thrpt(self.clients)) / 3600
                                    restart_period_pfs = float(self.ckpt_size) / float(pfs.get_real_rd_thrpt(1, self.ckpt_size)) / 3600
                                    if restart_period_bb > restart_period_pfs:
                                        restart_period = restart_period_bb
                                    else:
                                        restart_period = restart_period_pfs
                                    if self.ckpt_intvs[-1][1] + self.pfs_ckpt_period > failure_time:
                                        #what if failure happens during write to PFS.
                                        #add waste for current computation and checkpoint to BB.
                                        time_to_wait = self.live_migration_threshold
                                        #self.waste_intvs.append([self.ckpt_intvs[-1][0], self.ckpt_intvs[-1][1]])
                                        self.interval_to_be_saved.append([self.comp_intvs[-1][0], failure_time + restart_period])
                                        #self.comp_saved_lm_intvs.append([self.comp_intvs[-1][0], self.comp_intvs[-1][1]])
                                        #self.comp_saved_lm_intvs.append([self.ckpt_intvs[-1][1], failure_time + restart_period])
                                        self.ckpt_intvs.pop()
                                        self.last_ckpt_id -= 1
                                        self.no_of_ckpts -= 1
                                    else:
                                        time_to_wait = self.live_migration_threshold
                                        if time_to_wait < (next_ckpt_time - self.env.now):
                                            time_to_wait = next_ckpt_time - self.env.now
                                        self.interval_to_be_saved.append([self.comp_start_time, failure_time + restart_period])
                                        #self.comp_saved_lm_intvs.append([self.comp_start_time, failure_time + restart_period])
                                else:
                                    #in case there is no checkpoint done yet.
                                    self.interval_to_be_saved.append([self.comp_start_time, failure_time])
                                    #self.comp_saved_lm_intvs.append([self.comp_start_time, failure_time])
                                    time_to_wait = self.sys_fail.live_migration_threshold
                                    if time_to_wait < (next_ckpt_time - self.env.now):
                                        time_to_wait = next_ckpt_time - self.env.now
                                #if self.comp_saved_lm_intvs[-1][1] <= self.comp_saved_lm_intvs[-1][0]:
                                #    exit(-1)
                            else:
                            # if next checkpoint is before failure then move the next checkpoint to just after failure.
                                restart_period_bb = float(self.ckpt_size) / float(bb.get_real_rd_thrpt(self.clients)) / 3600
                                restart_period_pfs = float(self.ckpt_size) / float(pfs.get_real_rd_thrpt(1, self.ckpt_size)) / 3600
                                if restart_period_bb > restart_period_pfs:
                                    restart_period = restart_period_bb
                                else:
                                    restart_period = restart_period_pfs
                                ckpt_time_bb = float(self.ckpt_size) / float(bb.get_real_wrt_thrpt(self.clients)) / 3600
                                ckpt_time_pfs = float(self.ckpt_size) / float(pfs.get_real_wrt_thrpt(self.clients, self.ckpt_size)) / 3600
                                ckpt_time = ckpt_time_bb + ckpt_time_pfs
                                if ckpt_time + next_ckpt_time > failure_time:
                                    self.interval_to_be_saved.append([self.comp_start_time, failure_time + restart_period])
                                    #self.comp_saved_lm_intvs.append([self.comp_start_time, failure_time + restart_period])
                                else:
                                    #self.comp_saved_lm_intvs.append([next_ckpt_time + ckpt_time_bb, failure_time + restart_period])
                                    self.interval_to_be_saved.append([next_ckpt_time + ckpt_time_bb, failure_time + restart_period])
                                #if self.comp_saved_lm_intvs[-1][1] <= self.comp_saved_lm_intvs[-1][0]:
                                #    exit(-1)
                                time_to_wait = self.sys_fail.live_migration_threshold

                            #print('next ckpt time:', next_ckpt_time)
                            #print('failure time:', failure_time)
                            #print('yield time:', time_to_wait)
                            self.live_migration_in_progress = True
                            comp_period = self.env.now - self.comp_start_time
                            self.comp_intvs_to_be_added.append([self.comp_start_time, self.comp_start_time + comp_period])

                            yield self.env.timeout(time_to_wait)

                            for interval in self.interval_to_saved:
                                self.comp_saved_lm_intvs.append(interval)
                            for interval in self.comp_intvs_to_be_added:
                                self.comp_intvs.append(interval)

                            self.live_migration_in_progress = False
                            #print(self.name + ', comp started: ' + str(self.comp_start_time) + ', ended: ' + str(
                            #    self.comp_start_time + comp_period))
                            #print('saved computation waste due to live migration')
                        else:
                            #calculate how much time needed to write checkpoint data.
                            self.single_pfs_ckpt_period = float(
                                self.ckpt_size) / self.clients / pfs.get_real_wrt_thrpt_single(
                                self.ckpt_size / self.clients) / 3600
                            ckpt_time = self.single_pfs_ckpt_period
                            yield_time = self.time_to_failure - ckpt_time

                            #print('time to failure:', self.sys_fail.latest_failure.meanleadtime / 3600)
                            #print('ckpt time:', ckpt_time)
                            #print('sleeping after failure alarm:', yield_time)

                            #print(self.name, 'failure prediction during comp', time_to_failure, self.ckpt_period,
                            #      self.pfs_ckpt_period)

                            if yield_time < 0:
                                if self.time_to_failure < self.ckpt_period:
                                    # with self.resource.request(priority=0) as req:
                                    #    yield req
                                    yield self.env.timeout(self.time_to_failure)
                                else:
                                    self.calculate = True
                                    self.pckpt_start(self.time_to_failure)

                                    self.pckpt_start_pfs(self.env.now)

                                    self.pckpt_continue_pfs(pfs)

                                    pckpt_time_pfs = float(self.ckpt_size) / float(
                                        pfs.get_real_wrt_thrpt(self.clients - self.pckpt_pfs_commit_count,
                                                               self.ckpt_size)) / 3600

                                    yield self.env.timeout(
                                        (pckpt_time_pfs - (self.env.now - self.pckpt_pfs_start_time)))

                                    self.pckpt_end_pfs(self.env.now)

                                    self.pckpt_end(bb, pfs)
                            else:
                                yield self.env.timeout(yield_time)
                                # comp_period = self.env.now - self.comp_start_time
                                # self.comp_intvs.append([self.comp_start_time, self.comp_start_time + comp_period])
                                # self.comp_saved_ckpt_intvs.append(
                                # [self.comp_start_time, self.comp_start_time + comp_period])

                                # with self.resource.request(priority=0) as req:
                                #    yield req
                                self.calculate = True
                                self.pckpt_start(self.time_to_failure)

                                self.pckpt_start_pfs(self.env.now)

                                self.pckpt_continue_pfs(pfs)

                                pckpt_time_pfs = float(self.ckpt_size) / float(
                                    pfs.get_real_wrt_thrpt(self.clients - self.pckpt_pfs_commit_count,
                                                           self.ckpt_size)) / 3600

                                yield self.env.timeout((pckpt_time_pfs - (self.env.now - self.pckpt_pfs_start_time)))

                                self.pckpt_end_pfs(self.env.now)

                                self.pckpt_end(bb, pfs)
                            continue
                if (self.failure_alarm == True and self.ckpt_in_progress == True) or (self.failure_alarm == False):
                    if self.failure_alarm == False:
                        self.ckpt_start_time = self.env.now

                        self.ckpt_in_progress = True
                        #only BB ckpt.
                        self.ckpt_period = float(self.ckpt_size) / float(bb.get_real_wrt_thrpt(self.clients)) / 3600
                        self.pfs_ckpt_period = float(self.ckpt_size) / float(pfs.get_real_wrt_thrpt(self.clients, self.ckpt_size)) / 3600
                        self.curnt_ckpt_loc = 'BB'
                        yield self.env.timeout(self.ckpt_period)
                        self.last_ckpt_id += 1
                        bb.store_ckpt(self.name, self.last_ckpt_id, self.ckpt_size, self.clients)
                        #print (self.name+', ckpt started: '+str(self.ckpt_start_time)+', ended: '+str(self.ckpt_start_time+self.ckpt_period))
                        self.ckpt_intvs.append([self.ckpt_start_time, self.ckpt_start_time+self.ckpt_period])
                        self.no_of_ckpts += 1
                        self.ckpt_in_progress = False
                        self.last_ckpt_pfs = False
                    else:
                        self.failure_alarm = False

                        # if we have enough time to perform live migration.
                        if self.time_to_failure >= self.live_migration_threshold:
                            #ckpt wasted
                            #self.waste_intvs.append([self.ckpt_start_time, self.env.now])
                            #computation done during live migration.
                            # Doubt
                            self.comp_intvs_to_be_added.append([self.env.now, self.env.now + self.live_migration_threshold])
                            #self.comp_intvs.append([self.env.now, self.env.now + self.sys_fail.live_migration_threshold])
                            if self.env.now + self.time_to_failure <= self.comp_intvs[-1][1] + self.ckpt_period + self.pfs_ckpt_period:
                                if bb.search_ckpt(self.name, self.last_ckpt_id):
                                    restart_period_bb = float(self.ckpt_size) / float(
                                        bb.get_real_rd_thrpt(self.clients)) / 3600
                                    restart_period_pfs = float(self.ckpt_size) / float(
                                        pfs.get_real_rd_thrpt(1, self.ckpt_size)) / 3600
                                    if restart_period_bb > restart_period_pfs:
                                        restart_period = restart_period_bb
                                    else:
                                        restart_period = restart_period_pfs
                                    self.interval_to_be_saved.append([self.comp_intvs[-1][0], self.env.now + self.time_to_failure + restart_period])
                                    #self.comp_saved_lm_intvs.append([self.comp_intvs[-1][0], self.env.now + time_to_failure + restart_period])
                                else:
                                    self.interval_to_be_saved.append([self.comp_intvs[-1][0], self.env.now + self.time_to_failure])
                                    #self.comp_saved_lm_intvs.append([self.comp_intvs[-1][0], self.env.now + time_to_failure])
                            else:
                                self.interval_to_be_saved.append([self.comp_intvs[-1][1] + self.ckpt_period, self.env.now + self.time_to_failure])
                                #self.comp_saved_lm_intvs.append([self.comp_intvs[-1][1] + self.ckpt_period, self.env.now + time_to_failure])
                            #if self.comp_saved_lm_intvs[-1][1] <= self.comp_saved_lm_intvs[-1][0]:
                            #    exit(-1)
                            #first perform live migration.
                            yield  self.env.timeout(self.sys_fail.live_migration_threshold)

                            for interval in self.interval_to_saved:
                                self.comp_saved_lm_intvs.append(interval)
                            for interval in self.comp_intvs_to_be_added:
                                self.comp_intvs.append(interval)

                            self.live_migration_in_progress = False

                            #now do the checkpoint again.
                            self.ckpt_start_time = self.env.now
                            self.ckpt_in_progress = True
                            # only BB ckpt.
                            self.ckpt_period = float(self.ckpt_size) / float(bb.get_real_wrt_thrpt(self.clients)) / 3600
                            self.pfs_ckpt_period = float(self.ckpt_size) / float(pfs.get_real_wrt_thrpt(self.clients, self.ckpt_size)) / 3600
                            self.curnt_ckpt_loc = 'BB'

                            yield self.env.timeout(self.ckpt_period)
                            #print(self.name + ', ckpt started after live migration: ' + str(self.ckpt_start_time) + ', ended: ' + str(
                            #    self.ckpt_start_time + self.ckpt_period))
                            self.last_ckpt_id += 1
                            bb.store_ckpt(self.name, self.last_ckpt_id, self.ckpt_size, self.clients)
                            self.ckpt_intvs.append([self.ckpt_start_time, self.ckpt_start_time + self.ckpt_period])
                            self.no_of_ckpts += 1
                            self.ckpt_in_progress = False
                        else:
                            #print('failure alarm during checkpoint')

                            self.failure_alarm = False
                            self.single_pfs_ckpt_period = float(
                                self.ckpt_size) / self.clients / pfs.get_real_wrt_thrpt_single(
                                self.ckpt_size / self.clients) / 3600
                            yield_time = self.single_pfs_ckpt_period

                            #print(self.name, 'failure prediction during ckpt', time_to_failure, self.ckpt_period,
                            #      self.pfs_ckpt_period)

                            # print('ckpt period:', self.ckpt_period)
                            # print('ckpt start time:', self.ckpt_start_time)
                            # print('now:', self.env.now)
                            # print('time to failure:', time_to_failure)
                            if yield_time > self.time_to_failure:
                                #   print('low failure prediction time nothing can be done, except accept fate')
                                yield self.env.timeout(self.time_to_failure)
                                self.ckpt_in_progress = False
                            else:
                                # ABORT THE CURRENT CHECKPOINT, PERFORM COMPUTATION, PERFORM P-CKPT
                                self.single_pfs_ckpt_period = float(
                                    self.ckpt_size) / self.clients / pfs.get_real_wrt_thrpt_single(
                                    self.ckpt_size / self.clients) / 3600
                                yield_time = self.single_pfs_ckpt_period

                                if yield_time < self.time_to_failure:
                                    self.waste_intvs.append([self.ckpt_start_time, self.env.now])

                                    # self.comp_start_time = self.env.now
                                    comp_period = self.time_to_failure - (yield_time)
                                    self.ckpt_in_progress = False
                                    yield self.env.timeout(comp_period)
                                    # self.comp_intvs.append([self.comp_start_time, self.comp_start_time + comp_period])
                                    # self.comp_saved_ckpt_intvs.append(
                                    # [self.comp_start_time, self.comp_start_time + comp_period])

                                    # with self.resource.request(priority=0) as req:
                                    #    yield req
                                    self.calculate = True
                                    self.pckpt_start(self.time_to_failure)

                                    self.pckpt_start_pfs(self.env.now)

                                    self.pckpt_continue_pfs(pfs)

                                    pckpt_time_pfs = float(self.ckpt_size) / float(
                                        pfs.get_real_wrt_thrpt(self.clients - self.pckpt_pfs_commit_count,
                                                               self.ckpt_size)) / 3600
                                    yield self.env.timeout(
                                        (pckpt_time_pfs - (self.env.now - self.pckpt_pfs_start_time)))

                                    self.pckpt_end_pfs(self.env.now)

                                    self.pckpt_end(bb, pfs)

                                else:
                                    self.calculate = True
                                    self.ckpt_in_progress = False
                                    # start p-ckpt immidiately
                                    self.pckpt_start(self.time_to_failure)

                                    self.pckpt_start_pfs(self.env.now)

                                    self.pckpt_continue_pfs(pfs)

                                    pckpt_time_pfs = float(self.ckpt_size) / float(
                                        pfs.get_real_wrt_thrpt(self.clients - self.pckpt_pfs_commit_count,
                                                               self.ckpt_size)) / 3600
                                    yield self.env.timeout(
                                        (pckpt_time_pfs - (self.env.now - self.pckpt_pfs_start_time)))

                                    self.pckpt_end_pfs(self.env.now)

                                    self.pckpt_end(bb, pfs)

                #self.set_ckpt_loc('BB')
            except simpy.Interrupt as interrupt:
                if 'alarm' in interrupt.cause:
                    self.failed_client_id = int(interrupt.cause.split(":")[1])
                    self.time_to_failure = float(interrupt.cause.split(":")[2])
                    #print(interrupt.cause, self.env.now)
                    if self.pckpt_in_progress == True:
                        heapq.heappush(self.p_queue, (self.time_to_failure, self.failed_client_id))
                        #print ('added node ' + str(self.failed_client_id) + ' with time to failure' + str(self.time_to_failure))
                    self.failure_alarm = True
                    continue
                elif 'failure' in interrupt.cause:
                    # print(self.env.now, ' ', interrupt.cause)
                    self.ckpt_in_progress = False
                    self.interruptions += 1
                    self.failed_client_id = int(interrupt.cause.split(":")[1])

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
                    '''
                    if self.pckpt_in_progress == True:
                        if self.failed_client_id in self.p_queue and self.failed_client_id not in self.sp_queue:
                            # wastage should be calculated in pckpt_reset() function
                            # print ('unexpected failure')
                            self.failured_handled = False
                            self.pckpt_reset(pfs)
                        elif self.failed_client_id in self.sp_queue:
                            # print ('failure handled')
                            self.pckpt_reset(pfs)
                            self.failured_handled = True
                        elif self.failed_client_id not in self.p_queue and self.failed_client_id not in self.sp_queue:
                            # print ('previously handled failure')
                            self.pckpt_reset(pfs)
                            self.failured_handled = True
                    else:
                        self.failured_handled = False
                    '''
                    #print(self.id, 'failure happened')
                restart_time = self.env.now
                #print ('execution of '+self.name+' interrupted at '+str(restart_time)+': '+ interrupt.cause)
                if self.failured_handled == False:
                    if self.ckpt_intvs:
                        if self.ckpt_intvs[-1][1] < self.comp_intvs[-1][1]:
                            # remove computation savings, computation intervals.
                            while len(self.comp_intvs) > 0:
                                if self.comp_intvs[-1][0] > self.ckpt_intvs[-1][0]:
                                    self.waste_intvs.append([self.comp_intvs[-1][0], self.comp_intvs[-1][1]])
                                    self.comp_intvs.pop()
                                else:
                                    break
                            self.waste_intvs.append([self.comp_intvs[-1][1], restart_time])

                            while len(self.comp_saved_lm_intvs) > 0:
                                if self.comp_saved_lm_intvs[-1][0] > self.ckpt_intvs[-1][0]:
                                    self.comp_saved_lm_intvs.pop()
                                else:
                                    break
                        elif self.ckpt_intvs[-1][1] + self.pfs_ckpt_period > self.env.now and self.last_ckpt_pfs == False:
                            # that means failure happened during dumping to the PFS.
                            # this is the last checkpoint and current computation time waste.
                            self.waste_intvs.append([self.ckpt_intvs[-1][0], restart_time])
                            self.ckpt_intvs.pop()
                            # remove the last checkpoint from BB data.
                            bb.delete_ckpt(self.name, self.last_ckpt_id, self.ckpt_size)
                            self.last_ckpt_id -= 1
                            self.no_of_ckpts -= 1

                            # remove computation savings, computation intervals recursively.
                            while len(self.comp_intvs) > 0:
                                if len(self.ckpt_intvs) == 0 or self.comp_intvs[-1][0] > self.ckpt_intvs[-1][0]:
                                    self.waste_intvs.append([self.comp_intvs[-1][0], self.comp_intvs[-1][1]])
                                    self.comp_intvs.pop()
                                else:
                                    break

                            while len(self.comp_saved_lm_intvs) > 0:
                                if len(self.ckpt_intvs) == 0 or self.comp_saved_lm_intvs[-1][0] > self.ckpt_intvs[-1][0]:
                                    self.comp_saved_lm_intvs.pop()
                                else:
                                    break
                        else:
                            self.waste_intvs.append([self.ckpt_intvs[-1][1], restart_time])
                    else:
                        if self.comp_intvs:
                            self.waste_intvs.append([self.comp_intvs[-1][0], restart_time])
                            self.comp_intvs.pop()
                        else:
                            self.waste_intvs.append([0, restart_time])

                #print 'last comp intv: '+str(self.comp_intvs[-1])
                #print 'last ckpt intv: '+str(self.ckpt_intvs[-1])              
                #print 'last waste intv: '+str(self.waste_intvs[-1])
            
                while self.interruptions > 0:
                    self.interruptions -= 1
                    # for only BB, with and without limits.
                    if bb.search_ckpt(self.name, self.last_ckpt_id)  or self.last_ckpt_pfs == False:
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
                

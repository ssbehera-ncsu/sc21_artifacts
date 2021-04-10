import simpy
import random
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
        if self.ckpt_size / self.clients * 3 > 512:
            self.live_migration_threshold = 512 / 12.5 / 3600
        else:
            self.live_migration_threshold = self.ckpt_size * 3 / self.clients / 12.5 / 3600

        self.live_migration_percentage = 0

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

    #def pop_ckpt_loc(self):
    #    return self.ckpt_loc.pop(0)    

    def run(self, bb, pfs):
        with self.resource.request(priority=0) as req:
            yield req
            yield self.env.timeout(self.start_time)
        #print (self.name+' started at: '+str(self.start_time))
        self.status = 'active'
        while True:
            try:
                if sum([x[1]-x[0] for x in self.comp_intvs]) >= self.total_comp_time:
                    #print (self.name+', computation finished!')
                    self.status = 'terminated'
                    return

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
                        with self.resource.request(priority=0) as req:
                            yield req

                        time_to_failure = self.sys_fail.latest_leadtime / 3600

                        #print (self.name, self.live_migration_threshold, time_to_failure)

                        #if we have enough time to perform live migration.
                        if time_to_failure >= self.live_migration_threshold:
                            #print(self.name, 'handled', self.sys_fail.latest_leadtime/3600, self.live_migration_threshold)
                            #find next checkpoint start time.
                            next_ckpt_time = self.comp_start_time + self.comp_period
                            #find failure time
                            failure_time = time_to_failure + self.env.now
                            #if next checkpoint is after failure then wait till next checkpoint.
                            if next_ckpt_time > failure_time:
                                if bb.search_ckpt(self.name, self.last_ckpt_id):
                                    restart_period_bb = float(self.ckpt_size) / float(bb.get_real_rd_thrpt(self.clients)) / 3600
                                    restart_period_pfs = float(
                                        self.ckpt_size) / self.clients / pfs.get_real_wrt_thrpt_single(
                                        self.ckpt_size / self.clients) / 3600
                                    if restart_period_bb > restart_period_pfs:
                                        restart_period = restart_period_bb
                                    else:
                                        restart_period = restart_period_pfs
                                    if self.ckpt_intvs[-1][1] + self.pfs_ckpt_period > failure_time:
                                        #what if failure happens during write to PFS.
                                        #add waste for current computation and checkpoint to BB.
                                        time_to_wait = self.live_migration_threshold
                                        #self.waste_intvs.append([self.ckpt_intvs[-1][0], self.ckpt_intvs[-1][1]])
                                        self.comp_saved_lm_intvs.append([self.comp_intvs[-1][0], self.comp_intvs[-1][1]])
                                        self.comp_saved_lm_intvs.append([self.ckpt_intvs[-1][1], failure_time + restart_period])
                                        self.ckpt_intvs.pop()
                                        self.last_ckpt_id -= 1
                                        self.no_of_ckpts -= 1
                                    else:
                                        time_to_wait = self.live_migration_threshold
                                        if time_to_wait < (next_ckpt_time - self.env.now):
                                            time_to_wait = next_ckpt_time - self.env.now
                                        self.comp_saved_lm_intvs.append([self.comp_start_time, failure_time + restart_period])
                                else:
                                    #in case there is no checkpoint done yet.
                                    self.comp_saved_lm_intvs.append([self.comp_start_time, failure_time])
                                    time_to_wait = self.live_migration_threshold
                                    if time_to_wait < (next_ckpt_time - self.env.now):
                                        time_to_wait = next_ckpt_time - self.env.now
                                if self.comp_saved_lm_intvs[-1][1] <= self.comp_saved_lm_intvs[-1][0]:
                                    exit(-1)
                            else:
                            # if next checkpoint is before failure then move the next checkpoint to just after failure.
                                restart_period_bb = float(self.ckpt_size) / float(bb.get_real_rd_thrpt(self.clients)) / 3600
                                restart_period_pfs = float(self.ckpt_size) / self.clients / pfs.get_real_wrt_thrpt_single(
                                self.ckpt_size / self.clients) / 3600
                                if restart_period_bb > restart_period_pfs:
                                    restart_period = restart_period_bb
                                else:
                                    restart_period = restart_period_pfs
                                ckpt_time_bb = float(self.ckpt_size) / float(bb.get_real_wrt_thrpt(self.clients)) / 3600
                                ckpt_time_pfs = float(self.ckpt_size) / float(pfs.get_real_wrt_thrpt(self.clients, self.ckpt_size)) / 3600
                                ckpt_time = ckpt_time_bb + ckpt_time_pfs
                                if ckpt_time + next_ckpt_time > failure_time:
                                    self.comp_saved_lm_intvs.append([self.comp_start_time, failure_time + restart_period])
                                else:
                                    self.comp_saved_lm_intvs.append([next_ckpt_time + ckpt_time_bb, failure_time + restart_period])
                                if self.comp_saved_lm_intvs[-1][1] <= self.comp_saved_lm_intvs[-1][0]:
                                    exit(-1)
                                time_to_wait = self.live_migration_threshold

                            #print('next ckpt time:', next_ckpt_time)
                            #print('failure time:', failure_time)
                            #print('yield time:', time_to_wait)
                            yield self.env.timeout(time_to_wait)
                            comp_period = self.env.now - self.comp_start_time
                            self.comp_intvs.append([self.comp_start_time, self.comp_start_time + comp_period])
                            #print(self.name + ', comp started: ' + str(self.comp_start_time) + ', ended: ' + str(
                            #    self.comp_start_time + comp_period))
                            #print('saved computation waste due to live migration')
                        else:
                            yield self.env.timeout(time_to_failure)
                if (self.failure_alarm == True and self.ckpt_in_progress == True) or (self.failure_alarm == False):
                    if self.failure_alarm == False:
                        self.ckpt_start_time = self.env.now
                        with self.resource.request(priority=0) as req:
                            yield req
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
                    else:
                        self.failure_alarm = False

                        with self.resource.request(priority=0) as req:
                            yield req

                        time_to_failure = self.sys_fail.latest_leadtime / 3600

                        #print(self.name, self.live_migration_threshold, time_to_failure)
                        # if we have enough time to perform live migration.
                        if time_to_failure >= self.live_migration_threshold:
                            #print(self.name, 'handled', self.sys_fail.latest_leadtime / 3600,
                                  #self.live_migration_threshold)
                            #ckpt wasted
                            #self.waste_intvs.append([self.ckpt_start_time, self.env.now])
                            #computation done during live migration.
                            # Doubt
                            self.comp_intvs.append([self.env.now, self.env.now + self.live_migration_threshold])
                            if self.env.now + time_to_failure <= self.comp_intvs[-1][1] + self.ckpt_period + self.pfs_ckpt_period:
                                if bb.search_ckpt(self.name, self.last_ckpt_id):
                                    restart_period_bb = float(self.ckpt_size) / float(
                                        bb.get_real_rd_thrpt(self.clients)) / 3600
                                    restart_period_pfs = float(
                                        self.ckpt_size) / self.clients / pfs.get_real_wrt_thrpt_single(
                                        self.ckpt_size / self.clients) / 3600
                                    if restart_period_bb > restart_period_pfs:
                                        restart_period = restart_period_bb
                                    else:
                                        restart_period = restart_period_pfs
                                    self.comp_saved_lm_intvs.append([self.comp_intvs[-1][0], self.env.now + time_to_failure + restart_period])
                                else:
                                    self.comp_saved_lm_intvs.append([self.comp_intvs[-1][0], self.env.now + time_to_failure])
                            else:
                                self.comp_saved_lm_intvs.append([self.comp_intvs[-1][1] + self.ckpt_period, self.env.now + time_to_failure])
                            if self.comp_saved_lm_intvs[-1][1] <= self.comp_saved_lm_intvs[-1][0]:
                                exit(-1)
                            #first perform live migration.
                            yield  self.env.timeout(self.live_migration_threshold)

                            with self.resource.request(priority=0) as req:
                                yield req
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
                            yield_time = self.ckpt_period - (self.env.now - self.ckpt_start_time) + self.pfs_ckpt_period
                            time_to_failure = self.sys_fail.latest_leadtime / 3600
                            #print(self.name, self.live_migration_threshold, time_to_failure)
                            if yield_time > time_to_failure:
                             #   print('low failure prediction time nothing can be done, except accept fate')
                                yield self.env.timeout(time_to_failure)
                                self.ckpt_in_progress = False
                            else:
                                yield_time = self.ckpt_period - (self.env.now - self.ckpt_start_time)
                                #print(self.ckpt_period, self.env.now, self.ckpt_start_time)
                                #print(yield_time)
                                yield self.env.timeout(yield_time)
                                self.last_ckpt_id += 1
                                bb.store_ckpt(self.name, self.last_ckpt_id, self.ckpt_size, self.clients)
                                self.ckpt_intvs.append([self.ckpt_start_time, self.env.now])
                                self.ckpt_in_progress = False
                                self.no_of_ckpts += 1

                #self.set_ckpt_loc('BB')
            except simpy.Interrupt as interrupt:
                if interrupt.cause == 'alarm':
                    #if self.ckpt_in_progress:
                        #print('failure happened during checkpoint')
                    #else:
                        #print('failure happened during computation')
                    #print(self.id, 'got alarmed')
                    #print(self.sys_fail.latest_failure.id)
                    self.failure_alarm = True
                    continue
                elif interrupt.cause == 'failure':
                    #print (self.name, 'failure')
                    self.interruptions += 1
                    self.ckpt_in_progress = False
                    #print(self.id, 'failure happened')
                restart_time = self.env.now
                #print ('execution of '+self.name+' interrupted at '+str(restart_time)+': '+ interrupt.cause)
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
                    elif self.ckpt_intvs[-1][1] + self.pfs_ckpt_period > self.env.now:
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
                    if bb.search_ckpt(self.name, self.last_ckpt_id):
                        restart_period_bb = float(self.ckpt_size) / float(bb.get_real_rd_thrpt(self.clients)) / 3600
                        restart_period_pfs = float(self.ckpt_size) / self.clients / pfs.get_real_wrt_thrpt_single(
                            self.ckpt_size / self.clients) / 3600
                        if restart_period_bb < restart_period_pfs:
                            restart_period = restart_period_pfs
                        else:
                            restart_period = restart_period_bb
                    else:
                        # ckpt doesn't exist continue to computation.
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
                

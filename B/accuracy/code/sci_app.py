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
        self.ckpt_intervals = []
        self.ckpt_2bb_percentages = []
        self.no_of_ckpts = 0
        self.ckpt_intvs = []
        self.waste_intvs = []
        self.restart_intvs = []
        self.last_ckpt_id = -1
        self.ckpt_loc = deque([])
        #self.ckpt_loc = []
        self.curnt_ckpt_loc = 'BB'
        self.interruptions = 0
        self.status = ''
        self.ckpt2bb_percnt = ckpt2bb_percnt
        self.ckpt_period = 0
        self.pfs_ckpt_period = 0
        self.comp_start_time = 0

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
        #print(self.name, float(bb.get_real_wrt_thrpt(self.clients)), float(pfs.get_real_wrt_thrpt(self.clients, self.ckpt_size)), self.ckpt_size / float(pfs.get_real_wrt_thrpt(self.clients, self.ckpt_size)))
        while True:
            try:
                if sum([x[1]-x[0] for x in self.comp_intvs]) >= self.total_comp_time:
                    #print (self.name+', computation finished!')
                    self.status = 'terminated'
                    return
                self.comp_start_time = self.env.now
                with self.resource.request(priority=0) as req:
                    yield req
                    comp_period = self.comp_period
                yield self.env.timeout(comp_period)
                #print (self.name+', comp started: '+str(self.comp_start_time)+', ended: '+str(self.comp_start_time+comp_period))
                self.comp_intvs.append([self.comp_start_time, self.comp_start_time+comp_period])
                #rand = random.random()
                #print 'random number: '+str(rand)
                #if rand > 1.0:
                #    self.set_ckpt_loc('PFS')
                self.ckpt_start_time = self.env.now
                with self.resource.request(priority=0) as req:
                    yield req
                    self.ckpt_period = float(self.ckpt_size) / float(bb.get_real_wrt_thrpt(self.clients)) / 3600
                    #print(self.name, self.ckpt_period)
                    self.pfs_ckpt_period = float(self.ckpt_size) / float(pfs.get_real_wrt_thrpt(self.clients, self.ckpt_size)) / 3600
                    self.curnt_ckpt_loc = 'BB'
                    '''
                    if rand < self.ckpt2bb_percnt:
                        if bb.store_ckpt(self.name, self.last_ckpt_id, self.ckpt_size, self.clients):
                            ckpt_period = float(self.ckpt_size)/float(bb.get_real_wrt_thrpt(self.clients))/3600
                            self.curnt_ckpt_loc = 'BB'
                        else:
                            pfs.store_ckpt(self.name, self.last_ckpt_id, self.ckpt_size)
                            ckpt_period = float(self.ckpt_size)/float(pfs.get_real_wrt_thrpt(self.clients, self.ckpt_size))/3600
                            self.curnt_ckpt_loc = 'PFS'
                    else:
                            pfs.store_ckpt(self.name, self.last_ckpt_id, self.ckpt_size)
                            ckpt_period = float(self.ckpt_size)/float(pfs.get_real_wrt_thrpt(self.clients, self.ckpt_size))/3600
                            self.curnt_ckpt_loc = 'PFS'
                    '''
                yield self.env.timeout(self.ckpt_period)
                self.last_ckpt_id += 1
                rand = random.random()
                bb.store_ckpt(self.name, self.last_ckpt_id, self.ckpt_size, self.clients)
                #print (self.name+', ckpt started: '+str(self.ckpt_start_time)+', ended: '+str(self.ckpt_start_time+self.ckpt_period))
                self.ckpt_intvs.append([self.ckpt_start_time, self.ckpt_start_time+self.ckpt_period])
                self.no_of_ckpts += 1
                #self.set_ckpt_loc('BB')
            except simpy.Interrupt as i:
                self.interruptions += 1
                restart_time = self.env.now
                #print ('execution of '+self.name+' interrupted at '+str(restart_time)+': '+ i.cause)
                if self.ckpt_intvs:
                    if self.ckpt_intvs[-1][1] < self.comp_intvs[-1][1]:
                        self.waste_intvs.append([self.comp_intvs[-1][0], restart_time])
                        self.comp_intvs.pop()
                    elif self.ckpt_intvs[-1][1] + self.pfs_ckpt_period > self.env.now:
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
                #print 'last comp intv: '+str(self.comp_intvs[-1])
                #print 'last ckpt intv: '+str(self.ckpt_intvs[-1])              
                #print 'last waste intv: '+str(self.waste_intvs[-1])
            
                while self.interruptions > 0:
                    self.interruptions -= 1
                    #for both BB and PFS.
                    '''
                    if bb.search_ckpt(self.name, self.last_ckpt_id):
                        restart_period = float(self.ckpt_size)/float(bb.get_real_rd_thrpt(self.clients))/3600
                    else:
                        restart_period = float(self.ckpt_size)/float(pfs.get_real_rd_thrpt(self.clients, self.ckpt_size))/3600
                    '''

                    #for only BB, with and without limits.
                    if bb.search_ckpt(self.name, self.last_ckpt_id):
                        restart_period_bb = float(self.ckpt_size)/float(bb.get_real_rd_thrpt(self.clients))/3600
                        restart_period_pfs = float(self.ckpt_size) / self.clients / pfs.get_real_wrt_thrpt_single(self.ckpt_size/self.clients) / 3600
                        if restart_period_bb < restart_period_pfs:
                            restart_period = restart_period_pfs
                        else:
                            restart_period = restart_period_bb
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
                

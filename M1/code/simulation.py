import simpy
import os
import sys
from conf_parser import *
from sci_app import *
from sys_fail import *
from ckpt_placement import *
from sci_app_proc import *
from statistics import mean

class Simulation:
    def __init__(self, duration = 1000):
        self.env = simpy.Environment()
        self.resource = simpy.PriorityResource(self.env, capacity=1)
        self.duration = duration
        self.conf_parser = Configuration_Parser()

    def parse_conf(self, conf_fn, leadtime_var):
        [self.sys_tbf_distr, self.sys_nodes, self.apps, self.bb, self.pfs, self.ckpt_plcmnt, self.node_failures, self.soft_failures] = self.conf_parser.parse(conf_fn, self.env, self.resource)
        self.sys_fail = System_Failure(self.env, self.sys_tbf_distr, self.sys_nodes, self.node_failures, self.soft_failures, leadtime_var)
        self.app_procs = [Scientific_App_Proc(self.env, app, self.bb, self.pfs, self.sys_fail) for app in self.apps]
        self.sys_fail.app_procs = self.app_procs
        self.env.process(self.sys_fail.run(self.apps, self.bb, self.pfs))
        self.env.process(self.ckpt_plcmnt.run(self.apps, self.sys_fail, self.bb, self.pfs))

    def run(self):
        while self.env.peek() < self.duration:
            #print self.env.peek()
            self.env.step()

if __name__ == "__main__":
    sim_runs = int(sys.argv[1])
    sim_hours = int(sys.argv[2])
    res_path = sys.argv[3]
    leadtime_var = float (sys.argv[4])
    print ('Simulation runs: '+str(sim_runs))
    print ('Simulation hours: '+str(sim_hours))
    print ('Path to save results: '+res_path)
    for i in range(sim_runs):
        sim = Simulation(sim_hours)
        sim.parse_conf('sim_conf.xml', leadtime_var)
        sim.run()
        if not os.path.exists(res_path):
            os.makedirs(res_path)
        f = open(res_path+'/sim_results_'+str(i), 'w')
        comp_end_time = []
        for app in sim.apps:
            #print('ckpt intervals', app.ckpt_intvs)
            #print('waste intervals', app.waste_intvs)
            #print('restart intervals', app.restart_intvs)
            comp_time = sum([x[1]-x[0] for x in app.comp_intvs])
            comp_saved_time = sum([x[1] - x[0] for x in app.comp_saved_ckpt_intvs])
            ckpt_time = sum([x[1]-x[0] for x in app.ckpt_intvs])
            waste_time = sum([x[1]-x[0] for x in app.waste_intvs])
            restart_time = sum([x[1]-x[0] for x in app.restart_intvs])
            total_time = comp_time+ckpt_time+waste_time+restart_time
            total_no_of_ckpts = app.no_of_ckpts
            avg_percentage_of_ckpt_2bb = mean(app.ckpt_2bb_percentages)
            avg_ckpt_interval = mean(app.ckpt_intervals)
            comp_end_time.append(app.comp_intvs[-1][1])
            f.write('App comp time: '+str(app.id)+','+app.name+','+str(comp_time)+'\n')
            f.write('App ckpt time: '+str(app.id)+','+app.name+','+str(ckpt_time)+'\n')
            f.write('App waste time: '+str(app.id)+','+app.name+','+str(waste_time)+'\n')
            f.write('App restart time: '+str(app.id)+','+app.name+','+str(restart_time)+'\n')
            f.write('App comp saved time: '+str(app.id)+','+app.name+','+str(comp_saved_time)+'\n')
            f.write('App number of ckpts: ' + str(app.id) + ',' + app.name + ',' + str(total_no_of_ckpts) + '\n')
            f.write('App avg pct of ckpt 2bb: '+ str(app.id) + ',' + app.name + ',' + str(avg_percentage_of_ckpt_2bb) + '\n')
            f.write('App avg ckpt interval: ' + str(app.id) + ',' + app.name + ',' + str(avg_ckpt_interval) + '\n')
            f.write('App total time: '+str(app.id)+','+app.name+','+str(total_time)+'\n')
            f.write('App efficiency: '+str(app.id)+','+app.name+','+str(comp_time/total_time)+'\n')
            f.write('App # of failures: '+str(app.id)+','+app.name+','+str(len(app.restart_intvs))+'\n')
            f.write('App total write workloads to BB: ' + str(app.id) + ',' + app.name + ',' + str(
                sim.bb.get_total_write_workload(app.name) / 1024) + '\n')
            f.write('App total read workloads from BB: ' + str(app.id) + ',' + app.name + ',' + str(
                sim.bb.get_total_read_workload(app.name) / 1024) + '\n')
            f.write('App Write workloads to BB per day: ' + str(app.id) + ',' + app.name + ',' + str(
                sim.bb.get_total_write_workload(app.name) / app.comp_intvs[-1][1] * 24 / 1024) + '\n')
        f.close()
        print('simulation done ', i)
        #print sim.bb.get_total_write_workload()/sim.duration*24/1024
        #print sim.bb.get_total_read_workload()/1024
        #print sim.bb.storage
        #print sim.sys_fail.get_num_fail()

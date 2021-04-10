import simpy
import math
#from pulp import *
from scipy import integrate
#from scipy.optimize import minimize
#import random
from openopt import NLP
#from openopt import SNLE
from numpy import cos, arange, ones, asarray, zeros, mat, array
import sys, os
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

class Checkpoint_Placement:
    def __init__(self, env, resource, updt_window):
        self.env = env
        self.resource = resource
        self.updt_window = updt_window
        
    def optimization_bb_only_no_limit(self, apps, sys_fail, bb, pfs, current_time):
        last_fail_time = sys_fail.get_last_fail_time()
        sys_fail_rate = (integrate.quad(lambda x: sys_fail.get_tbf_distr().hazard(x), current_time - last_fail_time,
                                        current_time - last_fail_time + self.updt_window)[0]) / self.updt_window
        #print('average system failure rate during update window: ' + str(sys_fail_rate))

        app_ckpt_size = {}
        app_clients = {}
        app_fail_rates = {}
        app_ckpt2bb_time = {}
        app_ckpt2pfs_time = {}
        var_id_2_app_name = {}

        var_id = 0
        for app in apps:
            if app.status == 'terminated':
                continue
            var_id_2_app_name[var_id] = app.name
            app_ckpt_size[var_id] = app.ckpt_size
            app_clients[var_id] = app.clients
            app_fail_rates[var_id] = sys_fail_rate / sys_fail.get_nodes_num() * app.clients
            app_ckpt2bb_time[var_id] = float(app.ckpt_size) / float(bb.get_real_wrt_thrpt(app.clients)) / 3600
            app_ckpt2pfs_time[var_id] = float(app.ckpt_size) / float(pfs.get_real_wrt_thrpt(app.clients, app.ckpt_size)) / 3600
            #print(app.name + ' ckpt size ' + str(app.ckpt_size))
            #print(app.name + ' bb throughput ' + str(float(bb.get_real_wrt_thrpt(app.clients))))
            #print(app.name + ' pfs throughput ' + str(float(pfs.get_real_wrt_thrpt(app.clients, app.ckpt_size))))
            #print(app.name + ' 2bb time ' + str(app_ckpt2bb_time[var_id]) + ' 2pfs time ' + str(app_ckpt2pfs_time[var_id]))
            #print(app.name + ' comp_period before: ' + str(app.comp_period))
            #print(app.name + ' app failrate ' + str(app_fail_rates[var_id]))
            app.comp_period = math.sqrt((2 * app_ckpt2bb_time[var_id] / app_fail_rates[var_id]) + (
                        2 * app_ckpt2pfs_time[var_id] * app_ckpt2bb_time[var_id]))
            #print(app.name + ' comp_period after: ' + str(app.comp_period))
            app.ckpt_intervals.append(app.comp_period)
            app.ckpt_2bb_percentages.append(1)
            var_id += 1

    def optimization(self, apps, sys_fail, bb, pfs, current_time):
        print ('ckpt placement optimization started at: '+str(current_time))
        last_fail_time = sys_fail.get_last_fail_time()
        print ('last failure occurred at: '+str(last_fail_time))
        #sys_fail_rate = sys_fail.get_tbf_distr().hazard(current_time+0.5*self.updt_window-last_fail_time)
        sys_fail_rate = (integrate.quad(lambda x: sys_fail.get_tbf_distr().hazard(x), current_time-last_fail_time, current_time-last_fail_time+self.updt_window)[0])/self.updt_window
        print ('average system failure rate during update window: '+str(sys_fail_rate))
        bb_wrt_limits = bb.get_wrt_lim_per_day()
        app_ckpt_size = {}
        app_clients = {}
        app_fail_rates = {}
        app_ckpt2bb_time = {}
        app_ckpt2pfs_time = {}
        app_left_comp_time = {}
        var_id_2_app_name = {}
        var_id = 0
        for app in apps:
            if app.status == 'terminated':
                continue
            var_id_2_app_name[var_id] = app.name
            app_ckpt_size[var_id] = app.ckpt_size
            app_clients[var_id] = app.clients
            app_fail_rates[var_id] = sys_fail_rate/sys_fail.get_nodes_num()*app.clients
            app_ckpt2bb_time[var_id] = float(app.ckpt_size)/float(bb.get_real_wrt_thrpt(app.clients))/3600
            app_ckpt2pfs_time[var_id] = float(app.ckpt_size)/float(pfs.get_real_wrt_thrpt(app.clients))/3600 
            app_left_comp_time[var_id] = app.total_comp_time-sum([x[1]-x[0] for x in app.comp_intvs])
            var_id += 1

        if not var_id_2_app_name:
            return

        '''
        print( var_id_2_app_name)
        print (app_ckpt_size)
        print (app_clients)
        print (app_fail_rates)
        print (app_ckpt2bb_time)
        print (app_ckpt2pfs_time)
        print (app_left_comp_time)

        print (var_id_2_app_name.keys())
        '''
        blockPrint()
        obj_func = lambda x: array([app_clients[i]*app_left_comp_time[i]*(x[i]) for i in var_id_2_app_name.keys()]).sum()
        print(str(obj_func))
        cons_func = lambda x: array([app_ckpt_size[i]*(app_fail_rates[i]*app_ckpt2pfs_time[i]/x[i]-0.5*x[i])/(app_ckpt2pfs_time[i]-app_ckpt2bb_time[i]) for i in var_id_2_app_name.keys()]).sum()-(bb_wrt_limits/24.0)
        print(str(cons_func))


        low_bnds = array([math.sqrt(2*app_fail_rates[i]*app_ckpt2bb_time[i]) for i in var_id_2_app_name.keys()])
        print (low_bnds)
        up_bnds = array([math.sqrt(2*app_fail_rates[i]*app_ckpt2pfs_time[i]) for i in var_id_2_app_name.keys()])
        print (up_bnds)
        #bnds = [(math.sqrt(2*app_fail_rates[app_id]*app_ckpt2bb_time[app_id]), math.sqrt(2*app_fail_rates[app_id]*app_ckpt2pfs_time[app_id])) for app_id in app_id2name.keys()]
        #print bnds
        #bnds = tuple(bnds)
        #bnds = [(0.0, 0.5) for app_id in app_id2name.keys()]
        x0 = array([math.sqrt(2*app_fail_rates[i]*(0.1*app_ckpt2bb_time[i]+0.9*app_ckpt2pfs_time[i])) for i in var_id_2_app_name.keys()])
        #x0 = up_bnds
        #x0 = array([0.0965,0.0161,0.0326,0.0011,0.00015,0.0016])
        print (x0)

        contol = 1e-5
        gtol = 1e-5
        #p = NLP(obj_func, x0, c=cons_func, lb=low_bnds, ub=up_bnds, gtol=gtol, contol=contol, iprint = 50, maxIter = 10000, maxFunEvals = 1e7, name = 'NLP_ckpt_plcmnt')
        p = NLP(obj_func, x0, c=cons_func, lb=low_bnds, ub=up_bnds, gtol=gtol, contol=contol, iprint = 10, maxIter = 10000, maxFunEvals = 1e7, name = 'NLP_ckpt_plcmnt')
        solver = 'ralg'
        #solver = 'ipopt'
        #solver = 'algencan'
        #solver = 'scipy_slsqp'
        r = p.solve(solver, plot=False)
        print (r.xf)
        print (r.ff)
        print (cons_func(r.xf))
        #print [(r.xf[i]**2/(2*app_fail_rates[i])-app_ckpt2pfs_time[i])/(app_ckpt2bb_time[i]-app_ckpt2pfs_time[i]) for i in var_id_2_app_name.keys()]
        tmp = [(r.xf[i]**2/(2*app_fail_rates[i])-app_ckpt2pfs_time[i])/(app_ckpt2bb_time[i]-app_ckpt2pfs_time[i]) for i in var_id_2_app_name.keys()]
        print (tmp)
        ckpt2bb_percnt = []
        for x in tmp:
            if x >= 0:
                ckpt2bb_percnt.append(x)
            else:
                ckpt2bb_percnt.append(0.0)
        print (ckpt2bb_percnt)
        var_val = [math.sqrt(2*app_fail_rates[i]*(ckpt2bb_percnt[i]*(app_ckpt2bb_time[i]-app_ckpt2pfs_time[i])+app_ckpt2pfs_time[i])) for i in var_id_2_app_name.keys()]
        print (var_val)
        print (cons_func(var_val))
        comp_period = [var_val[i]/app_fail_rates[i] for i in var_id_2_app_name.keys()]
        print (comp_period)
        for k, v in var_id_2_app_name.items():
            for app in apps:
                if app.name == v:
                    print (app.name)
                    #print ('comp_period before: '+str(app.comp_period))
                    app.comp_period = comp_period[k]
                    app.ckpt_intervals.append(app.comp_period)
                    #print ('comp_period after: '+str(app.comp_period)   )
                    #print ('ckpt2bb_percnt before: '+str(app.ckpt2bb_percnt))
                    app.ckpt2bb_percnt = ckpt2bb_percnt[k]
                    app.ckpt_2bb_percentages.append(app.ckpt2bb_percnt)
                    #print ('ckpt2bb_percnt after: '+str(app.ckpt2bb_percnt)   )
        enablePrint()

    def run(self, apps, sys_fail, bb, pfs):
        
        while True:
            with self.resource.request(priority=-1) as req:
                yield req
                #print ('***********************************************************')
                #print ('now is '+str(self.env.now)+', update checkpoints placement!')
                current_time = self.env.now
                #self.optimization(apps, sys_fail, bb, pfs, current_time)
                self.optimization_bb_only_no_limit(apps, sys_fail, bb, pfs, current_time)
                #print ('***********************************************************')
            yield self.env.timeout(self.updt_window)


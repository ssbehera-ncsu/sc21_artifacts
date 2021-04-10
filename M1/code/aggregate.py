from os import listdir
from os.path import isfile, join
import sys

path = sys.argv[1]
files = [join(path, fn) for fn in listdir(path) if isfile(join(path, fn))]
sim_runs = len(files)

sum_app_wrt_workload_per_day = {}
sum_app_rd_workload = {}
sum_app_comp_time = {}
sum_app_ckpt_time = {}
sum_app_waste_time = {}
sum_app_restart_time = {}

sum_app_comp_ckpt_saved_time = {}
sum_app_no_of_ckpts = {}
sum_app_pct_of_ckpt_2bb = {}
sum_app_ckpt_interval = {}

sum_app_efficiency = {}
sum_app_total_time = {}
sum_app_failures = {}

read_bb = []
for fn in files:
    f = open(fn, 'r')
    for line in f:
        a = line.split(':')
        if a[0] == 'App Write workloads to BB per day':
            b = a[1].split(',')
            if b[1] in sum_app_wrt_workload_per_day:
                sum_app_wrt_workload_per_day[b[1]] += float(b[2])
            else:
                sum_app_wrt_workload_per_day[b[1]] = float(b[2])
        elif a[0] == 'App total read workloads from BB':
            b = a[1].split(',')
            if b[1] in sum_app_rd_workload:
                sum_app_rd_workload[b[1]] += float(b[2])
            else:
                sum_app_rd_workload[b[1]] = float(b[2])
        elif a[0] == 'App avg ckpt interval':
            b = a[1].split(',')
            if b[1] in sum_app_ckpt_interval:
                sum_app_ckpt_interval[b[1]] += float(b[2])
            else:
                sum_app_ckpt_interval[b[1]] = float(b[2])
        elif a[0] == 'App avg pct of ckpt 2bb':
            b = a[1].split(',')
            if b[1] in sum_app_pct_of_ckpt_2bb:
                sum_app_pct_of_ckpt_2bb[b[1]] += float(b[2])
            else:
                sum_app_pct_of_ckpt_2bb[b[1]] = float(b[2])
        elif a[0] == 'App number of ckpts':
            b = a[1].split(',')
            if b[1] in sum_app_failures:
                sum_app_no_of_ckpts[b[1]] += float(b[2])
            else:
                sum_app_no_of_ckpts[b[1]] = float(b[2])
        elif a[0] == 'App comp saved time':
            b = a[1].split(',')
            if b[1] in sum_app_comp_ckpt_saved_time:
                sum_app_comp_ckpt_saved_time[b[1]] += float(b[2])
            else:
                sum_app_comp_ckpt_saved_time[b[1]] = float(b[2])
        elif a[0] == 'App comp time':
            b = a[1].split(',')
            if b[1] in sum_app_comp_time:
                sum_app_comp_time[b[1]] += float(b[2])
            else:
                sum_app_comp_time[b[1]] = float(b[2])            
        elif a[0] == 'App ckpt time':
            b = a[1].split(',')
            if b[1] in sum_app_ckpt_time:
                sum_app_ckpt_time[b[1]] += float(b[2])
            else:
                sum_app_ckpt_time[b[1]] = float(b[2])            
        elif a[0] == 'App waste time':
            b = a[1].split(',')
            if b[1] in sum_app_waste_time:
                sum_app_waste_time[b[1]] += float(b[2])
            else:
                sum_app_waste_time[b[1]] = float(b[2])            
        elif a[0] == 'App restart time':
            b = a[1].split(',')
            if b[1] in sum_app_restart_time:
                sum_app_restart_time[b[1]] += float(b[2])
            else:
                sum_app_restart_time[b[1]] = float(b[2])            
        elif a[0] == 'App total time':
            b = a[1].split(',')
            if b[1] in sum_app_total_time:
                sum_app_total_time[b[1]] += float(b[2])
            else:
                sum_app_total_time[b[1]] = float(b[2])
        elif a[0] == 'App efficiency':
            b = a[1].split(',')
            if b[1] in sum_app_efficiency:
                sum_app_efficiency[b[1]] += float(b[2])
            else:
                sum_app_efficiency[b[1]] = float(b[2])           
        elif a[0] == 'App # of failures':
            b = a[1].split(',')
            if b[1] in sum_app_failures:
                sum_app_failures[b[1]] += float(b[2])
            else:
                sum_app_failures[b[1]] = float(b[2])             

#print sum_app_total_time
for k in sum_app_total_time.keys():
    print ('Average computation time of '+k+': '+str(sum_app_comp_time[k]/sim_runs))
    print ('Average checkpoint time of '+k+': '+str(sum_app_ckpt_time[k]/sim_runs))
    print ('Average waste time of '+k+': '+str(sum_app_waste_time[k]/sim_runs))
    print ('Average restart time of '+k+': '+str(sum_app_restart_time[k]/sim_runs))
    print ('Average total running time of '+k+': '+str(sum_app_total_time[k]/sim_runs))
    print ('Average efficiency of '+k+': '+str(sum_app_efficiency[k]/sim_runs))
    print ('Average failures of '+k+': '+str(sum_app_failures[k]/sim_runs))
    print ('Average comp time saved ' + k + ': ' + str(sum_app_comp_ckpt_saved_time[k]/sim_runs))
    print ('Average no. of checkpoints ' + k + ': ' + str(sum_app_no_of_ckpts[k]/sim_runs))
    print ('Average checkpoint interval ' + k + ': ' + str(sum_app_ckpt_interval[k]/sim_runs))
    print ('Average pct of checkpoints to BB ' + k + ': ' + str(sum_app_pct_of_ckpt_2bb[k]/sim_runs))
    print('Average write workloads to BB per day: ' + str(sum_app_wrt_workload_per_day[k] / sim_runs))
    print('Average total read workloads from BB: ' + str(sum_app_rd_workload[k] / sim_runs))

for k in sum_app_total_time.keys():
    print('[' + str(sum_app_ckpt_time[k]/sim_runs) + ','
          + str(sum_app_waste_time[k]/sim_runs) + ',' + str(sum_app_restart_time[k]/sim_runs) + ','
          + str(sum_app_efficiency[k]/sim_runs * 100) + ','
          + str(sum_app_failures[k]/sim_runs) + ',' + str(sum_app_no_of_ckpts[k] / sim_runs) + ','
          + str(sum_app_ckpt_interval[k] / sim_runs) + ','
          + str(sum_app_wrt_workload_per_day[k] / sim_runs) + ']')

fout = open('read_bb.txt', 'w')
for i in read_bb:
    fout.write(str(i)+'\n')
fout.close()

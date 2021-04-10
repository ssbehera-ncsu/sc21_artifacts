from os import listdir
from os.path import isfile, join
import sys

path = sys.argv[1]
files = [join(path, fn) for fn in listdir(path) if isfile(join(path, fn))]
sim_runs = len(files)

app_ckpt_time = {}
app_waste_time = {}
app_restart_time = {}

for fn in files:
    f = open(fn, 'r')
    for line in f:
        a = line.split(':')
        if a[0] == 'App ckpt time':
            b = a[1].split(',')
            if b[1] in app_ckpt_time:
                app_ckpt_time[b[1]].append(float(b[2]))
            else:
                app_ckpt_time[b[1]] = [float(b[2])]            
        elif a[0] == 'App waste time':
            b = a[1].split(',')
            if b[1] in app_waste_time:
                app_waste_time[b[1]].append(float(b[2]))
            else:
                app_waste_time[b[1]] = [float(b[2])]            
        elif a[0] == 'App restart time':
            b = a[1].split(',')
            if b[1] in app_restart_time:
                app_restart_time[b[1]].append(float(b[2]))
            else:
                app_restart_time[b[1]] = [float(b[2])] 
    f.close()

fout1 = open('ckpt-time.txt', 'w')
fout2 = open('waste-time.txt', 'w')
fout3 = open('restart-time.txt', 'w')
for i in range(sim_runs):
    count = 0
    for k, v in app_ckpt_time.iteritems():
        if count == len(app_ckpt_time.keys())-1:
            fout1.write(str(v[i])+'\n')
        else:
            fout1.write(str(v[i])+',')
        count += 1
    count = 0
    for k, v in app_waste_time.iteritems():
        if count == len(app_waste_time.keys())-1:
            fout2.write(str(v[i])+'\n')
        else:
            fout2.write(str(v[i])+',')
        count += 1
    count = 0
    for k, v in app_restart_time.iteritems():
        if count == len(app_restart_time.keys())-1:
            fout3.write(str(v[i])+'\n')
        else:
            fout3.write(str(v[i])+',')
        count += 1
fout1.close()
fout2.close()
fout3.close()
    

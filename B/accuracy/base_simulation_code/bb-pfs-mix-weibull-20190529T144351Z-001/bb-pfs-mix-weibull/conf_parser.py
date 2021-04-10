import xml.etree.ElementTree as ET
import re
from prob_distr import *
from sci_app import *
#from sys_fail import *
from storage import *
from ckpt_placement import *
from sys_fail import *

class Configuration_Parser:
    def __init__(self):
        self.conf_fn = ''

    def parse(self, conf_fn, env, resource):
        apps = []
        self.conf_fn = conf_fn
        tree = ET.parse(self.conf_fn)
        root = tree.getroot()
        fail_distr = root.find('sys_fail').find('distr')
        fail_distr_name = fail_distr.get('name')
        if fail_distr_name == 'exponential':
            rate = float(fail_distr.get('rate'))
            print (rate)
            sys_tbf_distr = Exponential(rate)
        elif fail_distr_name == 'weibull':
            shape = float(fail_distr.get('shape'))
            scale = float(fail_distr.get('scale'))
            location = float(fail_distr.get('location'))
            sys_tbf_distr = Weibull(shape, scale, location)

        node_failures = []
        soft_failures = []

        for node_failure in root.find('node_failures').findall('node_failure'):
            id = str(node_failure.find('id').text)
            frequency = float(node_failure.find('frequency').text)
            meanleadtime = float(node_failure.find('meanleadtime').text)
            stddev = float(node_failure.find('stddev').text)
            startphrase = str(node_failure.find('startphrase').text)
            endphrase = str(node_failure.find('endphrase').text)
            failure_type = "nodefailure"
            if frequency >= 1:
                node_failures.append(Failure(id, frequency, meanleadtime, stddev, startphrase, endphrase, failure_type))

        for soft_failure in root.find('soft_failures').findall('soft_failure'):
            id = str(soft_failure.find('id').text)
            frequency = float(soft_failure.find('frequency').text)
            meanleadtime = float(soft_failure.find('meanleadtime').text)
            stddev = float(soft_failure.find('stddev').text)
            startphrase = str(soft_failure.find('startphrase').text)
            endphrase = str(soft_failure.find('endphrase').text)
            failure_type = "softfailure"
            if frequency >= 1:
                soft_failures.append(Failure(id, frequency, meanleadtime, stddev, startphrase, endphrase, failure_type))

        sys_nodes = int(root.find('sys_fail').find('nodes').text)
        for app in root.find('apps').findall('app'):
            app_name = app.attrib['name']
            #print app_name
            app_id = int(app.find('id').text)
            app_start_time = float(app.find('start_time').text)
            app_comp_period = float(app.find('comp_period').text)
            app_ckpt_size = float(app.find('ckpt_size').text) / 18688 * 4608 * 16
            app_clients = int(app.find('clients').text)
            app_client_id_start = int(app.find('client_id_start').text)
            app_client_id_end = int(app.find('client_id_end').text)
            app_total_comp_time = float(app.find('total_comp_time').text)
            app_ckpt2bb_percnt = float(app.find('ckpt2bb_percnt').text)
            #print (app_id, app_comp_period, app_ckpt_size, app_clients)
            sci_app = Scientific_App(env, resource, app_name, app_id, app_start_time, app_comp_period, app_ckpt_size, app_clients, app_client_id_start, app_client_id_end, app_total_comp_time, app_ckpt2bb_percnt)
            apps.append(sci_app)

        bb = root.find('burst_buffer')
        bb_capacity = float(bb.find('capacity').text)
        bb_max_wrt_thrpt = float(bb.find('max_wrt_thrpt').text)
        bb_max_rd_thrpt = float(bb.find('max_rd_thrpt').text)
        bb_wrt_lim_per_day = float(bb.find('wrt_lim_per_day').text)
        burst_buf = Burst_Buffer(bb_capacity, bb_max_wrt_thrpt, bb_max_rd_thrpt, bb_wrt_lim_per_day)


        pfs = root.find('pfs')
        pfs_capacity = float(pfs.find('capacity').text)
        memory_ranges = []
        for memory_range in root.find('pfs').findall('memory_range'):
            id = int(memory_range.find('id').text)
            limit = float(memory_range.find('limit').text)
            bandwidth = float(memory_range.find('bandwidth').find('limit').text)
            saturation_point = int(memory_range.find('bandwidth').find('saturation_point').text)
            memory_ranges.append(Memory_Range(id, limit, bandwidth, saturation_point))

        parallel_file_sys = PFS(pfs_capacity, memory_ranges)

        ckpt_plcmnt = root.find('ckpt_placement')
        ckpt_plcmnt_updt_window = float(ckpt_plcmnt.find('updt_window').text)
        ckpt_placement = Checkpoint_Placement(env, resource, ckpt_plcmnt_updt_window)

        return [sys_tbf_distr, sys_nodes, apps, burst_buf, parallel_file_sys, ckpt_placement, node_failures, soft_failures]


'''
888888888888                                      88              88
         ,88                                      88              88
       ,88"                                       88              88
     ,88"     ,adPPYba,  8b,dPPYba,   ,adPPYba,   88  ,adPPYYba,  88,dPPYba,
   ,88"      a8P_____88  88P'   "Y8  a8"     "8a  88  ""     `Y8  88P'    "8a
 ,88"        8PP"""""""  88          8b       d8  88  ,adPPPPP88  88       d8
88"          "8b,   ,aa  88          "8a,   ,a8"  88  88,    ,88  88b,   ,a8"
888888888888  `"Ybbd8"'  88           `"YbbdP"'   88  `"8bbdP"Y8  8Y"Ybbd8"'

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0.

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


__author__ = "@netwookie"
__credits__ = ["Rick Kauffman"]
__license__ = "Apache2"
__version__ = "0.1.1"
__maintainer__ = "Rick Kauffman"
__status__ = "Alpha"

'''
from flask import Flask, request, render_template, abort, redirect, url_for
from jinja2 import Environment, FileSystemLoader
from pyVim.connect import SmartConnect, Disconnect
import urllib3
from pyVmomi import vim
from pyVim.task import WaitForTask
from utility.revert_vm import revert_vm
import utility.nic2dvs as nic
from utility.port_info import port_info
from utility.vm_watcher import vm_watcher
import logging
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


#
app = Flask(__name__)

logging.basicConfig(filename="toolbox.log",
					format='%(asctime)s %(message)s',
					filemode='a')


'''
#-------------------------------------------------------------------------------
Main Page
#-------------------------------------------------------------------------------
'''

@app.route("/", methods=('GET', 'POST'))
def login():
    message='Welcome to the machine'
    return render_template('home.html')

@app.route("/home", methods=('GET', 'POST'))
def home():
    message='Welcome to the machine'
    return render_template('home.html', message=message)



@app.route("/show_connect", methods=('GET', 'POST'))
def show_connect():
    content, si = nic.login(port_info)

    workloads = port_info['workloads']

    lines = []
    for load in workloads:
        line = vm_watcher(content,load)
        lines.append(line)

    Disconnect(si)
    
    return render_template('list_connects.html', lines=lines)

@app.route("/connect_workload", methods=('GET', 'POST'))
def connect_workload():
    content, si = nic.login(port_info)

    switch = nic.find_dvs_by_name(content, port_info['dvs_name'])
    switch_uuid = switch.uuid

    vm = nic.find_vm_by_name(content, port_info['vm_name'])

    #dvs = nic.find_dvs_by_name(content, port_info['dvs_name'])
    
    port_group = nic.find_dvs_portgroup_by_name(content, port_info['dvs_name'],port_info['dvs_pg'])
    if port_group:
        tash, portgroup_key = str(port_group).split(':')
        portgroup_key = portgroup_key[:-1]

    portKey = port_info['portKey']
    pg_name = port_info['dvs_pg']
    vnic_mac = port_info['vmnic_mac']

    response = nic.connect_vnic_to_portgroup(vm, portgroup_key, vnic_mac, switch_uuid, pg_name, portKey)

    Disconnect(si)
    message='VM Nic has been connected to the switch'
    return render_template('home.html', message=message)

def traverse_snapshots(snapshot_tree):
    # Recursively traverse and collect all snapshots
    snapshots = []
    for child_snapshot in snapshot_tree:
        snapshots.append(child_snapshot)
        snapshots.extend(traverse_snapshots(child_snapshot.childSnapshotList))
    return snapshots

@app.route("/reset_afc", methods=('GET', 'POST'))
def reset_afc():
    content, si = nic.login(port_info)

    vm = nic.find_vm_by_name(content, port_info['afc_name'])
  
    if vm.snapshot:
        snapshot_tree = vm.snapshot.rootSnapshotList
        snapshot_list = traverse_snapshots(snapshot_tree)
        if snapshot_list:
            for snapshot in snapshot_list:
                if snapshot.name == '201LAB':
                    
                    # Power Off the VM
                    vm.PowerOff()
                        
                    # Revert VM
                    response = revert_vm(snapshot.snapshot)
                        
                    # Power On the VM
                    vm.ResetVM_Task()
                   

    Disconnect(si)

    message='Your AFC has been reset'
    return render_template('home.html', message=message)

    return render_template('list_logs.html')



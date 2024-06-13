from pyVmomi import vim
from pyVim.task import WaitForTask
from pyVim.connect import SmartConnect, Disconnect
import logging
import ssl
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def login(port_info):

    sslContext = ssl._create_unverified_context()
    port="443"

    # Create a connector to vsphere
    si = SmartConnect(
        host=port_info['vsp_ip'],
        user=port_info['vsp_user'],
        pwd=port_info['vsp_pass'],
        port=port,
        sslContext=sslContext
    )
    content = si.RetrieveContent()
   
    return content, si

def list_dvs_switches(content):
    dvs_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualSwitch], True)
    dvs_list = dvs_view.view
    dvs_view.Destroy()
    return dvs_list

def list_networks(content):
    network_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.Network], True)
    networks = network_view.view
    network_view.Destroy()
    return networks

def get_vm_on_dvs(content, dvs_name):
   
     # Retrieve all Distributed Virtual Switches 
     container = content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualSwitch], True) 
     dvs_list = container.view 
     container.Destroy() 
     # Find the specific DVS by name 
     dvs = None 
     for d in dvs_list: 
        if d.name == dvs_name: 
            dvs = d 
            break

     if not dvs: 
        raise Exception(f"Distributed Virtual Switch '{dvs_name}' not found.") 

     # Retrieve all virtual machines connected to the DVS 
     vm_list = [] 
     for portgroup in dvs.portgroup: 
        for vm in portgroup.vm: 
            if vm not in vm_list: 
                vm_list.append(vm) 
                
     return vm_list


# Function to find a virtual machine by its name
def find_vm_by_name(content, vm_name):
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    for vm in container.view:
        if vm.name == vm_name:
            return vm
    return None

# Function to find a distributed virtual switch by its name
def find_dvs_by_name(content, dvs_name):
    dvs_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualSwitch], True)
    for switch in dvs_view.view:
        if switch.name == dvs_name:
            return switch
    return None


def find_dvs_portgroup_by_name(content, dvs_name, portgroup_name):
    dvs = find_dvs_by_name(content, dvs_name)
    if dvs:
        portgroup = find_portgroup_by_name(content, dvs, portgroup_name)
        return portgroup
    else:
        return None
    
# Function to find the snapshot by its name
def get_snapshot_by_name(snapshots, snap_name): 
    for snapshot in snapshots: 
        if snapshot.name == snap_name: 
            return snapshot 
        elif snapshot.childSnapshotList: 
            result = get_snapshot_by_name(snapshot.childSnapshotList, snap_name) 
            if result: 
                return result 
    return None

# Function to revert the snapshot
def revert_snapshot(vm, snapshot_name): 
    snapshot = get_snapshot_by_name(vm.snapshot.rootSnapshotList, snapshot_name) 
    if snapshot: 
        task = snapshot.snapshot.RevertToSnapshot_Task() 
        return task 
    else: print(f"Snapshot '{snapshot_name}' not found for VM '{vm.name}'") 
    return None

def find_portgroup_by_name(content, dvs, portgroup_name):
    portgroup_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.dvs.DistributedVirtualPortgroup], True)
    portgroups = [pg for pg in portgroup_view.view if pg.config.distributedVirtualSwitch == dvs and pg.name == portgroup_name]
    portgroup_view.Destroy()
    if portgroups:
        return portgroups[0]
    else:
        return None

def connect_vnic_to_portgroup(vm, portgroup_key, vnic_mac, switch_uuid, portgroup_name, portKey):
    
    devices = vm.config.hardware.device
    for device in devices:
        if isinstance(device, vim.vm.device.VirtualVmxnet3) and device.macAddress == vnic_mac:
        
            nic_spec = vim.vm.device.VirtualDeviceSpec()
            nic_spec.device = device
            nic_spec.device.connectable.connected = True
            nic_spec.device.deviceInfo.summary = portgroup_name
            nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
            nic_spec.device.backing.port.switchUuid = switch_uuid
            nic_spec.device.backing.port.portgroupKey = portgroup_key
            nic_spec.device.backing.port.portKey = portKey
            #
            config_spec = vim.vm.ConfigSpec(deviceChange=[nic_spec])
         
            vm.ReconfigVM_Task(config_spec)
            print("Successfully connected vNIC with MAC {} to DVS port group.".format(vnic_mac))

            return
    print("No vNIC found with MAC {} on the VM.".format(vnic_mac))

    return None

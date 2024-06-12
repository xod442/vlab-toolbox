from pyVmomi import vim
from pyVim.task import WaitForTask

import logging

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

def list_dvs_ports(content, dvs_name):
    try:
         
        # Create a view of all the networks (including DVS)
        container_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.Network], True)

        # Filter out the DistributedVirtualSwitch by name
        dvs = None
        for network in container_view.view:
            if isinstance(network, vim.DistributedVirtualSwitch) and network.name == dvs_name:
                dvs = network
                break
        
        if dvs is None:
            raise Exception(f"Distributed Virtual Switch '{dvs_name}' not found.")

        # Retrieve all ports on the distributed virtual switch
        port_list = dvs.FetchDVPorts()
         rick.append('fail')
        
        # print(f"Port Key: {port.key}, Port Name: {port.config.name}")  
    except Exception as e:
            return e
   
    return port_list

def get_dvs_ports(content, dvs_name):
    dvs_ports = []

    # Get DistributedVirtualSwitch object
    dvs = None
    for dvs_mor in content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualSwitch], True).view:
        if dvs_mor.name == dvs_name:
            dvs = dvs_mor
            break

    if not dvs:
        print("DVS '{}' not found.".format(dvs_name))

    # Get DistributedVirtualPortgroup objects

    dvs_portgroups = dvs.portgroup
   
    for dvs_pg in dvs_portgroups:
         #
        # Get DistributedVirtualPort objects
        dvs_ports.append(dvs_pg)
    rick.append('fail')
    

    return dvs_ports
def revert_vm_snap_by_name(content,level,vm_name):

    vm_list = content.viewManager.CreateContainerView(content.rootFolder,
                                                     [vim.VirtualMachine],
                                                    True)
    vm_data = vm_list.view

    #---------------------------------------------------------------------------
    #
    #  Step 1: Find VM in list of VMs
    #
    #---------------------------------------------------------------------------
    
    # revert all vms to snapshot named 202LAB and reboot or reset vm.
    for vm in vm_data:
        if vm.name == vm_name:
            if vm.snapshot:
                snapshot_tree = vm.snapshot.rootSnapshotList
                snapshot_list = traverse_snapshots(snapshot_tree)
                if snapshot_list:
                    for snapshot in snapshot_list:


                        if snapshot.name == level:
                            message = "VM Name is %s ==> Processing snapshot %s for level %s........" % (vm.name,snapshot.name,level)
                            logging.warning(message)
                            when = str(datetime.datetime.now())
                            # Power Off the VM
                            vm.PowerOff()
                            message = "%s ==> vm%s: %s has been powered OFF" % (counter,when,vm.name)
                            logging.warning(message)
                            response = write_log(db,message)
                            # Revert VM
                            response = revert_vm(snapshot.snapshot)
                            # Power On the VM
                            vm.ResetVM_Task()
                            # Compose log information
                            when = str(datetime.datetime.now())
                            message = "%s ==> vm%s: %s has been reverted and powered back ON" % (counter,when,vm.name)
                            logging.warning(message)
                            response = write_log(db,message)
                            counter = counter + 1



    vm_list.Destroy()

    when = str(datetime.datetime.now())
    message = "%s ==> All All virtual machines have been reverted\n" % (when)
    logging.warning(message)
    response = write_log(db,message)

    return None

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

def find_portgroup_by_name(content, dvs, portgroup_name):
    portgroup_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.dvs.DistributedVirtualPortgroup], True)
    portgroups = [pg for pg in portgroup_view.view if pg.config.distributedVirtualSwitch == dvs and pg.name == portgroup_name]
    portgroup_view.Destroy()
    if portgroups:
        return portgroups[0]
    else:
        return None

def connect_vnic_to_portgroup(vm, portgroup_key, vnic_mac, switch_uuid, portgroup_name, portKey):
    print('blue')
    devices = vm.config.hardware.device
    for device in devices:
        if isinstance(device, vim.vm.device.VirtualVmxnet3) and device.macAddress == vnic_mac:
            # bprint(device.backing.port.switchUuid)

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
            # print(nic_spec)
            vm.ReconfigVM_Task(config_spec)
            print("Successfully connected vNIC with MAC {} to DVS port group.".format(vnic_mac))

            return
    print("No vNIC found with MAC {} on the VM.".format(vnic_mac))

    return None

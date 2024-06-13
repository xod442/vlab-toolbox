import urllib3
import utility.nic2dvs as nic
from pyVmomi import vim


def vm_watcher(content, name):

    vm = nic.find_vm_by_name(content, name)
    devices = vm.config.hardware.device
    for device in devices:
        if isinstance(device, vim.vm.device.VirtualVmxnet3):
            if device.connectable.connected == True:
                line = "Workload: {} MAC address: {} connected state {}.".format(name, device.macAddress, device.connectable.connected)    
            else:
                line = "Workload: {} MAC address: {} IS NOT CONNECTED TO THE SWITCH!!!!.".format(name, device.macAddress)
    return line          
        
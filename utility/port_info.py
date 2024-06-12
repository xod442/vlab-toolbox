dvs_name = 'LG01-dvs-1'
dvs_pg = 'LG01-DP-01'
vm_name ='LG01-WL01-V10-101'
vmnic_mac = '00:50:56:b6:5c:a6'
portKey = '1'
vsp_ip = '10.250.0.50'
vsp_user = 'administrator@vsphere.local'
vsp_pass = "password"


'''
Data Center POD automation script
2024 wookieware.

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
__email__ = "rick@rickkauffman.com"
__status__ = "Alpha"
'''

def port_info():

    port_info = {
                'dvs_name' : 'LG01-dvs-1',  
                'dvs_pg' : 'LG01-DP-01',
                'vm_name' :'LG01-WL01-V10-101',
                'vmnic_mac' : '00:50:56:b6:5c:a6',
                'portKey' : '1',
                'vsp_ip' : '10.250.0.50',
                'vsp_user' : 'administrator@vsphere.local',
                'vsp_pass' : "password"
                }
    return port_info

# Title:        Remote Network Scan
# Description:  Perform a remote network scan based on NBTSCAN
# Requirements: Python3 with paramiko module installed
# Author:       Stephan Avenwedde
# Copyright:    Beckhoff Automation Gmbh & Co. KG
# License:      0BSD

import argparse
import paramiko
import sys
import time
import re
import os

parser = argparse.ArgumentParser(description='Parse all arguments')
parser.add_argument("address", help="IP Address from remote system e.g. 192.168.6.15")
parser.add_argument("user", help="username for remote system login e.g. Administrator")
parser.add_argument("password", help="password for remote system login e.g. 1")
parser.add_argument("interface", help="Interface to bo used")

args = parser.parse_args()

addr = args.address
user = args.user
password = args.password
interface = args.interface
read_delay = 0.5 # Seconds

def read_shell(shell: paramiko.Channel):
    if shell.recv_ready():
        recvBytes = shell.recv(50000)
        return recvBytes.decode('utf8')

# Alternative approach
def get_devices_from_arp(client: paramiko.SSHClient):
    shell = client.invoke_shell()
    sentbytes = shell.send('arp -i {} -a\n'.format(interface))

    time.sleep(read_delay)
    s_arp_raw = read_shell(shell).splitlines()

    s_raw_list = s_arp_raw[10:]

    # declaring the regex pattern for IP addresses 
    pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})') 
    
    # initializing the list object 
    lst=[] 
    res = None
    # extracting the IP addresses 
    for line in s_raw_list: 
            if(res := pattern.search(line)):
                lst.append(res[0]) 
    
    return lst


def get_devices_from_nbtscan(client: paramiko.SSHClient):

    cmd_ip = "ifconfig {} | grep 'inet' | awk -F ' ' '{{ print $2 }}'".format(interface)
    _, stdout, _ = client.exec_command(cmd_ip)
    iface_ip = stdout.read().decode('utf8').replace('\n', '')

    cmd_netmask = "ifconfig {} | grep 'netmask' | awk '/netmask/{{ print $4;}}'".format(interface)
    _, stdout, _ = client.exec_command(cmd_netmask)
    iface_netmask_raw = stdout.read().decode('utf8').replace('\n', '')
    iface_netmask = int(iface_netmask_raw, 16)
    bitcount = bin(iface_netmask).count("1") + 1 # +1 for skipping boradcast request
    
    _, stdout, _ = client.exec_command('nbtscan {}/{}'.format(iface_ip, bitcount))
    result = stdout.read().decode('utf8').replace('\\n', '\n')
    return result
    
read_delay = 0.5  # Seconds

# print('Target address: {}'.format(addr))
# print('User: {}'.format(user))
# print('Password: {}'.format(password))
# print('Interface: {}'.format(interface))

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
try:
    client.connect(addr, username=user, password=password)
    
except Exception as e:
    print('SSH connection failed: {}'.format(str(e)))
    sys.exit()

while True:
    os.system('cls')
    #print('\n'.join(get_devices_from_arp(client))) # Read ARP table -> alternative approach, no scan
    print(get_devices_from_nbtscan(client))
    i = input("Press Enter to refresh, any other key to quit...")
    if i:
        break

  

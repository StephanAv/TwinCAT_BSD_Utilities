# Title:        Automatic remote configuration of system using ssh
# Description:  This script can remotely preconfigure your TwinCAT/BSD system
# Requirements: Python3 with paramiko module installed
# Author:       Heiko Wilke
# Copyright:    Beckhoff Automation Gmbh & Co. KG
# License:      0BSD

import argparse
import paramiko
import sys
import time
import os

parser = argparse.ArgumentParser(description='Parse all arguments')
parser.add_argument("address", help="IP Address from remote system e.g. 192.168.6.15")
parser.add_argument("user", help="username for remote system login e.g. Administrator")
parser.add_argument("password", help="password for remote system login e.g. 1")
parser.add_argument("configfile", help="File path to config script")

args = parser.parse_args()

addr = args.address
user = args.user
password = args.password
file_path = args.configfile


def read_shell(shell: paramiko.Channel):
    if shell.recv_ready():
        recvBytes = shell.recv(50000)
        return recvBytes.decode('utf8')


read_delay = 0.5  # Seconds

print('Target address: {}'.format(addr))
print('Config file path: {}'.format(file_path))
print('User: {}'.format(user))
print('Password: {}'.format(password))

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
try:
    client.connect(addr, username=user, password=password)
    shell = client.invoke_shell()
except Exception as e:
    print('SSH connection failed: {}'.format(str(e)))
    sys.exit()

# Transfer config script file
sftp = client.open_sftp()
if os.path.isfile(file_path):
    try:
        sftp.put(file_path, '/home/Administrator/config.sh')
    except Exception as e:
        print('SFTP connection failed: {}'.format(str(e)))
        sys.exit()
else:
    raise IOError('Could not find localFile %s !!' % localFile)
sftp.close()

# Try to get root rights via doas
sentbytes = shell.send('doas -S\n')
if sentbytes > 0:
    print("Root shell requested")

time.sleep(read_delay)
read_shell(shell)

sentbytes = shell.send('{}\n'.format(password))
if sentbytes > 0:
    print("Password send")

time.sleep(read_delay)
read_shell(shell)

# Check for root rights
sentbytes = shell.send('whoami\n')
if sentbytes > 0:
    print("Cheking root rights")
time.sleep(read_delay)
ret = read_shell(shell)

if 'root' in ret:
    print('>>> Root rights granted')
else:
    print('Root rights not granted, cannot start config script - EXIT')
    sys.exit()

# Run config script with root rights
shell.send("sh config.sh\n")
time.sleep(read_delay)
ret = read_shell(shell)

print('>>>>> Config Complete <<<<<')

client.close()
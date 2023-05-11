from pathlib import Path
from hurry.filesize import size
import paramiko
import time
import binascii
import base64


chunc = 2 ** 20
backup_name = Path.home() / 'Downloads' / 'backup_x.tcbkp00'
backup_decoded_name = Path.home() / 'Downloads' / 'backup_decoded.tcbkp00'

def read_shell(shell : paramiko.Channel):
    if shell.recv_ready():
        recvBytes = shell.recv(50000)
        for line in recvBytes.decode('utf8').splitlines():
            print(line)

# with open(backup_name, 'wb') as f:
#     #process = subprocess.Popen("ssh root@192.168.1.90 \" sh -c 'TcBackup.sh --disk /dev/ada0'\"", stdout=subprocess.PIPE)
#     #process = subprocess.Popen("ssh -t Administrator@192.168.1.121 'doas TcBackup.sh --disk /dev/ada0'", stdout=subprocess.PIPE)
#     process = subprocess.Popen("ssh -t Administrator@192.168.1.121 \"doas sh -c '/usr/local/bin/TcBackup.sh --disk /dev/ada0'\"", stdout=subprocess.PIPE)
#     for c in iter(lambda: process.stdout.read(chunc), b""):
#         f.write(c)
        
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
client.connect('192.168.1.121', username='Administrator', password='1')
#stdin, stdout, stderr = client.exec_command("doas -S")
shell = client.invoke_shell()

sentbytes = shell.send('doas -S\n')
if sentbytes  > 0:
    print("root mode requested")

time.sleep(0.2)
read_shell(shell)


sentbytes = shell.send('1\n')
if sentbytes  > 0:
    print("password send")

time.sleep(0.2)
read_shell(shell)

sentbytes = shell.send('whoami\n')
if sentbytes  > 0:
    print("whoami send")
time.sleep(0.2)
read_shell(shell)



# shell.send('stty -ocrnl\n')
# time.sleep(0.2)
# read_shell(shell)

# shell.send('stty -onlcr\n')
# time.sleep(0.2)
# read_shell(shell)

# shell.send('stty -opost\n')
# time.sleep(0.2)
# read_shell(shell)

# shell.send('echo $TERM\n')
# time.sleep(0.2)
# read_shell(shell)

# shell.send('stty -e\n')
# time.sleep(0.2)
# read_shell(shell)

shell.send("TcBackup.sh --disk /dev/ada0 2> /home/Administrator/error.log | uuencode -m -r /dev/stdout\n")
time.sleep(0.2)
read_shell(shell)

time.sleep(1)
bytes_read = 0

# Write Base 64 encoded stream
with open(backup_name, 'wb') as f:
    while shell.recv_ready():
        _bytes = shell.recv(chunc)
        #print(' '.join('{:02x}'.format(x) for x in _bytes[0:20]))
        bytes_read += len(_bytes)
        print('read {}'.format(size(bytes_read)))
        f.write(_bytes)
        time.sleep(0.3)

# Decode file

with open(backup_name, 'rb') as input_file:
    with open(backup_decoded_name, 'wb') as output_file:
        while (line := input_file.readline()) != b'':
            try:
                decoded = base64.b64decode(line)
                output_file.write(decoded)
            except binascii.Error:
                pass

print('>>> BACKUP COMPLETE <<<')

client.close()
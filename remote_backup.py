import sys, time, base64, itertools, paramiko
from pathlib import Path

addr = '192.168.1.121'
user = 'Administrator'
password = '1'
file_path = Path.home() / 'Downloads' / 'twincat_bsd_backup.tcbkp00'

t = len(sys.argv)

# Process command line arguments in the following order
#
# 1. Address
# 2. Backup file path
# 3. Password
# 4. User

if len(sys.argv) < 2:
    print(r'At least target address required! file path, password and username are optional')
    print(r'Example: remote_backup.py 192.168.1.98 C:\Users\StephanA\Downloads\mybackup.tcbkp00 1 Administrator')
    sys.exit()

addr = sys.argv[1]

if len(sys.argv) > 2:
    try:
        file_path = sys.argv[2]
    except:
        pass
    
    try:
        password = sys.argv[3]
    except:
        pass

    try:
        user = sys.argv[4]
    except:
        pass

def read_shell(shell : paramiko.Channel):
    if shell.recv_ready():
        recvBytes = shell.recv(50000)
        return recvBytes.decode('utf8')

chunc = 2 ** 20 # Bytes
megybyte = float(1024**2) # MB
spinner = itertools.cycle(['-', '\\', '|', '/'])
read_delay = 0.5 # Seconds
stream_delay = 1.0 # Seconds

print('Target address: {}'.format(addr))
print('Backup file path: {}'.format(file_path))
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

sentbytes = shell.send('doas -S\n')
if sentbytes  > 0:
    print("Root shell requested")

time.sleep(read_delay)
read_shell(shell)


sentbytes = shell.send('{}\n'.format(password))
if sentbytes  > 0:
    print("Password send")

time.sleep(read_delay)
read_shell(shell)

sentbytes = shell.send('whoami\n')
if sentbytes  > 0:
    print("Cheking root rights")
time.sleep(read_delay)
ret = read_shell(shell)

if 'root' in ret:
    print('>>> Root rights granted')
else:
    print('Root rights not granted, cannot start backup - EXIT')


print('Receiving backup stream...')
shell.send("TcBackup.sh --disk /dev/ada0 2> /home/Administrator/error.log | uuencode -m -r /dev/stdout\n")
time.sleep(read_delay)

lastline = ''
bFirstIter = True
mb_received = 0

with open(file_path, 'wb') as f:
    while shell.recv_ready(): 
        b64_lines = shell.recv(chunc).decode('ASCII').splitlines(keepends=True)

        if bFirstIter:
            b64_lines.pop(0)
            bFirstIter = False

        mb_received += float(sum([len(i) for i in b64_lines]) / megybyte)

        if lastline != '':
            b64_lines[0] = lastline +  b64_lines[0]

        
        if '\n' in b64_lines[-1:]: # if the last line is not chopped
            lastline = ''
        else:
            lastline = b64_lines.pop() # keep the remaining strin for next iteration

        f.writelines(list(map(base64.b64decode, b64_lines)))

        print('[{}] - Backup {:6.2f} MB received  '.format(next(spinner), mb_received), end='\r')
        time.sleep(stream_delay)

print('>>>>> BACKUP COMPLETE <<<<<')

client.close()
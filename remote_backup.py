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

print('Starting backup....')
print('Target address: {}'.format(addr))
print('Backup file path: {}'.format(file_path))
print('User: {}'.format(user))
print('Password: {}'.format(password))

chunc = 2 ** 20
megybyte = float(1024**2)
spinner = itertools.cycle(['-', '\\', '|', '/'])

def read_shell(shell : paramiko.Channel):
    if shell.recv_ready():
        recvBytes = shell.recv(50000)
        return recvBytes.decode('utf8')



        
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
client.connect(addr, username=user, password=password)
shell = client.invoke_shell()

sentbytes = shell.send('doas -S\n')
if sentbytes  > 0:
    print(">>> root rights requested")

time.sleep(0.2)
read_shell(shell)


sentbytes = shell.send('{}\n'.format(password))
if sentbytes  > 0:
    print("password send")

time.sleep(0.2)
read_shell(shell)

sentbytes = shell.send('whoami\n')
if sentbytes  > 0:
    print("whoami send")
time.sleep(0.2)
zz = read_shell(shell)



shell.send("TcBackup.sh --disk /dev/ada0 2> /home/Administrator/error.log | uuencode -m -r /dev/stdout\n")
time.sleep(0.2)
read_shell(shell)

time.sleep(1)
bytes_read = 0

# Write Base 64 encoded stream
# Das Funktioniert
# with open(backup_name, 'wb') as f:
#     while shell.recv_ready():
#         _bytes = shell.recv(chunc)
#         #print(' '.join('{:02x}'.format(x) for x in _bytes[0:20]))
#         bytes_read += len(_bytes)
#         print('read {}'.format(size(bytes_read)), end='\r')
#         f.write(_bytes)
#         time.sleep(0.3)




lastline = ''
i = 0
mb_received = 0

with open(file_path, 'wb') as f:
    while shell.recv_ready(): 
        b64_lines = shell.recv(chunc).decode('ASCII').splitlines(keepends=True)

        mb_received += float(sum([len(i) for i in b64_lines]) / megybyte)

        if lastline != '':
            b64_lines[0] = lastline +  b64_lines[0]

        
        if '\n' in b64_lines[-1:]: # if the last line is not chopped
            lastline = ''
        else:
            lastline = b64_lines.pop() # keep the remaining strin for next iteration
        i += 1

        f.writelines(list(map(base64.b64decode, b64_lines)))



        # todo: writelines
        print('[{}] - Backup {:6.2f} MB received  '.format(next(spinner), mb_received), end='\r')
        #print(' '.join('{:02x}'.format(x) for x in _bytes[0:20]))
        # print(' '.join('{:02x}'.format(x) for x in _bytes))
        # bytes_read += len(_bytes)
        # print('read {}'.format(size(bytes_read)), end='\r')
        # f.write(_bytes)
        # if i == 2:
        #     k = 5
        time.sleep(1)

# Decode file

# with open(backup_name, 'rb') as input_file:
#     with open(backup_decoded_name, 'wb') as output_file:
#         while (line := input_file.readline()) != b'':
#             try:
#                 decoded = base64.b64decode(line)
#                 output_file.write(decoded)
#             except binascii.Error:
#                 pass

print('>>> BACKUP COMPLETE <<<')

client.close()
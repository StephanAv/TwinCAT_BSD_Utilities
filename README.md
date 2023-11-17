# TwinCAT BSD Utilities

## Remote Backup ([remote_backup.py](/remote_backup.py))
A Python scripts which performs a complete system backup over SSH

#### Requirements

- [Python 3.6](https://www.python.org/) or newer
- [Paramiko](https://pypi.org/project/paramiko/)

#### Usage

Arguments:
1. Address (**required**)
2. Backup file path (*optional*, default *~/Downloads/twincat_bsd_backup.tcbkp00*)
3. Password (*optional*, default: '*1*')
4. User (*optional*, default: '*Administrator*')

#### Examples

```bash
python remote_backup.py 192.168.1.98
```
```bash
python remote_backup.py 192.168.1.98 C:\Users\StephanA\Downloads\backup.tcbkp00
```
```bash
python remote_backup.py 192.168.1.98 C:\Users\StephanA\Downloads\backup.tcbkp00 123
```

The backups created with this script can be copied to a TwinCAT BSD installation stick in order to use them to perform a restore.

## Remote Config ([remote_config.py](/remote_config.py))
A Python scripts which can remotely configure your device.

#### Requirements

- [Python 3.6](https://www.python.org/) or newer
- [Paramiko](https://pypi.org/project/paramiko/)

#### Usage

```console
usage: remote_config.py [-h] address user password configfile

Parse all arguments

positional arguments:
  address     IP Address from remote system e.g. 192.168.6.15
  user        username for remote system login e.g. Administrator
  password    password for remote system login e.g. 1
  configfile  File path to config script

optional arguments:
  -h, --help  show this help message and exit
```

#### Examples

```bash
python remote_config.py 172.17.40.30 Administrator 1 test.sh
```

The test.sh script should be a configuration script which will be executed on the remote system.

## Remote Network Scan ([remote_network_scan.py](/remote_network_scan.py))

Print a list of remote network targets for which there is a entry in the arp table.

#### Requirements

- [Python 3.6](https://www.python.org/) or newer
- [Paramiko](https://pypi.org/project/paramiko/)

#### Examples

```bash
python remote_network_scan.py 192.168.1.98 Administrator 1 igb0
```



   


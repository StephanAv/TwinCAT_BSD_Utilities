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
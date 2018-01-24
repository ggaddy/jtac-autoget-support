# jtac-autoget-support

This program is for uploading RSI and /var/log/* to Juniper for JTAC support cases.

# Example
```
[agaddy@server]~% jtac-autoget-support.py
=========================================
===   Gene Gaddy gene.gaddy@ibm.com   ===
=== IBM Cloud: Datacenter Engineering ===
===    jtac-autoget-support.py v1.1   ===
=========================================
= Username: agaddy
= Password:
= Router: ppr03.dal12
= JTAC Case(ex. 2016-1207-0728): 2018-0110-0881
2018-01-24 13:25:17:021 - jtac-autoget-support.py creating varlog
2018-01-24 13:25:18:225 - jtac-autoget-support.py varlog compressed
2018-01-24 13:25:18:225 - jtac-autoget-support.py creating rsi_tmp.log (takes minutes)
2018-01-24 13:42:07:163 - jtac-autoget-support.py rsi_tmp.log created
2018-01-24 13:42:08:366 - jtac-autoget-support.py rsi compressed
2018-01-24 13:42:08:366 - SCP copy file here from router /var/tmp/2018-0110-0881_ppr03.dal12_rsi.tar.gz
2018-01-24 13:42:09:973 - SCP copy file here from router /var/tmp/2018-0110-0881_ppr03.dal12_varlog.tar.gz
2018-01-24 13:42:12:931 - file deleted on router: /var/tmp/2018-0110-0881_ppr03.dal12_rsi.tar.gz
2018-01-24 13:42:13:533 - file deleted on router: /var/tmp/2018-0110-0881_ppr03.dal12_varlog.tar.gz
2018-01-24 13:42:13:534 - JTAC FTP creating directory pub/incoming/2018-0110-0881
2018-01-24 13:42:14:735 - JTAC FTP file PUT 2018-0110-0881_ppr03.dal12_rsi.tar.gz
2018-01-24 13:42:16:262 - JTAC FTP file PUT 2018-0110-0881_ppr03.dal12_varlog.tar.gz
```

# Dependencies
> netmiko
> scp
> paramiko
> pysftp

#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
+--------------------------------------------------------------------------
|   jtac-autoget-support.py
|   ========================================
|   by Gene Gaddy
|   (c) 2018 IBM Cloud
|   https://www.ibm.com/cloud/
|   ========================================
|   Web: https://console.bluemix.net
|   Email: gene.gaddy@ibm.com
|   2018-01-18 v1.2
+--------------------------------------------------------------------------
'''

_version = '1.2'

from sys import exit
from os.path import expanduser
from os import remove
from netmiko.snmp_autodetect import SNMPDetect
from netmiko import ConnectHandler
from datetime import datetime
from getpass import getpass, getuser
from scp import SCPClient
from paramiko import SSHClient, AutoAddPolicy
import logging
import pysftp


def _get_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]


def get_type_snmp(target):
    my_snmp = SNMPDetect(hostname=target, community='snmpm3!', snmp_version='v2c')
    return my_snmp.autodetect()


def exit_not_junos(target):
    snmp_type = get_type_snmp(target)
    if snmp_type != 'juniper_junos':
        print('{0} - ERROR: only supports juniper, exiting'.format(_get_time()))
        exit()


def get_connecthandler(ip, username, password):
    dev = {
      'device_type': 'juniper_junos',
      'ip': ip,
      'username': username,
      'password': password,
      'verbose': False,
    }
    return ConnectHandler(**dev)


def make_varlog(handler, filename):
    print('{0} - jtac-autoget-support.py creating varlog'.format(_get_time()))
    cmd = 'start shell command "tar -zcvf {0} /var/log/*"'.format(filename)
    if '{master}' not in handler.send_command(cmd):
        # log error
        pass
    print('{0} - jtac-autoget-support.py varlog compressed'.format(_get_time()))


def make_rsi(handler):
    print('{0} - jtac-autoget-support.py creating rsi_tmp.log (takes minutes)'.format(_get_time()))
    cmd = 'request support information | save /var/tmp/rsi_tmp.log'
    if 'Wrote' not in handler.send_command(cmd, max_loops=15000):
        # log error
        pass
    print('{0} - jtac-autoget-support.py rsi_tmp.log created'.format(_get_time()))


def compress_rsi(handler, filename):
    cmd = 'start shell command "tar -zcvf {0} /var/tmp/rsi_tmp.log"'.format(filename)
    if '{master}' not in handler.send_command(cmd):
        # log error
        pass
    delete_cmd = 'start shell command "rm /var/tmp/rsi_tmp.log"'
    if '{master}' not in handler.send_command(delete_cmd):
        # log error
        pass
    print('{0} - jtac-autoget-support.py rsi compressed'.format(_get_time()))



def delete_file_router(handler, filename):
    cmd = 'start shell command "rm {0}"'.format(filename)
    if '{master}' not in handler.send_command(cmd):
        # log error
        pass
    print('{0} - file deleted on router: {1}'.format(_get_time(), filename))



def createSSHClient(server, port, user, password):
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(server, port, user, password)
    return client


def scp_file_here(filename, name, user, password):
    print('{0} - SCP copy file here from router {1}'.format(_get_time(), filename))
    ssh = createSSHClient(name, 22, user, password)
    with SCPClient(ssh.get_transport()) as scp:
        scp.get(filename)


def generate_filename(whichfile, jtc, name):
    return '/var/tmp/{0}_{1}_{2}.tar.gz'.format(jtc, name, whichfile)


def ftp_make_directory(jtc):
    # kvargs : jtac_case
    directory = 'pub/incoming/{0}'.format(jtc)
    print('{0} - JTAC FTP creating directory {1}'.format(_get_time(), directory))
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    try:
        with pysftp.Connection('sftp.juniper.net', username='anonymous', password='anonymous', cnopts=cnopts) as sftp:
            sftp.mkdir(directory)
    except:
        pass


def ftp_copy_file(jtc, filename):
    print('{0} - JTAC FTP file PUT {1}'.format(_get_time(), filename))
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection('sftp.juniper.net', username='anonymous', password='anonymous', cnopts=cnopts) as sftp:
        with sftp.cd('pub/incoming/{0}'.format(jtc)):
            sftp.put(filename)


if __name__ == '__main__':
    print('=========================================')
    print('===   Gene Gaddy gene.gaddy@ibm.com   ===')
    print('=== IBM Cloud: Datacenter Engineering ===')
    print('===   jtac-autoget-support.py v{0}    ==='.format(_version))
    print('=========================================')
    usr = str(raw_input('= Username: '))
    pwd = getpass('= Password: ')
    rtr = str(raw_input('= Router: ')).lower().strip(' ')
    jtc = str(raw_input('= JTAC Case(ex. 2016-1207-0728): ')).strip(' ')
    # if junos quit and log (depedent on netmiko updating SNMPDetect)
    # exit_not_junos(rtr)
    # get netmiko handler
    handler = get_connecthandler(rtr, usr, pwd)
    handler.timeout = 600
    # generate filenames
    filename_rsi = generate_filename('rsi', jtc, rtr)
    filename_rsi_short = filename_rsi.split('/')[3]
    filename_varlog = generate_filename('varlog', jtc, rtr)
    filename_varlog_short = filename_varlog.split('/')[3]
    # start log
    # with open('/var/log/jtac-autoget-support/jtac-autoget-support.log','a') as f:
    #    f.write('{0} - jtac-autoget-support.py starting - {1} {2} {3}\n'.format(_get_time(),getuser(),rtr,jtc))
    # create tar.gz varlog
    make_varlog(handler, filename_varlog)
    # create rsi log file
    make_rsi(handler)
    # compress rsi
    compress_rsi(handler, filename_rsi)
    # copy files here
    scp_file_here(filename_rsi, rtr, usr, pwd)
    scp_file_here(filename_varlog, rtr, usr, pwd)
    # clean up tar.gz files on router
    delete_file_router(handler, filename_rsi)
    delete_file_router(handler, filename_varlog)
    # this creates the JTAC SFTP case directory
    ftp_make_directory(jtc)
    # this does FTP PUT with the RSI archive
    ftp_copy_file(jtc, filename_rsi_short)
    # this does FTP PUT with the /var/log/* archive
    ftp_copy_file(jtc, filename_varlog_short)
    # clean up files
    remove(filename_rsi_short)
    remove(filename_varlog_short)
    # complete log
    # with open('/var/log/jtac-autoget-support/jtac-autoget-support.log','a') as f:
    #    f.write('{0} - jtac-autoget-support.py complete - {1} {2} {3}\n'.format(_get_time(),getuser(),rtr,jtc))

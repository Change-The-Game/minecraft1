#!/usr/bin/env python
# coding=utf-8

# This script will check for a minecraft update from the official site and attempt to install it.

import sys
import os
import time
import subprocess
import re
import pprint
import json
import requests
#import pipes


#
# Module routines
#

def main(argv):
    # Detect installed version
    versioninfo = getInstalledVersion()

    if not versioninfo['valid']:
        log('Cannot detect installed server version.')
        return 1

    log('Installed server version: ' + versioninfo['version'])

    # Check for newer version
    pubversioninfo = getPublicVersion()

    if not pubversioninfo['valid']:
        log('Cannot detect public server version: ' + pubversioninfo['error'])
        return 1

    log('Public server version: ' + pubversioninfo['version'])

    # Update server
    if versioninfo['version'] != pubversioninfo['version']:
        log('Updating to newer version.')
        ok = updateServer(versioninfo['version'], pubversioninfo['version'], pubversioninfo['download_url'])
        if ok:
            log('Server updated.')
        else:
            log('Unable to update server.')
    else:
        log('No update needed.')

    return 0


def getInstalledVersion():
    versioninfo = {'valid': False, 'version': '0.0'}

    line_list = fileGetLines('minecraft_server_version')
    if len(line_list) > 0:
        versioninfo['valid'] = True
        versioninfo['version'] = line_list[0].strip()

    return versioninfo


def getPublicVersion():
    versioninfo = {'valid': False, 'version': '0.0', 'download_url': '', 'error': 'Unknown error.'}

    # Get Version info
    response = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json')
    manifest = json.loads(response.text)

    # Set data from version info
    versioninfo['version'] = manifest['latest']['release']

    # Search for the release
    for vers in manifest['versions']:
        if vers['id'] == versioninfo['version']:
            # Grab release data
            response = requests.get(vers['url'])
            release = json.loads(response.text)
            versioninfo['download_url'] = release['downloads']['server']['url']
            versioninfo['version'] = versioninfo['version']
            versioninfo['valid'] = True
            break

    # Fail gracefully
    if versioninfo['download_url'] == '':
        versioninfo['error'] = 'Failed to find the release data for ' + versioninfo['version']

    return versioninfo


def updateServer(old_version, new_version, download_url):
    shellExecute("rm -f update.jar")
    shellExecute("wget -T 300 -O update.jar '" + download_url + "'")

    file_size = 0
    try:
        file_size = os.path.getsize('update.jar')
    except Exception:
        pass

    if file_size < (1024 * 1024):
        # download failed or file is less than 1MB, something went wrong
        return False

    shellExecute("rm -f 'minecraft_server_" + old_version + ".jar'")
    shellExecute("mv minecraft_server.jar 'minecraft_server_" + old_version + ".jar'")
    shellExecute("rm -f minecraft_server.jar")
    shellExecute("mv update.jar minecraft_server.jar")
    shellExecute("echo '" + new_version + "' > minecraft_server_version")

    return True


#
# Utility routines
#

def shellExecute(command, wait_EOF = True):
    line_list = []

    try:
        text = ''
        if (wait_EOF):
            p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            output = p.communicate()
            text = output[0].decode('utf-8')
        else:
            p = subprocess.Popen(command, shell=True)
            p.communicate()

        text = text.rstrip('\n')
        line_list = text.split('\n')

    except Exception:
        pass

    return line_list

def log(message):
    print(time.strftime('%Y-%m-%d %H:%M:%S') + ': ' + message)
    sys.stdout.flush()
    return

def fileGetLines(filename):
    line_list = []

    text = ''
    try:
        with open(filename, 'r') as file:
            text = file.read()
    except Exception:
        pass

    text = text.replace('\r\n', '\n')
    line_list = text.split('\n')

    return line_list


#
# Script logic
#

if __name__ == '__main__':
    sys.exit(main(sys.argv))

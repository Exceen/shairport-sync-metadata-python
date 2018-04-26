#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import binascii
import codecs
import json
import logging
import math
import re
import sys

from shairport_sync_metadata import reader
from shairport_sync_metadata import decoder
from shairport_sync_metadata.metadata import TrackInfo


# set up logging to file
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='/run/user/1000/output_text.log',
                    filemode='w')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)

logger.info('testing')


def start_item(line):
    regex = r"<item><type>(([A-Fa-f0-9]{2}){4})</type><code>(([A-Fa-f0-9]{2}){4})</code><length>(\d*)</length>"
    matches = re.findall(regex, line)
    #print(matches)
    # python2 only # typ = matches[0][0].decode('hex')
    # python2 only # code = matches[0][2].decode('hex')
    #typ = codecs.decode(matches[0][0], 'hex').decode()
    #code = codecs.decode(matches[0][2], 'hex').decode()
    #typ = base64.b16decode(matches[0][0], casefold=True).decode()
    #code = base64.b16decode(matches[0][2], casefold=True).decode()
    typ = str(binascii.unhexlify(matches[0][0]), 'ascii')
    code = str(binascii.unhexlify(matches[0][2]), 'ascii')
    length = int(matches[0][4])
    return (typ, code, length)

def start_data(line):
    # logger.debug(line)
    try:
        assert line == '<data encoding="base64">\n'
    except AssertionError:
        if line.startswith("<data"):
            return 0
        return -1
    return 0

def read_data(line, length):
    # convert to base64 size
    b64size = 4*math.ceil((length)/3) ;
    #if length < 100: print (line, end="")
    try:
        data = base64.b64decode(line[:b64size])
        # if length < 100: print (data)
        data = data.decode()
    except TypeError:
        data = ""
        pass
    except UnicodeDecodeError:
        data = ""
        pass
    return data

def guessImageMime(magic):

    if magic.startswith('\xff\xd8'):
        return 'image/jpeg'
    elif magic.startswith('\x89PNG\r\n\x1a\r'):
        return 'image/png'
    else:
        return "image/jpg"

# cat /tmp/shairport-sync-metadata | /usr/bin/python3 ./output_text.py
if __name__ == "__main__":

    metadata = {}
    fi = sys.stdin
    while True:
        line = sys.stdin.readline()
        if not line:    #EOF
            break
        #print(line, end="")
        sys.stdout.flush()
        if not line.startswith("<item>"):
            continue
        typ, code, length = start_item(line)
        #print (typ, code, length)

        data = ""
        if (length > 0):
            line2 = fi.readline()
            #print('line2:{}'.format(line2), end="")
            r = start_data(line2)
            if (r == -1):
                continue
            line3 = fi.readline()
            #print('line3:{}'.format(line3), end="")
            data = read_data(line3, length)

        # Everything read
        if (typ == 'core'):
            #logger.debug(code)
            #logger.debug(data)

            if (code == "asal"):
                metadata['songalbum'] = data
                print(data)
            elif (code == "asar"):
                metadata['songartist'] = data
            #elif (code == "ascm"):
            #    metadata['Comment'] = data
            #elif (code == "asgn"):
            #    metadata['Genre'] = data
            elif (code == "minm"):
                metadata['itemname'] = data
            #elif (code == "ascp"):
            #    metadata['Composer'] = data
            #elif (code == "asdt"):
            #    metadata['File Kind'] = data
            #elif (code == "assn"):
            #    metadata['Sort as'] = data
            #elif (code == "clip"):
            #    metadata['IP'] = data

        if (typ == "ssnc" and code == "pfls"):
            metadata = {}
            print (json.dumps({}))
            sys.stdout.flush()
        if (typ == "ssnc" and code == "pend"):
            metadata = {}
            print (json.dumps({}))
            sys.stdout.flush()
        if (typ == "ssnc" and code == "PICT"):
            if (len(data) == 0):
                print (json.dumps({"image": ""}))
            else:
                mime = guessImageMime(data)
                #print (json.dumps({"image": "data:" + mime + ";base64," + base64.b64encode(data)}))
                print (json.dumps({"image": "data:" + mime + ";base64,"}))
            sys.stdout.flush()
        if (typ == "ssnc" and code == "mden"):
            logger.debug('metadata end')
            print (json.dumps(metadata))
            sys.stdout.flush()
            metadata = {}

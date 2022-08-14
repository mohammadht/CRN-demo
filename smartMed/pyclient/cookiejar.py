#!/usr/bin/env python3

# Copyright 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------
'''
Command line interface for cookiejar TF.
Parses command line arguments and passes to the CookieJarClient class
to process.
'''

import argparse
import logging
import os
import sys
import traceback

from colorlog import ColoredFormatter
from cookiejar_client import CookieJarClient

KEY_NAME = 'mycookiejar'

# hard-coded for simplicity (otherwise get the URL from the args in main):
DEFAULT_URL = 'http://localhost:8008'
# For Docker:
# DEFAULT_URL = 'http://rest-api:8008'

def create_console_handler(verbose_level):
    '''Setup console logging.'''
    del verbose_level # unused
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })

    clog.setFormatter(formatter)
    clog.setLevel(logging.DEBUG)
    return clog

def setup_loggers(verbose_level):
    '''Setup logging.'''
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))

def create_parser(prog_name):
    '''Create the command line argument parser for the cookiejar CLI.'''
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)

    parser = argparse.ArgumentParser(
        description='Provides subcommands to manage your simple cookie baker',
        parents=[parent_parser])

    subparsers = parser.add_subparsers(title='subcommands', dest='command')
    subparsers.required = True

    bake_subparser = subparsers.add_parser('bake',
                                           help='bake some cookies',
                                           parents=[parent_parser])
    bake_subparser.add_argument('amount',
                                type=int,
                                help='the number of cookies to bake')
    find_subparser = subparsers.add_parser('find',
                                           help='find the list of DSs with color tag',
                                           parents=[parent_parser])                                           
    find_subparser.add_argument('color',
                                type=str,
                                help='the color to be found')
    find_subparser.add_argument('--qid',
                               type=int,
                               help='query id of the request')
    list_subparser = subparsers.add_parser('list',
                                           help='display all of the query results',
                                           parents=[parent_parser])
    interested_subparser = subparsers.add_parser('interested',
                                           help='The DS shows its interest to the query',
                                           parents=[parent_parser])
    interested_subparser.add_argument('--dsid',
                                type=str,
                                help='the ID of the DS that is going to answer the query')
    interested_subparser.add_argument('--qid',
                                type=int,
                                help='the ID of the query needed to be answered')
    interested_subparser.add_argument('status',
                                type=str,
                                help='YES/NO response from the DS')
    delete_subparser = subparsers.add_parser('delete',
                                          help='delete a registered query',
                                          parents=[parent_parser])
    delete_subparser.add_argument('qid',
                               type=int,
                               help='Query ID of the one that is going to be deleted')                                                                                                                                                                                                                                      
    eat_subparser = subparsers.add_parser('eat',
                                          help='eat some cookies',
                                          parents=[parent_parser])
    eat_subparser.add_argument('amount',
                               type=int,
                               help='the number of cookies to eat')
    subparsers.add_parser('count',
                          help='show number of cookies in ' +
                          'the cookie jar',
                          parents=[parent_parser])
						  
    clear_subparser = subparsers.add_parser('clear',
                                           help='empties cookie jar',
                                           parents=[parent_parser])					  
						  
    return parser

def _get_private_keyfile(key_name):
    '''Get the private key for key_name.'''
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")
    return '{}/{}.priv'.format(key_dir, key_name)

def do_bake(args):
    '''Subcommand to bake cookies.  Calls client class to do the baking.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = CookieJarClient(base_url=DEFAULT_URL, key_file=privkeyfile)
    response = client.bake(args.amount)
    print("Bake Response: {}".format(response))

def do_find(args):
    '''Subcommand to find a list of DSs with associated color. Calls client class to do the finding.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = CookieJarClient(base_url=DEFAULT_URL, key_file=privkeyfile)
    response = client.find(args.color,args.qid)
    print("Find Response: {}".format(response))

def do_interested(args):
    '''Subcommand to show the interest of the DS to a query. Calls client class to do the interest.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = CookieJarClient(base_url=DEFAULT_URL, key_file=privkeyfile)
    data = client.get_query(args.qid)
    if data is not None:
        qid, ds1, ds2, ds3, ds4, ds5 = data.decode().split(",")
    response = client.interested(args.dsid,args.qid,args.status,ds1,ds2,ds3,ds4,ds5)
    print("Find Response: {}".format(response))    

def do_list():
    '''Subcommand to show the list of query results.  Calls client class to do the showing.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = CookieJarClient(base_url=DEFAULT_URL, key_file=privkeyfile)
    query_list = [
        tx.split(',')
        for txs in client.list()
        for tx in txs.decode().split('|')
    ]
    if query_list is not None:
        count = 0;
        for tx_data in query_list:
            count = count + 1;
            qid, ds1, ds2, ds3, ds4, ds5 = tx_data
            print(str(count) + ") Query ID:"+ qid, \
                "| DS1:"+ ds1, \
                "| DS2:"+ ds2, \
                "| DS3:"+ ds3, \
                "| DS4:"+ ds4, \
                "| DS5:"+ ds5)
    else:
        raise Exception("Transaction data not found")            

def do_eat(args):
    '''Subcommand to eat cookies.  Calls client class to do the eating.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = CookieJarClient(base_url=DEFAULT_URL, key_file=privkeyfile)
    response = client.eat(args.amount)
    print("Eat Response: {}".format(response))

def do_delete(args):
    '''Subcommand to delete a query.  Calls client class to do the deleting.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = CookieJarClient(base_url=DEFAULT_URL, key_file=privkeyfile)
    response = client.delete(args.qid)
    print("delete Response: {}".format(response))    

def do_count():
    '''Subcommand to count cookies.  Calls client class to do the counting.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = CookieJarClient(base_url=DEFAULT_URL, key_file=privkeyfile)
    data = client.count()
    if data is not None:
        print("\nThe cookie jar has {} cookies.\n".format(data.decode()))
    else:
        raise Exception("Cookie jar data not found")
		
def do_clear():
    '''Subcommand to empty cookie jar. Calls client class to do the clearing.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = CookieJarClient(base_url=DEFAULT_URL, key_file=privkeyfile)
    response = client.clear()
    print("Clear Response: {}".format(response))

def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    '''Entry point function for the client CLI.'''
    try:
        if args is None:
            args = sys.argv[1:]
        parser = create_parser(prog_name)
        args = parser.parse_args(args)
        verbose_level = 0
        setup_loggers(verbose_level=verbose_level)

        # Get the commands from cli args and call corresponding handlers
        if args.command == 'bake':
            do_bake(args)
        elif args.command == 'eat':
            do_eat(args)
        elif args.command == 'find':
            do_find(args)
        elif args.command == 'interested':
            do_interested(args)
        elif args.command == 'delete':
            do_delete(args)        
        elif args.command == 'list':
            do_list()                   
        elif args.command == 'count':
            do_count()
        elif args.command == 'clear':
            do_clear()	
        else:
            raise Exception("Invalid command: {}".format(args.command))

    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

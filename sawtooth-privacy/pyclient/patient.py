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
Command line interface for patient TF.
Parses command line arguments and passes to the patientClient class
to process.
'''
#writtne by MH
import argparse
from ast import arguments
import logging
import os
import sys
import traceback

from colorlog import ColoredFormatter
from patient_client import PatientClient

KEY_NAME = 'mypatient'

# hard-coded for simplicity (otherwise get the URL from the args in main):
DEFAULT_URL = 'http://localhost:8008'
# For Docker:
#DEFAULT_URL = 'http://rest-api:8008'

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
    '''Create the command line argument parser for the patient CLI.'''
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)

    parser = argparse.ArgumentParser(
        description='Provides subcommands to manage your patient privacy operations',
        parents=[parent_parser])

    subparsers = parser.add_subparsers(title='subcommands', dest='command')
    subparsers.required = True

    register_subparser = subparsers.add_parser('register',
                                           help='register a patient',
                                           parents=[parent_parser])
    register_subparser.add_argument('--uid',
                                type=int,
                                help='user id of the patient')
    register_subparser.add_argument('--psid',
                                type=int,
                                help='privacy signal id of the patient')
    register_subparser.add_argument('status',
                                type=str,
                                help='an operation on the patient')                                                        
    honor_subparser = subparsers.add_parser('honor',
                                          help='honor a transaction',
                                          parents=[parent_parser])
    honor_subparser.add_argument('--uid',
                               type=int,
                               help='user id of the patient')
    honor_subparser.add_argument('--psid',
                               type=int,
                               help='privacy signal id of the patient')                                                      
    show_subparser = subparsers.add_parser('show',
                          help='display information of a registered data',
                          parents=[parent_parser])
    show_subparser.add_argument('--uid',
                               type=int,
                               help='user id of the patient')
    show_subparser.add_argument('--psid',
                               type=int,
                               help='privacy signal id of the patient')
    list_subparser = subparsers.add_parser('list',
                                           help='display information of all registered data',
                                           parents=[parent_parser])                                                    					  
    delete_subparser = subparsers.add_parser('delete',
                                           help='delete a registered data',
                                           parents=[parent_parser])
    delete_subparser.add_argument('--uid',
                               type=int,
                               help='user id of the patient')
    delete_subparser.add_argument('--psid',
                               type=int,
                               help='privacy signal id of the patient')                                           					  
						  
    return parser

def _get_private_keyfile(key_name):
    '''Get the private key for key_name.'''
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")
    return '{}/{}.priv'.format(key_dir, key_name)

def do_register(args):
    '''Subcommand to register a patient.  Calls client class to do the registering.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = PatientClient(base_url=DEFAULT_URL, key_file=privkeyfile, arguments = args)
    response = client.register(args.uid,args.psid,args.status)
    print("Register Response: {}".format(response))

def do_honor(args):
    '''Subcommand to honor status.  Calls client class to do the honoring.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = PatientClient(base_url=DEFAULT_URL, key_file=privkeyfile, arguments = args)
    response = client.eat(args.amount)
    print("Honor Response: {}".format(response))

def do_show(args):
    '''Subcommand to show the transaction info.  Calls client class to do the showing.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = PatientClient(base_url=DEFAULT_URL, key_file=privkeyfile, arguments = args)
    data = client.show(args.uid, args.psid)
    if data is not None:
        print("\nThe registered info: {} \n".format(data.decode()))
    else:
        raise Exception("Transaction data not found")

def do_list():
    '''Subcommand to show the transaction info.  Calls client class to do the showing.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = PatientClient(base_url=DEFAULT_URL, key_file=privkeyfile, arguments = None)
    tx_list = [
        tx.split(',')
        for txs in client.list()
        for tx in txs.decode().split('|')
    ]
    if tx_list is not None:
        count = 0;
        for tx_data in tx_list:
            count = count + 1;
            print(str(count) + ") The registered info: {}".format(tx_data))
    else:
        raise Exception("Transaction data not found")        

def do_delete(args):
    '''Subcommand to delete a registered data. Calls client class to do the deleting.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = PatientClient(base_url=DEFAULT_URL, key_file=privkeyfile, arguments = args)
    response = client.delete(args.uid, args.psid)
    print("Clear Response: {}".format(response))

def do_clear():
    '''Subcommand to empty cookie jar. Calls client class to do the clearing.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = PatientClient(base_url=DEFAULT_URL, key_file=privkeyfile)
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
        if args.command == 'register':
            do_register(args)
        elif args.command == 'honor':
            do_honor(args)
        elif args.command == 'show':
            do_show(args)
        elif args.command == 'list':
            do_list()
        elif args.command == 'delete':
            do_delete(args)                        
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

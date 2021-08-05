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
Command line interface for calculator TF.
Parses command line arguments and passes to the CalculatorClient class
to process.
'''

import argparse
import logging
import os
import sys
import traceback

from colorlog import ColoredFormatter
from calculator_client import CalculatorClient

KEY_NAME = 'mycalculator'

# hard-coded for simplicity (otherwise get the URL from the args in main):
#DEFAULT_URL = 'http://localhost:8008'
# For Docker:
DEFAULT_URL = 'http://rest-api:8008'

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
    '''Create the command line argument parser for the calculator CLI.'''
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)

    parser = argparse.ArgumentParser(
        description='Provides subcommands to manage your simple calculator',
        parents=[parent_parser])

    subparsers = parser.add_subparsers(title='subcommands', dest='command')
    subparsers.required = True

    add_subparser = subparsers.add_parser('add',
                                           help='add to the result',
                                           parents=[parent_parser])
    add_subparser.add_argument('amount',
                                type=int,
                                help='the number to be added to the previous result')
    mul_subparser = subparsers.add_parser('mul',
                                           help='multiply by the result',
                                           parents=[parent_parser])
    mul_subparser.add_argument('amount',
                                type=int,
                                help='the number to be multiplied by the previous result')
    sub_subparser = subparsers.add_parser('sub',
                                          help='subtract from the result',
                                          parents=[parent_parser])
    sub_subparser.add_argument('amount',
                               type=int,
                               help='the number to be subtracted from the previous result')
   
    div_subparser = subparsers.add_parser('div',
                                           help='div the result',
                                           parents=[parent_parser])
    div_subparser.add_argument('amount',
                                type=int,
                                help='the number the previous result is divided by')


    subparsers.add_parser('show',
                          help='show the result',
                          parents=[parent_parser])

    clear_subparser = subparsers.add_parser('clear',
                                           help='clear the calculator',
                                           parents=[parent_parser])					  
						  
    return parser

def _get_private_keyfile(key_name):
    '''Get the private key for key_name.'''
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")
    return '{}/{}.priv'.format(key_dir, key_name)

def do_add(args):
    '''Subcommand to addition.  Calls client class to do the addition.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = CalculatorClient(base_url=DEFAULT_URL, key_file=privkeyfile)
    response = client.add(args.amount)
    print("Addition Response: {}".format(response))

def do_mul(args):
    '''Subcommand to multiplication. Calls client class to do the multiplication.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = CalculatorClient(base_url=DEFAULT_URL, key_file=privkeyfile)
    response = client.mul(args.amount)
    print("Multiplication Response: {}".format(response))

def do_sub(args):
    '''Subcommand to subtraction.  Calls client class to do the subtraction.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = CalculatorClient(base_url=DEFAULT_URL, key_file=privkeyfile)
    response = client.sub(args.amount)
    print("Subtraction Response: {}".format(response))

def do_div(args):
    '''Subcommand to division. Calls client class to do the division.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = CalculatorClient(base_url=DEFAULT_URL, key_file=privkeyfile)
    response = client.div(args.amount)
    print("Division Response: {}".format(response))

def do_show():
    '''Subcommand to show the result.  Calls client class to do the showing.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = CalculatorClient(base_url=DEFAULT_URL, key_file=privkeyfile)
    data = client.show()
    if data is not None:
        print("\nThe result is {}.\n".format(data.decode()))
    else:
        raise Exception("Calculator data not found")
		
def do_clear():
    '''Subcommand to clear the calculator. Calls client class to do the clearing.'''
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = CalculatorClient(base_url=DEFAULT_URL, key_file=privkeyfile)
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
        if args.command == 'add':
            do_add(args)
        elif args.command == 'mul':
            do_mul(args)    
        elif args.command == 'sub':
            do_sub(args)
        elif args.command == 'div':
            do_div(args)
        elif args.command == 'show':
            do_show()
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

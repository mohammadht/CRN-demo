#!/usr/bin/env python3

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
CookieJarTransactionHandler class interfaces for cookiejar Transaction Family.
'''

import traceback
import sys
import hashlib
import logging

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.core import TransactionProcessor

from datetime import datetime

# hard-coded for simplicity (otherwise get the URL from the args in main):
DEFAULT_URL = 'tcp://localhost:4004'
# For Docker:
#DEFAULT_URL = 'tcp://validator:4004'

LOGGER = logging.getLogger(__name__)

FAMILY_NAME = "patient"
# TF Prefix is first 6 characters of SHA-512("cookiejar"), a4d219

def _hash(data):
    '''Compute the SHA-512 hash and return the result as hex characters.'''
    return hashlib.sha512(data).hexdigest()

def _get_patient_address(uid, psid):
    '''
    Return the address of a patient object from the patient TF.

    The address is the first 6 hex characters from the hash SHA-512(TF name),
    plus the result of the hash SHA-512(patient public key).
    '''
    return _hash(FAMILY_NAME.encode('utf-8'))[0:6] + \
                 _hash(uid.encode('utf-8'))[0:32] + _hash(psid.encode('utf-8'))[0:32]


class PatientTransactionHandler(TransactionHandler):
    '''
    Transaction Processor class for the patient Transaction Family.

    This TP communicates with the Validator using the accept/get/set functions.
    This implements functions to "register" or "eat" patients.
    '''
    def __init__(self, namespace_prefix):
        '''Initialize the transaction handler class.

           This is setting the "patient" TF namespace prefix.
        '''
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        '''Return Transaction Family name string.'''
        return FAMILY_NAME

    @property
    def family_versions(self):
        '''Return Transaction Family version string.'''
        return ['1.0']

    @property
    def namespaces(self):
        '''Return Transaction Family namespace 6-character prefix.'''
        return [self._namespace_prefix]
        

    def apply(self, transaction, context):
        '''This implements the apply function for the TransactionHandler class.

           The apply function does most of the work for this class by
           processing a transaction for the patient transaction family.
        '''

        # Get the payload and extract the patient-specific information.
        # It has already been converted from Base64, but needs deserializing.
        # It was serialized with CSV: action, value
        header = transaction.header
        payload_list = transaction.payload.decode().split(",")
        action = payload_list[0]
        uid = payload_list[1]
        psid = payload_list[2]
        status = payload_list[3]

        # Get the signer's public key, sent in the header from the client.
        from_key = header.signer_public_key

        # Perform the action.
        LOGGER.info("Action = %s.", action)
        LOGGER.info("UID = %s.", uid)
        LOGGER.info("PSID = %s.", psid)
        LOGGER.info("Status = %s.", status)
        if action == "register":
            self._make_register(context, uid, psid, status, from_key)
        elif action == "delete":
            self._make_delete(context, uid, psid)
        elif action == "clear":
            self._empty_cookie_jar(context, uid, from_key)
        else:
            LOGGER.info("Unhandled action. Action should be register or delete")

    @classmethod
    def _make_register(cls, context, uid, psid, status, from_key):
        '''Register (add) a transaction with uid, psid, and status.'''
        patient_address = _get_patient_address(uid,psid)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        LOGGER.info('Got the key %s and the patient address %s.',
                    from_key, patient_address)
#      state_entries = context.get_state([patient_address])
        transaction_field = [uid,psid,status,0,0,dt_string]

        state_data = str(transaction_field).encode('utf-8')
        addresses = context.set_state({patient_address: state_data})

        if len(addresses) < 1:
            raise InternalError("State Error")
        context.add_event(
            event_type="cookiejar/bake",
            attributes=[("cookies-baked", uid)])

    @classmethod
    def _make_delete(self, cls, context, uid, psid):
        '''delete a registered data with a specific uid and psid.'''
        patient_address = _get_patient_address(uid,psid)
        LOGGER.info('Got the patient address %s.',
                    patient_address)

        context.delete_state([patient_address])
        self._address_cache[patient_address] = None

    @classmethod
    def _empty_cookie_jar(cls, context, amount, from_key):
        cookie_jar_address = _get_patient_address(from_key)
        LOGGER.info("fetched key %s and state address %s", from_key, cookie_jar_address)
        state_entries = context.get_state([cookie_jar_address])
        if state_entries == []:
            LOGGER.info('No cookie jar with the key %s.', from_key)
            return
        else:
            state_data = str(0).encode('utf-8')
            addresses = context.set_state(
                {cookie_jar_address: state_data})

        if len(addresses) < 1:
            raise InternalError("State update Error")
        LOGGER.info("SET global state success")

def main():
    '''Entry-point function for the patient Transaction Processor.'''
    try:
        # Setup logging for this class.
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)

        # Register the Transaction Handler and start it.
        processor = TransactionProcessor(url=DEFAULT_URL)
        sw_namespace = _hash(FAMILY_NAME.encode('utf-8'))[0:6]
        handler = PatientTransactionHandler(sw_namespace)
        processor.add_handler(handler)
        processor.start()
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

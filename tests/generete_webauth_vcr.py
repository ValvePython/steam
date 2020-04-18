from __future__ import print_function
import re
import os
import sys

filepath = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.abspath(os.path.join(filepath, '..'))
os.chdir(rootdir)
sys.path.insert(0, rootdir)

from getpass import getpass
import json
import mock
import vcr
import requests

from steam import webauth as wa

try:
    _input = raw_input
except:
    _input = input

# personal info scrubbers
# -----------------------
# The recorded vcr is anonymized and should not contain
# any personal info. MAKE SURE TO CHECK THE VCR BEFORE COMMIT TO REPO

def request_scrubber(r):
    r.headers.pop('Cookie', None)
    r.headers['Accept-Encoding'] = 'identity'
    r.body = ''
    return r

def response_scrubber(r):
    r['headers'].pop('date', None)
    r['headers'].pop('expires', None)

    if 'set-cookie' in r['headers'] and 'steamLogin' in ''.join(r['headers']['set-cookie']):
        r['headers']['set-cookie'] = [
            'steamLogin=0%7C%7C{}; path=/; httponly'.format('A'*16),
            'steamLoginSecure=0%7C%7C{}; path=/; httponly; secure'.format('B'*16),
            'steamMachineAuth0={}; path=/; httponly'.format('C'*16),
            ]
    else:
        r['headers'].pop('set-cookie', None)

    if r.get('body', ''):
        data = json.loads(r['body']['string'])

        if 'token_gid' in data:
            data['token_gid'] = 0
        if 'timestamp' in data:
            data['timestamp'] = 12345678
        if 'transfer_parameters' in data:
            data['transfer_parameters']['steamid'] = '0'
            data['transfer_parameters']['token'] = 'A'*16
            data['transfer_parameters']['token_secure'] = 'B'*16
            data['transfer_parameters']['auth'] = 'Z'*16

        body = json.dumps(data)
        r['body']['string'] = body
        r['headers']['content-length'] = [str(len(body))]

        print("--- response ---------")
        print(r)

    return r

anon_vcr = vcr.VCR(
    before_record=request_scrubber,
    before_record_response=response_scrubber,
    serializer='yaml',
    record_mode='new_episodes',
    cassette_library_dir=os.path.join(rootdir, 'vcr'),
)

# scenarios
# -----------------

def user_pass_only():
    print("Please enter a user that can login with just password.")
    u = _input("Username: ")
    p = getpass("Password (no echo): ")

    user_pass_only_success(u, p)
    user_pass_only_fail(u, p + '123')

@anon_vcr.use_cassette('webauth_user_pass_only_success.yaml')
def user_pass_only_success(u, p):
    wa.WebAuth(u, p).login()

@anon_vcr.use_cassette('webauth_user_pass_only_fail.yaml')
def user_pass_only_fail(u, p):
    try:
        wa.WebAuth(u, p).login()
    except wa.LoginIncorrect:
        pass

# run
# -----------------
if __name__ == '__main__':
    user_pass_only()

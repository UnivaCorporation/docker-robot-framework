# Copyright 2008-2018 Univa Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import crypt
import json
import os
import secrets
import string
import subprocess
import time
from logging import getLogger
from typing import List, Tuple, Union
from urllib.parse import urlparse

import bs4
import pam
import requests
import yaml
from oic import rndstr
from oic.oic import Client
from oic.oic.message import RegistrationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD

logger = getLogger(__name__)


class Tortuga:
    """
    A collection of all Tortuga commands.

    """
    def __init__(self, remote=False):
        """
        Initialization.

        :param bool remote: if the library is being run in a remote
                            environment

        """
        self.remote = remote

    def _log(self, level: str, msg: str):
        log_func = getattr(logger, level.lower())
        log_func(msg)

        #
        # If this is running remotely, then we need to spit out log messages
        # using a print statement so they are properly captured
        #
        if self.remote:
            print('{}: {}'.format(level.upper(), msg))

    def wait_for_firstboot(self):
        """
        Waits for tortuga to finish the boot/initialization process.

        """
        while os.path.exists('/.tortuga_firstboot'):
            time.sleep(5)

    def hash_password(self, password: str, escape: bool = True) -> str:
        """
        Creates a password hash, suitable for use in a Linux password file.

        :param str password: the unencrypted password
        :param bool escape:  whether or not to escape the string for use
                             in a command line parameter

        :return str: the password hash

        """
        hash_ = crypt.crypt(password, crypt.mksalt(crypt.METHOD_MD5))

        if escape:
            hash_ = hash_.replace('$', '\$')

        return hash_

    def generate_password(self, length: int = 16) -> Tuple[str, str]:
        """
        Generates a random password, and hash for that password.

        :param int length: the length of the password to generate

        :return Tuple[str, str]: the password, and hash

        """
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(length))

        return password, self.hash_password(password)

    def pam_authenticate(self, username: str, password: str):
        """
        Test user authentication using PAM.

        :param str username: the username to test
        :param str password: the password to test

        :return bool: True if authentication succeeded, False otherwise

        """
        p = pam.pam()

        return p.authenticate(username, password)

    def openid_authenticate(
            self,
            issuer: str,
            client_id: str,
            client_secret: str,
            client_redirect: str,
            username: str,
            password: str,
            ca_bundle: str = '/etc/pki/tls/certs/ca-bundle.crt'):
        #
        # Setup the client
        #
        client = Client(
            client_authn_method=CLIENT_AUTHN_METHOD,
            verify_ssl='/etc/pki/tls/certs/ca-bundle.crt'
        )
        client.provider_config(issuer)
        client_registration = RegistrationResponse(
            client_id=client_id,
            client_secret=client_secret
        )
        client.store_registration_info(client_registration)

        #
        # Get the authentication URL
        #
        args = {
            'client_id': client.client_id,
            'response_type': 'code',
            'scope': ['openid'],
            'nonce': rndstr(),
            'redirect_uri': client_redirect,
            'state': rndstr()
        }
        auth_req = client.construct_AuthorizationRequest(request_args=args)
        auth_url = auth_req.request(client.authorization_endpoint)
        self._log('info', 'Auth URL: {}'.format(auth_url))

        #
        # Get the login page
        #
        resp = requests.get(auth_url, verify=ca_bundle)
        if not resp.status_code == 200:
            raise Exception(
                'Error getting login URL: {}'.format(resp.status_code))

        #
        # Get the login url
        #
        soup = bs4.BeautifulSoup(resp.text, features='html.parser')
        form = soup.form
        if not form:
            raise Exception(
                'Login form not found at URL: {}'.format(resp.url))
        parsed_url = urlparse(resp.url)
        login_url = '{}://{}{}'.format(parsed_url.scheme, parsed_url.netloc,
                                       form['action'])
        self._log('info', 'Login URL: {}'.format(login_url))

        #
        # Login the user
        #
        data = {
            'login': username,
            'password': password
        }
        resp = requests.post(login_url, data=data,
                             verify='/etc/pki/tls/certs/ca-bundle.crt')
        if not resp.status_code == 200:
            raise Exception(
                'Error posting login: {}'.format(resp.status_code))
        if not resp.url.startswith(client_redirect):
            self._log('warning', 'URL: {}'.format(resp.url))
            self._log('warning', resp.text)
            raise Exception('Login failed')

        return True

    def run_command(self, *args: str,
                    exit_code: Union[int, List[int]] = 0) -> str:
        """
        Runs a tortuga CLI command.

        :param args: the command and arguments to provide to the command
        :param int exit_code: the exit code(s) to expect as successful
                              (use a list if more than one is valid)

        :return str: the output of the command

        """
        cmd = ' '.join(args)
        self._log('info', cmd)

        proc = subprocess.run(
            [cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )

        if not isinstance(exit_code, list):
            exit_code = [exit_code]

        if proc.returncode not in exit_code:
            self._log('warning', proc.stdout.decode())
            self._log('warning', proc.stderr.decode())
            raise Exception('Unsuccessful exit code: {}'.format(
                proc.returncode
            ))

        return proc.stdout.decode()

    def parse_file(self, path: str, fmt='json') -> Union[list, dict]:
        """
        Opens, reads, and parses a file, returning the result as a Python
        data structure.

        :param str path: path to the file
        :param str fmt:  format of the file, default is json

        :return Union[list, dict]: parsed data structure

        """
        if not os.path.exists(path):
            raise Exception('File not found: {}'.format(path))

        with open(path) as fp:
            if fmt == 'json':
                return json.load(fp)

            elif fmt == 'yaml':
                return yaml.load(fp)

            else:
                raise Exception('Unsupported file format: {}'.format(fmt))

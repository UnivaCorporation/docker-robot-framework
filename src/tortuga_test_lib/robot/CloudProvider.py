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

import logging
import socket
import time
from typing import Dict, Tuple

from tortuga_test_lib.cloud_provider.base import CloudProviderLauncher
from tortuga_test_lib.cloud_provider.aws import AwsLauncher


logger = logging.getLogger(__name__)


class CloudProvider:
    """
    A RobotFramework library for managing cloud resources.

    """
    providers: Dict[str, CloudProviderLauncher] = {
        'aws': AwsLauncher()
    }

    def _get_launcher(self, provider: str) -> CloudProviderLauncher:
        try:
            return self.providers[provider]

        except KeyError:
            raise Exception('Unsupported provider: {}'.format(provider))

    def launch_vm(self, provider: str, region: str, security_group_id: str,
                  subnet_id: str, image_id: str, instance_type: str,
                  **kwargs) -> Tuple[str, str, str, str]:
        """
        Launches a VM instance.

        :param str provider: key for one of the supported providers
        :param str region:
        :param str security_group_id:
        :param str subnet_id:
        :param str image_id:
        :param str instance_type:
        :param kwargs:

        :return Tuple[str, str, str, str]: a tuple containing the instance id,
                                           the public hostname,
                                           the ssh username, and ssh key path

        """
        launcher = self._get_launcher(provider)

        result = launcher.launch_vm(region, security_group_id, subnet_id,
                                    image_id, instance_type, **kwargs)
        # Wait for the ssh port to be open
        if len(result) == 4 and result[1]:
            self.wait_for_port(result[1], 22, 40)
        return result

    def delete_vm(self, provider: str, region: str, instance_id: str):
        """
        Deletes a VM instance.

        :param str provider:    key for one of the supported providers
        :param str region:
        :param str instance_id:

        """
        launcher = self._get_launcher(provider)
        launcher.delete_vm(region, instance_id)

    def _is_open(self, host: str, port: int) -> bool:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
                s.connect((host, port))
                s.shutdown(socket.SHUT_RDWR)
                return True
        except:
                return False
        finally:
                s.close()

    def wait_for_port(self, host: str, port: int, retries: int) -> bool:
        """
        Waits for a port to be open

        :param str host:    The hostname to check
        :param int port:    The port to check
        :param int retries: How many times to check with 1 second waits in
                            between

        """
        host_open = False
        for i in range(retries):
                if self._is_open(host, port):
                        host_open = True
                        break
                else:
                        time.sleep(1)
        return host_open

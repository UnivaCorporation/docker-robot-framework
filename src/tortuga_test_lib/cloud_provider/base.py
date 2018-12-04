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

from typing import Tuple


class CloudProviderLauncher:
    def launch_vm(self,
                  region: str,
                  security_group_id: str,
                  subnet_id: str,
                  image_id: str,
                  instance_type: str,
                  instance_profile: str,
                  **kwargs) -> Tuple[str, str, str, str]:
        """
        Launches a VM instance.

        :param str region:
        :param str security_group_id:
        :param str subnet_id:
        :param str image_id:
        :param str instance_type:
        :param str instance_profile
        :param kwargs:

        :return Tuple[str, str, str, str]: a tuple containing the instance id,
                                           the public hostname,
                                           the ssh username, and ssh key path

        """
        raise NotImplementedError()

    def delete_vm(self, region: str, instance_id: str):
        """
        Deletes a VM instance.

        :param str region:
        :param str instance_id:

        """
        raise NotImplementedError()

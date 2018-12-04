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
import uuid

import boto3

from .base import CloudProviderLauncher


class AwsLauncher(CloudProviderLauncher):
    def _build_identifier(self) -> str:
        """

        :return:
        """
        return 'tortuga-test-lib-{}'.format(uuid.uuid4())
    
    def launch_vm(self,
                  region: str,
                  security_group_id: str,
                  subnet_id: str,
                  image_id: str,
                  instance_type: str,
                  instance_profile: str,
                  **kwargs) -> Tuple[str, str, str, str]:
        #
        # Build a unique identifier to use as the instance and key pair name
        #
        identifier = self._build_identifier()
        
        ec2 = boto3.resource('ec2', region_name=region)

        #
        # Create the key pair
        #
        private_key = self._create_key_pair(ec2, identifier)

        #
        # Crate the instance
        #
        instance_list = ec2.create_instances(
            IamInstanceProfile={
                'Name' : instance_profile
            },
            ImageId=image_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            KeyName=identifier,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': identifier
                        },
                        {
                            'Key': 'KeyPair',
                            'Value': identifier
                        },
                    ]
                },
            ],
            SubnetId=subnet_id,
            SecurityGroupIds=[
                security_group_id
            ]
        )
        instance = instance_list[0]
        instance.wait_until_running()

        #
        # Re-load the instance so that the public hostname, and other
        # associated data is populated
        #
        instance = ec2.Instance(instance.id)

        return instance.id, instance.public_dns_name, 'centos', private_key

    def _create_key_pair(self, ec2_resource, key_pair_name: str) -> str:
        """
        Generates a key pair, and outputs the private key to the filesystem.

        :param ec2_resource:
        :param key_pair_name:

        :return: the path to the private key

        """
        key_pair = ec2_resource.create_key_pair(KeyName=key_pair_name)
        private_key_path = '/tmp/{}.pem'.format(key_pair_name)

        with open(private_key_path, 'w') as fp:
            fp.write(key_pair.key_material)

        return private_key_path

    def delete_vm(self, region: str, instance_id: str):
        ec2 = boto3.resource('ec2', region_name=region)
        #
        # Get the instance
        #
        instance = ec2.Instance(instance_id)

        #
        # Get the identifier
        #
        key_pair = None
        for tag in instance.tags:
            if tag['Key'] == 'KeyPair':
                key_pair = tag['Value']
                break

        #
        # Terminate the instance
        #
        instance.terminate()
        instance.wait_until_terminated()

        if key_pair:
            self._delete_key_pair(ec2, key_pair)

    def _delete_key_pair(self, ec2_resource, key_pair_name: str):
        """
        Deletes a key pair.

        :param ec2_resource:
        :param key_pair_name:

        """
        key_pair = ec2_resource.KeyPair(key_pair_name)
        key_pair.delete()

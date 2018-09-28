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

from setuptools import setup


VERSION = '1.0.0'


setup(
    name='tortuga-test-lib',
    version=VERSION,
    url='http://univa.com',
    author='Univa Corporation',
    author_email='support@univa.com',
    license='Commercial',
    packages=[
        'tortuga_test_lib',
        'tortuga_test_lib.cloud_provider',
        'tortuga_test_lib.robot',
        'tortuga_test_lib.robot.scripts'
    ],
    package_dir={
        '': 'src'
    },
    install_requires=[
        'boto3',
        'bs4',
        'daemonize',
        'oic',
        'python-pam',
        'pyyaml',
        'robotframework',
        'robotframework-requests',
        'robotframework-sshlibrary',
        'robotremoteserver'
    ],
    entry_points={
        'console_scripts': [
            'start-remote-test-server=tortuga_test_lib.robot.scripts.start_remote_test_server:main',
        ]
    }
)

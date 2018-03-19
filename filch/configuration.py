# Copyright 2017 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import os
import sys

import click
import yaml

from filch import exceptions as peeves


def open_config_file(pathspec):
    with open(pathspec, 'r') as config_file:
        return config_file.read()


def get_config(pathspec=os.path.expanduser('~/.filch.yaml')):
    config = yaml.safe_load(open_config_file(pathspec))
    # check for required settings
    if 'trello' not in config:
        raise peeves.MissingConfigurationSectionException('trello')
    required_trello_settings = ['api_key', 'access_token']
    for setting in required_trello_settings:
        if setting not in config['trello']:
            raise peeves.MissingConfigurationSettingException(setting)
    return config

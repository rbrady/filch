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

from filch import exceptions


def get_config(pathspec=os.path.expanduser('~/.filch.yaml')):
    with open(pathspec, 'r') as config_file:
        config = yaml.safe_load(config_file.read())
        # check for required settings
        if 'trello' not in config:
            click.echo('Trello config section required.')
            raise exceptions.MissingConfigurationSectionException('trello')
        required_trello_settings = ['api_key', 'access_token']
        for setting in required_trello_settings:
            if setting not in config['trello']:
                click.echo(
                    'Missing %s in trello section of config file' % setting)
                raise exceptions.MissingConfigurationSettingException(setting)
        return config

# The MIT License (MIT)
#
# Copyright (c) 2016 Ryan Brady <ryan@ryanbrady.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os
import sys

import click
import requests
from trello import trelloclient

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


def get_config_info():
    config_path = os.environ.get('FILCH_CONFIG',
                                 os.path.expanduser('~/.filch.conf'))
    config = configparser.SafeConfigParser()
    if not config.read(config_path):
        click.echo('Failed to parse config file {}.'.format(config_path))
        sys.exit(1)
    if not config.has_section('trello'):
        click.echo('Config file does not contain section [trello].')
        sys.exit(1)
    trello_data = dict(config.items('trello'))
    required_settings = ['api_key', 'access_token']
    for setting in required_settings:
        if setting not in trello_data:
            click.echo(
                'Config file requires a setting for {setting}'
                ' in section [trello].'.format(setting)
            )
            sys.exit(1)
    return trello_data


def create_trello_card(api_key, access_token, board_name, card_name, card_desc,
                       card_labels=[], card_due="null", list_name='New'):

    trello_api = trelloclient.TrelloClient(api_key=api_key, token=access_token)
    board = [b for b in trello_api.list_boards()
             if b.name == board_name][0]
    default_labels = [label for label in board.get_labels()
                      if label.name in card_labels]
    new_list = [trello_list for trello_list in board.open_lists()
                if trello_list.name == list_name][0]
    card_dup = [card for card in new_list.list_cards()
                if card.name == card_name and card.desc == card_desc]
    if not card_dup:
        return new_list.add_card(card_name, card_desc, default_labels, card_due)


def get_blueprint(project, blueprint):
    url = 'https://api.launchpad.net/devel/{project}/+spec/{blueprint}'
    r = requests.get(
        url.format(project=project, blueprint=blueprint))
    return r.json()


def get_launchpad_bug(bug_id):
    url = 'https://api.launchpad.net/devel/bugs/%s'
    r = requests.get(url % bug_id)
    return r.json()


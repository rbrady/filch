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
#!/usr/bin/env python
import click
import os
from pprint import pprint
import sys

from filch.external import gerrit
from filch.external import trello

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

CONFIG_PATH = os.environ.get('FILCH_CONFIG',
                             os.path.expanduser('~/.filch.conf'))



@click.command()
@click.argument('change_id')
def import_from_gerrit(change_id):
    config = configparser.SafeConfigParser()
    if not config.read(CONFIG_PATH):
        click.echo('Failed to parse config file {}.'.format(CONFIG_PATH))
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
    change = gerrit.get_gerrit_change(change_id)
    pprint(change)
    # TODO(rbrady): map fields from gerrit change to trello card
    # trello_api = trello.Trello(
    #   trello_data['api_key'], trello_data['api_token'])
    # get board and list ids
    # create card


if __name__ == '__main__':
    import_from_gerrit()

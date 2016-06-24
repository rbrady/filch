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
import sys
import click
from pygerrit.rest import GerritRestAPI

from filch import constants
from filch import helpers


@click.command()
@click.option('--gerrit', '-g', default=None, type=str)
@click.option('--blueprint', '-bp', default=None, type=str)
@click.option('--project', '-p', default=None, type=str)
@click.option('--bug_id', default=None, type=str)
@click.option('--board', '-b', default=None, type=str)
@click.option('--labels', '-l', multiple=True)
@click.option('--list_name', default='New', type=str)
def trello_import(gerrit, blueprint, project, bug_id, board, labels,
                  list_name):
    config = helpers.get_config_info()
    if not board:
        if 'default_board' not in config:
            click.echo("No default_board exists in ~/filch.conf")
            click.echo("You must either set a default_board in ~/filch.conf "
                       "or use the --board_name option.")
            sys.exit(1)
        else:
            board = config['default_board']

    if gerrit:
        gerrit_api = GerritRestAPI(url="https://review.openstack.org", auth=None)
        change = gerrit_api.get("/changes/%s" % gerrit)
        helpers.create_trello_card(
            config['api_key'],
            config['access_token'],
            board,
            change['subject'],
            constants.GERRIT_CARD_DESC.format(**change),
            card_labels=list(labels),
            card_due="null",
            list_name=list_name
        )
        click.echo('You have successfully imported "%s"' % change['subject'])

    if blueprint:
        if not project:
            click.echo('To import a blueprint you must provide a project.')
            sys.exit(1)
        blueprint = helpers.get_blueprint(project, blueprint)
        helpers.create_trello_card(
            config['api_key'],
            config['access_token'],
            board,
            blueprint['title'],
            constants.BLUEPRINT_CARD_DESC.format(**blueprint),
            card_labels=list(labels),
            card_due="null",
            list_name=list_name
        )
        click.echo('You have successfully imported "%s"' % blueprint['title'])

    if bug_id:
        bug = helpers.get_launchpad_bug(bug_id)
        helpers.create_trello_card(
            config['api_key'],
            config['access_token'],
            board,
            bug['title'],
            constants.BUG_CARD_DESC.format(**bug),
            card_labels=list(labels),
            card_due="null",
            list_name=list_name
        )
        click.echo('You have successfully imported "%s"' % bug['title'])

if __name__ == '__main__':
    trello_import()

# The MIT License (MIT)
#
# Copyright (c) 2017 Ryan Brady <ryan@ryanbrady.org>
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

from filch import cards
from filch import configuration
from filch import constants
from filch import utils


@click.command()
@click.argument('service')
@click.option('--id', default=None, type=str, multiple=True)
@click.option('--url', default=None, type=str)
@click.option('--host', default=None, type=str)
@click.option('--user', default=None, type=str)
@click.option('--password', default=None, type=str)
@click.option('--project', '-p', default=None, type=str)
@click.option('--board', '-b', default=None, type=str)
@click.option('--labels', '-l', multiple=True)
@click.option('--list_name', default='New', type=str)
def importer(service, id, url, host, user, password, project, board,
             labels, list_name):
    config = configuration.get_config()
    trello_key = config['trello']['api_key']
    trello_token = config['trello']['access_token']
    if not board:
        if 'default_board' not in config['trello']:
            click.echo("No default_board exists in ~/filch.conf")
            click.echo("You must either set a default_board in ~/filch.conf "
                       "or use the --board_name option.")
            sys.exit(1)
        else:
            board = config['trello']['default_board']

    if service == 'gerrit':
        # default to upstream openstack
        # if host is present then use that
        # if url is present then use that
        gerrit_url = "https://review.openstack.org"
        if host:
            gerrit_url = config['gerrit'][host]['url']
        if url:
            gerrit_url = url

        gerrit_api = GerritRestAPI(url=gerrit_url, auth=None)
        for change_id in list(id):
            change = gerrit_api.get("/changes/%s" % change_id)
            cards.create_card(
                trello_key,
                trello_token,
                board,
                change['subject'],
                constants.GERRIT_CARD_DESC.format(**change),
                card_labels=list(labels),
                card_due="null",
                list_name=list_name
            )
            click.echo(
                'You have successfully imported "%s"' % change['subject'])

    if service == 'blueprint':
        if not project:
            click.echo('To import a blueprint you must provide a project.')
            sys.exit(1)
        for bp_id in list(id):
            blueprint = utils.get_blueprint(project, bp_id)
            card = cards.create_card(
                trello_key,
                trello_token,
                board,
                blueprint['title'],
                constants.BLUEPRINT_CARD_DESC.format(**blueprint),
                card_labels=list(labels),
                card_due="null",
                list_name=list_name
            )
            click.echo(
                'You have successfully imported "%s"' % blueprint['title'])
            if card is not None:
                click.echo(card.url)

    if service == 'bug':
        for bug_id in list(id):
            bug = utils.get_launchpad_bug(bug_id)
            cards.create_card(
                trello_key,
                trello_token,
                board,
                bug['title'],
                constants.BUG_CARD_DESC.format(**bug),
                card_labels=list(labels),
                card_due="null",
                list_name=list_name
            )
            click.echo(
                'You have successfully imported "%s"' % bug['title'])

    if service in ['bz', 'bugzilla']:
        if url:
            # also need user & password.  sslverify is optional
            if not user or not password:
                click.echo("If using a url for Bugzilla, you must also "
                           "provide a user and password.")
                sys.exit(1)

        # if host arg is not used, use first host from
        # configuration as default
        if not host:
            # check to ensure a host for bugzilla exists in config
            if len(config['bugzilla'].keys()) == 0:
                click.echo("No Bugzilla data configuration file.  Please "
                           "add configuration data or pass url, user and "
                           "password arguments.")
                sys.exit(1)
            else:
                host = config['bugzilla'].keys()[0]

        url = config['bugzilla'][host]['url']
        user = config['bugzilla'][host]['user']

        sslverify = config['bugzilla'][host].get('sslverify', True)

        for bz_id in list(id):
            try:
                bug = utils.get_bz(bz_id, url=url, user=user, password=password,
                                   sslverify=sslverify)

                if len(bug.comments) > 0:
                    bug.description = bug.comments[0]['text']

                cards.create_card(
                    trello_key,
                    trello_token,
                    board,
                    bug.summary,
                    constants.BZ_CARD_DESC.format(**bug.__dict__),
                    card_labels=list(labels),
                    card_due="null",
                    list_name=list_name
                )
                click.echo('You have successfully imported "%s"' % bug.summary)
            except Exception as err:
                click.echo(err)

    if service == 'debug':
        ids = list(id)
        print(ids)

if __name__ == '__main__':
    importer()

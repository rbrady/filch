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
import os
import sys

import click
from pygerrit.rest import GerritRestAPI
from trello import trelloclient

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
    try:
        config = configuration.get_config()
    except Exception as err:
        click.echo(err)
        sys.exit(1)

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

    trello_api = trelloclient.TrelloClient(
        api_key=config['trello']['api_key'],
        token=config['trello']['access_token']
    )

    board_obj = [b for b in trello_api.list_boards()
                 if b.name == board][0]

    # ensure labels being used are actually in the board
    card_labels = [label for label in board_obj.get_labels()
                      if label.name in list(labels)]

    # ensure list name exists in board
    board_list = [trello_list for trello_list in board_obj.open_lists()
                if trello_list.name == list_name][0]

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
                board_list,
                change['subject'],
                constants.GERRIT_CARD_DESC.format(**change),
                labels=card_labels,
                due="null",
            )
            click.echo(
                'You have successfully imported "%s"' % change['subject'])

    if service == 'blueprint':
        if not project:
            click.echo('To import a blueprint you must provide a project.')
            sys.exit(1)
        for bp_id in list(id):
            blueprint = utils.get_blueprint(project, bp_id)
            cards.create_card(
                board_list,
                blueprint['title'],
                constants.BLUEPRINT_CARD_DESC.format(**blueprint),
                labels=card_labels,
                due="null",
            )
            click.echo(
                'You have successfully imported "%s"' % blueprint['title'])

    if service == 'bug':
        for bug_id in list(id):
            bug = utils.get_launchpad_bug(bug_id)
            cards.create_card(
                board_list,
                bug['title'],
                constants.BUG_CARD_DESC.format(**bug),
                labels=card_labels,
                due="null",
            )
            click.echo(
                'You have successfully imported "%s"' % bug['title'])

    if service == 'story':
        for story_id in list(id):
            story = utils.get_storyboard_story(story_id)
            cards.create_card(
                board_list,
                story['title'],
                constants.STORY_CARD_DESC.format(**story),
                labels=card_labels,
                due="null",
            )
            click.echo(
                'You have successfully imported "%s"' % story['title'])

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
                host = list(config['bugzilla'].keys())[0]

        url = config['bugzilla'][host]['url']
        user = config['bugzilla'][host]['user']

        sslverify = config['bugzilla'][host].get('sslverify', True)

        for bz_id in list(id):
            try:
                bug = utils.get_bz(bz_id, url=url, user=user, password=password,
                                   sslverify=sslverify)

                if len(bug.comments) > 0:
                    bug.description = bug.comments[0]['text']

                bug_card = cards.create_card(
                    board_list,
                    bug.summary,
                    constants.BZ_CARD_DESC.format(**bug.__dict__),
                    labels=card_labels,
                    due="null",
                )

                # adds comments to a card
                if len(bug.comments) > 1:
                    for comment in bug.comments[1:]:
                        bug_card.comment(constants.COMMENT_TEXT.format(
                            text=comment['text'],
                            author=comment['author'],
                            create_time=comment['creation_time'],
                            is_private=constants.COMMENT_PRIVACY[
                                comment['is_private']
                            ],
                        ))

                # adds external trackers to card
                if len(bug.external_bugs) > 0:
                    external_trackers = []
                    for ext_bug in bug.external_bugs:
                        external_trackers.append(
                            os.path.join(ext_bug['type']['url'],
                                         ext_bug['ext_bz_bug_id'])
                        )
                    bug_card.add_checklist(
                        'External Trackers',
                        external_trackers
                    )

                click.echo('You have successfully imported "%s"' % bug.summary)
            except Exception as err:
                click.echo(err)

    if service == 'debug':
        ids = list(id)
        print(ids)

if __name__ == '__main__':
    importer()

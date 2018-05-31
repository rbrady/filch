# The MIT License (MIT)
#
# Copyright (c) 2018 Ryan Brady <ryan@ryanbrady.org>
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
import collections
import itertools
import json
import os
import sys

import click
from pprint import pprint
import requests

from filch import boards
from filch import configuration
from filch import constants
from filch import data
from filch import exceptions as peeves


@click.command()
@click.argument('board')
def health(board):

    try:
        config = configuration.get_config()
    except Exception as err:
        click.echo(err)
        sys.exit(1)

    board_manager = boards.BoardManager(config['trello'], board)
    duplicates = {}
    no_sources = []

    lists = [item.id for item in board_manager.board.open_lists() if
             item.name != "Meta"]
    cards = [card for card in board_manager.board.all_cards()
             if card.idList in lists]
    sources = list(
        itertools.chain(*[[(field.value, card) for field in card.customFields
                           if field.name == 'source'] for card in cards]))

    counts = collections.Counter([x for (x, y) in sources])
    dups = [(x, y) for (x, y) in counts.most_common() if y > 1]
    dup_urls = [name for (name, url) in dups]

    for source in sources:
        if source[0] == '':
            no_sources.append(source[1])
        else:
            if source[0] in dup_urls:
                if source[0] not in duplicates:
                    duplicates[source[0]] = []
                duplicates[source[0]].append(source[1])

    # display the cards that have more than one instance of the source
    if len(duplicates) > 0:
        click.echo(click.style("Duplicate Cards", bg='red', fg='black'))
        for url, dup_cards in duplicates.iteritems():
            print("%s(%s)" % (url, len(dup_cards)))
            dup_cards.sort(key=lambda x: x.list_labels.count, reverse=True)
            pprint([card_item.shortUrl for card_item in dup_cards[1:]])
    else:
        click.echo(
            click.style(u"\u2713 No Duplicate Cards", bg='green', fg='black'))

    # display the cards without sources
    if len(no_sources) > 0:
        click.echo(click.style("Cards Without Sources", bg='red', fg='black'))
        pprint(no_sources)
    else:
        click.echo(
            click.style(u"\u2713 All Cards Have Source URLs", bg='green', fg='black'))


if __name__ == '__main__':
    health()

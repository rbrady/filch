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
import collections
import pdb

from trello import trelloclient

from filch import constants
from filch import exceptions as peeves
from filch import utils


def get_or_create_board(config, name):
    trello_api = trelloclient.TrelloClient(
        api_key=config['trello']['api_key'],
        token=config['trello']['access_token']
    )
    boards = trello_api.list_boards()
    board_filter = [b for b in boards if b.name == name]
    if len(board_filter) > 0:
        board = board_filter[0]
    else:
        board = trello_api.add_board(name)
        board.open()
    return board


class BoardManager(object):

    def __init__(self, config, name):
        self.config = config
        self.client = self.get_client()
        self.sources = []
        self.board = self._get_board(name)
        if not self.board:
            self.board = self._create_board(name)
        self._initialize_board()

    def get_client(self):
        return trelloclient.TrelloClient(
            api_key=self.config['api_key'],
            token=self.config['access_token']
        )

    def _create_board(self, name):
        """ Creates a Trello Board

        :param name: name of board
        :return:
        """
        board = self.client.add_board(name)
        board.open()
        # clean pre-defined lists
        for item in board.all_lists():
            if item.name in ["To Do", "Doing", "Done"]:
                item.close()
        return board

    def _get_board(self, name):
        """ Gets a reference to a Trello Board

        :param name: name of board
        :return: Trello Board Object
        """
        boards = self.client.list_boards()
        board_filter = [b for b in boards if b.name == name]
        if len(board_filter) > 0:
            return board_filter[0]
        return None

    def add_lists(self, trellolists):
        board_list_names = [l.name for l in self.board.all_lists()]
        # add default lists
        for name in trellolists:
            if name not in board_list_names:
                trellolist = self.board.add_list(name)
                trellolist.open()

    def _initialize_board(self):
        """ Configure board with defaults as needed

        :param board: Trello Board Object
        :return: None
        """
        self.add_lists(['Complete', 'In Progress', 'Features', 'Bugs'])

        # add default labels
        self.add_labels_by_color("black", ["RFE", "Bug"])
        self.add_labels_by_color("red",
                                 ["Untriaged", "Blocked", "CI-Blocked"])

    def add_labels_by_color(self, color, names):
        # The supported colors are yellow, purple, blue, red, green, orange,
        # black, sky, pink, lime, null
        board_labels = collections.defaultdict(list)
        selected_color = color.lower()
        [board_labels[label.color.lower()].append(label.name.lower()) for label
         in self.board.get_labels()]
        for name in names:
            # ensure color is a supported type
            if selected_color.lower() not in constants.SUPPORTED_LABEL_COLORS:
                raise peeves.UnsupportedLabelColorException(selected_color)
            if selected_color not in board_labels:
                print("The color %s is not in the board labels" % color)
                self.board.add_label(name, selected_color)
            elif name.lower() not in board_labels[selected_color]:
                self.board.add_label(name, selected_color)
            else:  # ignore duplicate labels
                pass

    def run(self):

        # get a collection of all cards before adding new cards
        # append any created card to this list of cards to catch
        # any duplicates
        cards = self.board.all_cards()
        lists = collections.defaultdict(list)
        for trellolist in self.board.all_lists():
            lists[trellolist.name] = trellolist
        for source in self.sources:
            results = source.query()
            for color, labels in source.get_labels(results).iteritems():
                self.add_labels_by_color(color, labels)
            board_labels = self.board.get_labels()
            for result in results:
                card_data = source.create_card(result, board_labels)
                # where does this card need to be?
                target_list_name = source.sort_card(result)
                # TODO (rbrady): once custom fields API access becomes public
                # in the trello api, update card creation to add source data
                # custom field and check duplicates against the source data
                # instead of name and description.  Names and descriptions are
                # the same for dup BZ's created to map to different versions.

                card_desc = utils.get_description(card_data['description'])
                card_dups = [card for card in cards
                             if card.name == card_data['name']
                             and card.desc == card_desc]
                if len(card_dups) > 1:
                    card = card_dups[0]
                else:
                    # card does not exist in board
                    # add to specified list for new items
                    # ensure labels being used are actually in the board
                    card_labels = [label for label in board_labels
                                   if label.name in card_data['labels']]
                    card = lists[target_list_name].add_card(
                        card_data['name'],
                        card_desc,
                        card_labels,
                        card_data['date_due'])

                # update a card
                source.update_card(result, card, board_labels)
                # if current card list and target list don't match,
                # move the card to the target list
                if target_list_name != card.get_list().name:
                    # move list
                    card.change_list(lists[target_list_name].id)

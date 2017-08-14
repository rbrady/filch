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
from trello import trelloclient

_MAX_DESC_LEN = 16384


def _get_description(desc):
    l = len(desc)
    if l > _MAX_DESC_LEN:
        desc = desc[l - _MAX_DESC_LEN:]
    return desc


def create_card(api_key, access_token, board_name, card_name, card_desc,
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
        card_desc = _get_description(card_desc)
        return new_list.add_card(card_name, card_desc, default_labels, card_due)

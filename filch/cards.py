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
# NOTICE: (rbrady) This method is deprecated and will be removed on 4/1/2018
_MAX_DESC_LEN = 16384


def mirror_card(source, destination):
    # given two different cards from two different boards
    # mirror the data from the source card to the destination
    # card
    pass

# NOTICE: (rbrady) This method is deprecated and will be removed on 4/1/2018
def _get_description(desc):
    l = len(desc)
    if l > _MAX_DESC_LEN:
        desc = desc[l - _MAX_DESC_LEN:]
    return desc


# NOTICE: (rbrady) This method is deprecated and will be removed on 4/1/2018
def create_card(target_list, title, description, labels=[], due="null"):

    card_dup = [card for card in target_list.list_cards()
                if card.name == title and card.desc == description]
    if not card_dup:
        description = _get_description(description)
        return target_list.add_card(title, description, labels, due)

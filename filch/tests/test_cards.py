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
import mock
import trello

from filch import cards


class TestCards(object):
    def setup_method(self):
        self.mock_list = mock.MagicMock()
        self.mock_list.name = "New"

    def test_create_card(self):
        self.mock_list.list_cards.return_value = []

        cards.create_card(target_list=self.mock_list,
                          title="test_card",
                          description="test_card_desc",
                          labels=["test_label"],
                          due="null")
        self.mock_list.add_card.assert_called_with(
            "test_card", "test_card_desc", ["test_label"], "null")

    def test_create_card_duplicate(self):
        duplicate_card = trello.Card(self.mock_list, None, "test_card")
        duplicate_card.description = "duplicate card"
        self.mock_list.list_cards.return_value = [duplicate_card]

        cards.create_card(target_list=self.mock_list,
                          title="test_card",
                          description="duplicate card",
                          labels=["test_label"],
                          due="null")
        self.mock_list.add_card.assert_not_called()

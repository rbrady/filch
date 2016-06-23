# The MIT License (MIT)
#
# Copyright (c) 2016 James Slagle <james.slagle@gmail.com>
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
import requests


class Trello(object):

    def __init__(self, api_key, api_token):
        self.url = "https://api.trello.com/1/%s"
        self.api_key = api_key
        self.api_token = api_token
        self.payload = dict(key=self.api_key, token=self.api_token)

    def get(self, path):
        r = requests.get(self.url % path, params=self.payload)
        return r.json()

    def put(self, path, payload):
        payload.update(self.payload)
        r = requests.put(self.url % path, params=payload)
        return r.json()

    def post(self, path, payload):
        payload.update(self.payload)
        r = requests.post(self.url % path, params=payload)
        return r.json()

    def get_boards(self):
        return self.get("/member/me/boards")

    def get_board_by_id(self, board_id):
        return [board for board in
                self.get_boards if board['id'] == board_id][0]

    def get_board_by_name(self, name):
        return [board for board in
                self.get_boards if board['name'] == name][0]

    def get_lists(self, board_id):
        return self.get("/boards/%s/lists" % board_id)

    def get_list(self, list_id):
        return self.get("/lists/%s/cards" % list_id)

    def get_card(self, card_id):
        return self.get("/1/cards/%s" % card_id)

    def get_all_cards(self, board_id):
        return self.get("/boards/%s/cards" % board_id)

    def create_card(self, card_data):
        return self.post("/1/cards", card_data)

    def update_card(self, card_id, card_data):
        return self.put("/1/cards/%s" % card_id, card_data)
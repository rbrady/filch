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
import itertools
import json
import os

from launchpadlib.launchpad import Launchpad
import requests
from trello import trelloclient

from filch import constants
from filch import data
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


def add_custom_field(config, board_id, field):
    url = "https://api.trello.com/1/customFields"

    querystring = {
        "key": config['api_key'],
        "token": config['access_token']
    }

    payload = "{\"idModel\":\"5aafc385f26015f1b9f7c372\",\"modelType\":\"board\",\"name\":\"source\",\"type\":\"text\",\"pos\":\"0\"}"
    headers = {'content-type': 'application/json'}

    response = requests.request("POST", url, data=payload, headers=headers,
                                params=querystring)

    print(response.text)


class BoardManager(object):

    def __init__(self, config, name):
        self.config = config
        self.client = self.get_client()
        self.sources = []
        self.board = self._get_board(name)
        if not self.board:
            self.board = self._create_board(name)
        self._initialize_board()
        self.debug = False

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

    def get_plugins(self):
        url = "https://api.trello.com/1/boards/%s/boardPlugins" % self.board.id
        return json.loads(self.client.fetch_json(url, http_method="GET"))

    def enable_plugin(self, plugin_id):
        # this method deviates from using the py-trello library because there is a lack of support for status codes
        # other than 401 or 200.  Coupled with the slow release cadence of py-trello, there's no telling when a
        # contribution would make it into a release.
        url = "https://api.trello.com/1/boards/%s/boardPlugins" % self.board.id

        querystring = {"idPlugin": constants.CUSTOM_FIELDS_PLUGIN_ID, "key": self.config['api_key'],
                       "token":  self.config['access_token']}

        response = requests.request("POST", url, params=querystring)

        if response.status_code == 409:
            # boardPlugin for that association already exists
            # fail silently
            pass
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            raise peeves.APIException(response.status_code, response.reason, response.text)

    def add_custom_field(self, field_name, field_type, pos=0):
        url = "https://api.trello.com/1/customFields"

        payload = {
            'idModel': self.board.id,
            'type': field_type,
            'name': field_name,
            'modelType': 'board',
            'pos': pos,
            "key": self.config['api_key'],
            "token": self.config['access_token']
        }

        response = requests.request("POST", url, params=payload)

        if response.status_code == 409:
            # that association already exists
            # fail silently
            pass
        elif response.status_code == 200:
            return response.text
        else:
            raise peeves.APIException(response.status_code, response.reason, response.text)

    def remove_custom_field(self, field_id):
        url = "https://api.trello.com/1/customfields/%s" % field_id

        payload = {
            "key": self.config['api_key'],
            "token": self.config['access_token']
        }

        response = requests.request("DELETE", url, params=payload)

        if response.status_code == 200:
            return response.text
        else:
            raise peeves.APIException(response.status_code, response.reason, response.text)

    def get_custom_fields(self):
        url = "https://api.trello.com/1/boards/%s/customFields" % self.board.id

        payload = {"key": self.config['api_key'], "token": self.config['access_token']}

        response = requests.request("GET", url, params=payload)

        if response.status_code == 409:
            # that association already exists
            # fail silently
            pass
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            raise peeves.APIException(
                response.status_code, response.reason, response.text)

    def set_custom_field(self, card_id, custom_field_id, value):
        """ Sets a value on a custom field for a card

        The object you pass in as the value should be an object that has a key that matches the type of
        Custom Field that has been designed. For instance, if there is a Custom Field of type number that a value is
        being set for, the data you pass into the body should contain the following: "value": {"number": "3"}.
        """
        url = "https://api.trello.com/1/card/%s/customField/%s/item" % (
            card_id, custom_field_id)

        payload = {"key": self.config['api_key'], "token": self.config['access_token']}
        data = {'value': value}

        response = requests.request("PUT", url, params=payload, json=data)

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise peeves.APIException(
                response.status_code, response.reason, response.text)

    def _get_lists(self):
        lists = collections.defaultdict(list)
        for trellolist in self.board.all_lists():
            lists[trellolist.name] = trellolist
        return lists

    def update_cards(self, config):
        # get reference to only open cards (excludes closed/archived cards)
        cards = self.board.open_cards()
        # get all of the cards that have sources
        source_urls = [[(field.value, card) for field in card.customFields if
                        field.name == 'source'] for card in cards if
                       len(card.customFields) > 0]
        # transform cards with sources into dictionary
        cards_by_source = {k: v for (k, v) in
                           list(itertools.chain(*source_urls))}

        # get list of bugzilla IDs for batch query and update
        bz_ids = [k.split('id=')[1] for k
                  in cards_by_source.keys() if 'bugzilla' in k]

        bug_ids = [k.split("/")[-1] for k in cards_by_source.keys() if 'bugs' in k]

        blueprints = [k for k in cards_by_source.keys() if 'blueprint' in k]

        board_labels = self.board.get_labels()

        lists = self._get_lists()

        # find all of the BZs in the board
        if len(bz_ids) > 0:
            bzs_to_update = data.BugzillaIDSource(
                config['bugzilla']['redhat'],
                id_list=bz_ids,
                include_fields=constants.BZ_INCLUDE_FIELDS,
            )
            bzs = bzs_to_update.query()
            for bz in bzs:
                card = cards_by_source[bz.weburl]
                bzs_to_update.update_card(bz, card, board_labels)
                # where does this card need to be?
                target_list_name = bzs_to_update.sort_card(bz)
                if target_list_name != card.get_list().name:
                    # move list
                    card.change_list(lists[target_list_name].id)

        # find all of the lp bugs in the board
        if len(bug_ids) > 0:
            bugs_source = data.LaunchpadBugIDSource(bug_ids)
            bugs = bugs_source.query()
            for bug in bugs:
                card = cards_by_source[bug.web_link]
                bugs_source.update_card(bug, card, board_labels)
                if target_list_name != card.get_list().name:
                    # move list
                    card.change_list(lists[target_list_name].id)

    def import_cards(self):
        board_fields = self.get_custom_fields()
        source_field_id = [d for d in board_fields
                           if d['name'] == 'source'][0]['id']

        # all cards are retrieved here, because we don't want to add a new card
        # for the same source artifact if we've had it in the board already
        cards = self.board.all_cards()

        # get a list of all the cards for checking duplicates before starting
        # the create/update block
        source_urls = [[(field.value, card) for field in card.customFields
                        if field.name == 'source'] for card in cards]
        cards_by_source = {k: v for (k, v) in
                           list(itertools.chain(*source_urls))}

        for source in self.sources:
            results = source.query()
            for color, labels in source.get_labels(results).iteritems():
                self.add_labels_by_color(color, labels)
            board_labels = self.board.get_labels()

            for result in results:
                card_data = source.create_card(result, board_labels)
                # where does this card need to be?
                target_list_name = source.sort_card(result)

                card_desc = utils.get_description(card_data['description'])

                if card_data.get('source') not in cards_by_source:
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

                    # set source for card
                    # if the board supports the "source" custom field
                    if source_field_id is not None:
                        # check to see if the card source field is set
                        card_fields = {k: v for (k, v) in
                                       [(field.name, field.value) for field in
                                        card.customFields]}
                        card_source = card_fields.get('source')
                        if card_source is None:
                            self.set_custom_field(card.id, source_field_id,
                                                  {'text': card_data['source']})

    def run(self):
        # DEPRECATED
        # TODO(rbrady): Look at changing the strategy here to separate the import
        # and updating of cards.  The imports should query specific sources and
        # provide the results to the create pipeline, based on whether or not the
        # source already exists in a card on the board.

        # Next, the update process should be collecting each card that is on the
        # board and updating it.  We can cache the results from the import query
        # to help speed up the process, but will need to directly query for the
        # remaining cards.  Look to see if there is something that can be done
        # for querying sources via IDs so we cut down on request/response generation.

        board_fields = self.get_custom_fields()
        source_field_id = [d for d in board_fields if d['name'] == 'source'][0]['id']

        # get a collection of all cards before adding new cards
        # append any created card to this list of cards to catch
        # any duplicates
        cards = self.board.all_cards()
        # get a list of all the cards for checking duplicates before starting
        # the create/update block
        source_urls = [[(field.value, card) for field in card.customFields
                        if field.name == 'source'] for card in cards]
        cards_by_source = {k: v for (k, v) in
                           list(itertools.chain(*source_urls))}
        sources_to_process = list(cards_by_source.keys())
        lists = self._get_lists()
        for source in self.sources:
            results = source.query()
            for color, labels in source.get_labels(results).iteritems():
                self.add_labels_by_color(color, labels)
            board_labels = self.board.get_labels()
            # TODO(rbrady): try a strategy where each item from the query is
            # just used to check for cards to be created.  If the result.source
            # is already present in the board, pass.  if the result is not present,
            # then add it to the board.  Once all the cards have been added to
            # the board from the current results, go through each card in the
            # board and run the update method.  For the update method, check for
            # each card source in the query results first (e.g. checking the cache)
            # and if not present then do a single request based on the source url.
            # see if there is a way to do batching of requests per single source
            # of truth
            for result in results:
                card_data = source.create_card(result, board_labels)
                # where does this card need to be?
                target_list_name = source.sort_card(result)

                card_desc = utils.get_description(card_data['description'])

                if card_data.get('source') in cards_by_source:
                    card = cards_by_source.get(card_data.get('source'))
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

                # set source for card
                # if the board supports the "source" custom field
                if source_field_id is not None:
                    # check to see if the card source field is set
                    card_fields = {k: v for (k, v) in
                                   [(field.name, field.value) for field in
                                    card.customFields]}
                    card_source = card_fields.get('source')
                    if card_source is None:
                        self.set_custom_field(card.id, source_field_id,
                                              {'text': card_data['source']})

                # update a card
                source.update_card(result, card, board_labels)
                # if current card list and target list don't match,
                # move the card to the target list
                if target_list_name != card.get_list().name:
                    # move list
                    card.change_list(lists[target_list_name].id)

        # before we move to the next card, add this card to the
        # collection of cards we cached before starting this block
        cards_by_source[card_data['source']] = card
        if self.debug:
            try:
                sources_to_process.remove(card_data['source'])
            except Exception as err:
                print("Encountered error while attempting to "
                      "process '%s'" % card_data['source'])
                print(err)

            print("cards not processed:")
            for source_item in sources_to_process:
                print(source_item)

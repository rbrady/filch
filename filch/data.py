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
import abc
import os

import bugzilla
from launchpadlib.launchpad import Launchpad


from filch import constants
from filch import utils


class BugzillaURISource(object):

    def __init__(self, config, uri, include_fields, default_labels=[]):
        self.uri = uri
        self.config = config
        self.client = self.get_client()
        self.include_fields = include_fields
        self.default_labels = default_labels

    def get_client(self):
        return bugzilla.Bugzilla44(
            url=self.config['url'],
            user=self.config['user'],
            password=self.config['password'],
            sslverify=self.config['sslverify']
        )

    def query(self):
        query = self.client.url_to_query(self.uri)
        query["include_fields"] = self.include_fields
        return self.client.query(query)

    @staticmethod
    def get_labels(results):
        return {
            "sky": list(set([r.version.title() for r in results])),
            "blue": list(set([r.priority.title() for r in results]))
        }

    @staticmethod
    def sort_card(bz):
        # figure out which list
        if bz.status == 'ON_DEV':
            target_list = "In Progress"
        elif bz.status in ['NEW', 'ASSIGNED']:
            if 'FutureFeature' in bz.keywords:
                target_list = 'Features'
            else:
                target_list = 'Bugs'
        else:
            target_list = 'Complete'

        return target_list

    def create_card(self, bz, labels):

        bz.description = ""
        if len(bz.comments) > 0:
            bz.description = bz.comments[0]['text']

        card_labels = [bz.version, bz.priority] + self.default_labels

        return {
            'name': bz.summary,
            'description': constants.BZ_CARD_DESC.format(**bz.__dict__),
            'labels': card_labels,
            'date_due': None,
            'source': bz.weburl,
        }

    @staticmethod
    def update_card(bz, card, labels):
        # todo (rbrady): the pytrello library does not have support for
        # deleting labels from a card.  Add the support to the pytrello
        # library and then update the code here to check the current version
        # and priority and update as necessary.
        card_comments = [cm['data']['text'] for cm in card.get_comments()]
        # add comments in bz as comments in a card
        if len(bz.comments) > 1:
            for comment in bz.comments[1:]:
                comment_text = constants.COMMENT_TEXT.format(
                    text=comment['text'],
                    author=comment['author'],
                    create_time=comment['creation_time'],
                    is_private=constants.COMMENT_PRIVACY[
                        comment['is_private']],
                )
                try:
                    if comment_text not in card_comments:
                        card.comment(comment_text)
                except Exception as err:
                    print(str(err))

        # add external trackers in bz as a checklist in a card
        # check for external tracker checklist in the card
        # if it exists, get a reference to it, otherwise create it
        card_checklists = card.fetch_checklists()
        trackers_checklist = [cl for cl in card_checklists
                              if cl.name == "External Trackers"]
        if len(trackers_checklist) < 1:
            trackers_checklist = card.add_checklist('External Trackers', [])
        else:
            trackers_checklist = trackers_checklist[0]

        if len(bz.external_bugs) > 0:
            # external trackers may be added, removed, etc.  clear all list
            # items and rebuild.
            trackers_checklist.clear()
            external_trackers = []
            for ext_bug in bz.external_bugs:
                external_trackers.append(
                    os.path.join(ext_bug['type']['url'],
                                 ext_bug['ext_bz_bug_id'])
                )

            for tracker in external_trackers:
                trackers_checklist.add_checklist_item(tracker)


class ManualBlueprintSource(object):

    def __init__(self, project, blueprints, default_labels=[]):
        self.project = project
        self.blueprints = blueprints
        self.default_labels = default_labels

    def query(self):
        results = []
        for item in self.blueprints:
            results.append(utils.get_blueprint(self.project, item))
        return results

    @staticmethod
    def get_labels(results):
        return {}

    @staticmethod
    def sort_card(blueprint):
        if blueprint['is_complete']:
            return "Complete"
        elif blueprint['is_started']:
            return "In Progress"
        else:
            return "Features"

    def create_card(self, blueprint, labels):
        version = "unspecified"
        if blueprint['milestone_link']:
            version = blueprint['milestone_link'].split('/')[-1].split('-')[0]
        priority = blueprint['priority']
        # normalize the priority to fit within typical RFE attributes
        if priority == 'Essential':
            priority = 'High'
        bp_labels = [label.name for label in labels
                     if label.name.endswith("(%s)" % version.title())
                     or label.name.lower() == priority.lower()]

        card_labels = bp_labels + self.default_labels

        return {
            'name':  blueprint.get('title', ''),
            'description': constants.BLUEPRINT_CARD_DESC.format(**blueprint),
            'labels': card_labels,
            'date_due': None,
            'source': blueprint.get('web_link', '')
        }

    def update_card(self, blueprint, card, labels):
        # todo(rbrady): add code to swap labels for version and priority
        # if needed, once the ability to delete labels from a card is added
        # to py-trello.
        pass


class LaunchpadBugSource(object):

    def __init__(self, project, search_args, default_labels=[]):
        self.project = project
        self.search_args = search_args
        self.default_labels = default_labels

    def query(self):
        launchpad = Launchpad.login_anonymously('filch', 'production',
                                                version='devel')
        project = launchpad.projects[self.project]
        bugs = project.searchTasks(**self.search_args)
        return bugs

    @staticmethod
    def get_labels(results):
        return {}

    @staticmethod
    def sort_card(bug):

        if bug.status in ["New", "Confirmed", "Triaged", "Incomplete"]:
            return "Bugs"
        elif bug.status == "In Progress":
            return "In Progress"
        else:
            return "Complete"

    def create_card(self, bug, labels):
        try:
            version = bug.milestone.name.split('/')[-1].split('-')[0]
        except:
            version = "unspecified"

        priority = bug.importance
        # normalize the priority to fit within typical Bug attributes
        if priority == 'Critical':
            priority = 'High'
        if priority == 'Wishlist':
            priority = 'Low'

        bp_labels = [label.name for label in labels
                     if label.name.endswith("(%s)" % version.title())
                     or label.name.lower() == priority.lower()]

        card_labels = bp_labels + self.default_labels

        card_values = {
            "description": bug.bug.description,
            "web_link": bug.bug.web_link,
            "information_type": bug.bug.information_type,
            "id": bug.bug.id
        }

        return {
            'name':  bug.bug.title,
            'description': constants.BUG_CARD_DESC.format(**card_values),
            'labels': card_labels,
            'date_due': None,
            'source': bug.bug.web_link
        }

    def update_card(self, bug, card, labels):
        # todo(rbrady): add code to swap labels for version and priority
        # if needed, once the ability to delete labels from a card is added
        # to py-trello.
        pass
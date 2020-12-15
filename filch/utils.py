# The MIT License (MIT)
#
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
import bugzilla
from launchpadlib.launchpad import Launchpad
import requests

from filch import constants


def get_blueprint(project, blueprint):
    url = 'https://api.launchpad.net/devel/{project}/+spec/{blueprint}'
    r = requests.get(
        url.format(project=project, blueprint=blueprint))
    return r.json()


def get_launchpad_bug(bug_id):
    url = 'https://api.launchpad.net/devel/bugs/%s'
    r = requests.get(url % bug_id)
    return r.json()


def add_tags_to_launchpad_bug(bug_id, tags):
    launchpad = Launchpad.login_with('Filch', 'production', version='devel')
    bug = launchpad.bugs[bug_id]
    bug.tags = bug.tags + tags
    bug.lp_save()


def remove_tags_from_launchpad_bug(bug_id, tags):
    launchpad = Launchpad.login_with('Filch', 'production', version='devel')
    bug = launchpad.bugs[bug_id]
    for tag in tags:
        bug.tags.remove(tag)
    bug.tags = bug.tags
    bug.lp_save()


def get_storyboard_story(story_id):
    url = 'https://storyboard.openstack.org/api/v1/stories/%s' % story_id
    r = requests.get(url)
    story = r.json()
    story['story_url'] = (
            'https://storyboard.openstack.org/#!/story/%s' %
            story_id)
    return story


def get_bz(bz_id, **kwargs):
    bz4 = bugzilla.Bugzilla44(
        url=kwargs['url'],
        user=kwargs['user'], password=kwargs['password'],
        sslverify=kwargs['sslverify']
    )

    return bz4.getbug(bz_id)


def get_description(desc):
    l = len(desc)
    if l > constants.MAX_DESC_LEN:
        desc = desc[l - constants.MAX_DESC_LEN:]
    return desc

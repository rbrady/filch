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
GERRIT_CARD_DESC = u"""This card was imported to Trello from Gerrit.

url: https://review.openstack.org/#/c/{_number}/
updated: {updated}
project: {project}
status: {status}
source: gerrit|{_number}
"""

BLUEPRINT_CARD_DESC = u"""{summary}

blueprint_url: {web_link}
spec: {specification_url}
assignee: {assignee_link}
status: {lifecycle_status}
definition: {definition_status}
source: bp|{name}
"""

BUG_CARD_DESC = u"""{description}

bug_url: {web_link}
information_type: {information_type}
source: bug|{id}
"""

STORY_CARD_DESC = u"""{description}

story_url: {story_url}
status: {status}
source: story|{id}
"""

BZ_CARD_DESC = u"""{description}

bug_url: {weburl}
source: bz|{id}
"""

COMMENT_PRIVACY = {
    True: 'Private',
    False: 'Public'
}

COMMENT_TEXT = u"""{text}

{author} | {create_time}({is_private})
"""


MAX_DESC_LEN = 16384

SUPPORTED_LABEL_COLORS = ['yellow', 'purple', 'blue', 'red', 'green',
                          'orange', 'black', 'sky', 'pink', 'lime', 'null']

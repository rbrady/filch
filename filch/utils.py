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
import requests


def get_blueprint(project, blueprint):
    url = 'https://api.launchpad.net/devel/{project}/+spec/{blueprint}'
    r = requests.get(
        url.format(project=project, blueprint=blueprint))
    return r.json()


def get_launchpad_bug(bug_id):
    url = 'https://api.launchpad.net/devel/bugs/%s'
    r = requests.get(url % bug_id)
    return r.json()


def get_bz(bz_id, **kwargs):
    bz4 = bugzilla.Bugzilla44(
        url=kwargs['url'],
        user=kwargs['user'], password=kwargs['password'],
        sslverify=kwargs['sslverify']
    )

    return bz4.getbug(bz_id)


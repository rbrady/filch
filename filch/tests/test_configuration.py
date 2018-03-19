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
import pytest

from filch import configuration
from filch import exceptions as peeves

good_config_data = """
trello:
  api_key: testkey
  access_token: testtoken
  default_board: test-board
"""

good_config_obj = {
    'trello': {
        'api_key': 'testkey',
        'access_token': 'testtoken',
        'default_board': 'test-board'
    }
}

config_data_missing_section = """
mello:
  access_token: testtoken
  default_board: test-board
"""

config_data_missing_setting = """
trello:
  access_token: testtoken
  default_board: test-board
"""


class TestConfiguration(object):

    def test_get_config(self):
        mock_open = mock.mock_open()
        mock_open().read.return_value = good_config_data
        with mock.patch('six.moves.builtins.open', mock_open):
            result = configuration.get_config()
            assert result == good_config_obj

    def test_get_config_missing_section(self):
        mock_open = mock.mock_open()
        mock_open().read.return_value = config_data_missing_section
        with mock.patch('six.moves.builtins.open', mock_open):
            with pytest.raises(peeves.MissingConfigurationSectionException):
                configuration.get_config()

    def test_get_config_missing_setting(self):
        mock_open = mock.mock_open()
        mock_open().read.return_value = config_data_missing_setting
        with mock.patch('six.moves.builtins.open', mock_open):
            with pytest.raises(peeves.MissingConfigurationSettingException):
                configuration.get_config()

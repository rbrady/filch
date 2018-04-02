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
#!/usr/bin/env python
from pprint import pprint
import sys

import click
import jinja2

from filch import boards
from filch import configuration
from filch import exceptions as peeves


@click.command()
@click.argument('report')
@click.option('--template', default=None, type=str)
@click.option('--output', default=None, type=str)
@click.option('--board', '-b', default=None, type=str)
@click.option('--list_name', default=None, type=str, multiple=True)
def reports(report, template, output, board, list_name):
    try:
        config = configuration.get_config()
    except peeves.MissingConfigurationSettingException as missing_section:
        click.echo(str(missing_section))
        sys.exit(1)
    except peeves.MissingConfigurationSectionException as missing_setting:
        click.echo('Trello config section required.')
        click.echo(str(missing_setting))
        sys.exit(1)

    # choose the report query
    if report == "board":
        if not board:
            click.echo('If board report is indicated, you must '
                       'include a board argument. (--board or -b)')
            sys.exit(1)
        else:
            board_manager = boards.BoardManager(config['trello'], board)
            # create board context
            context = {'board': board_manager.board}
    else:
        click.echo('Unsupported report type requested.')
        sys.exit(1)

    # if there is a template present for the output, then merge the template
    # with the data
    if template:
        with open(template, 'r') as template_file:
            template_data = template_file.read()
            # Render the j2 template
            raw_template = jinja2.Environment().from_string(
                template_data)
            r_template = raw_template.render(**context)
            # if there is an output arg, write to a file of that name.
            if output:
                with open(output, 'w') as output_file:
                    output_file.write(r_template)
            else:
                # else, just print report to terminal
                click.echo(pprint(r_template))
    else:
        click.echo(pprint(context))


if __name__ == "__main__":
    reports()

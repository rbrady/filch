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
from filch import boards
from filch import configuration
from filch import data


def main():
    BOARD_NAME = 'DFG-Component'
    # BZ Queries
    OPEN_UNTRIAGED_BUGS = 'https://bugzilla.redhat.com/buglist.cgi?action=wrap&bug_status=NEW&bug_status=ASSIGNED&bug_status=POST&bug_status=MODIFIED&bug_status=ON_DEV&bug_status=ON_QA&bug_status=VERIFIED&bug_status=RELEASE_PENDING&chfield=%5BBug%20creation%5D&chfieldto=Now&f1=product&f10=flagtypes.name&f11=CP&f12=cf_internal_whiteboard&f2=cf_internal_whiteboard&f3=component&f4=cf_conditional_nak&f5=cf_qe_conditional_nak&f6=OP&f7=keywords&f8=priority&f9=bug_severity&keywords=FutureFeature%2C%20Tracking%2C%20Documentation%2C%20&keywords_type=nowords&list_id=8303834&n6=1&o1=equals&o10=substring&o12=equals&o2=substring&o3=notsubstring&o4=isempty&o5=isempty&o7=substring&o8=notsubstring&o9=notsubstring&saved_report_id=1948&v1=Red%20Hat%20OpenStack&v10=rhos&v12=DFG%3AWorkflows&v2=DFG%3A&v3=doc&v7=Triaged&v8=unspecified&v9=unspecified'
    BUG_BACKLOG_BY_RELEASE = 'https://bugzilla.redhat.com/buglist.cgi?action=wrap&bug_status=NEW&bug_status=ASSIGNED&bug_status=POST&bug_status=MODIFIED&bug_status=ON_DEV&bug_status=ON_QA&bug_status=VERIFIED&bug_status=RELEASE_PENDING&f2=component&f3=cf_internal_whiteboard&f4=product&f5=cf_internal_whiteboard&keywords=FutureFeature%2C%20Tracking%2C%20Documentation%2C%20&keywords_type=nowords&list_id=8303843&o2=notsubstring&o3=substring&o4=equals&o5=equals&v2=doc&v3=DFG%3A&v4=Red%20Hat%20OpenStack&v5=DFG%3AWorkflows'
    RFE_BACKLOG_BY_RELEASE = 'https://bugzilla.redhat.com/buglist.cgi?action=wrap&bug_status=NEW&bug_status=ASSIGNED&bug_status=POST&bug_status=MODIFIED&bug_status=ON_DEV&bug_status=ON_QA&bug_status=VERIFIED&bug_status=RELEASE_PENDING&f2=component&f3=cf_internal_whiteboard&f4=product&f5=keywords&f6=cf_internal_whiteboard&keywords=Tracking%2C%20Documentation%2C%20&keywords_type=nowords&list_id=8303849&o2=notsubstring&o3=substring&o4=equals&o5=substring&o6=equals&v2=doc&v3=DFG%3A&v4=Red%20Hat%20OpenStack&v5=FutureFeature&v6=DFG%3AWorkflows'

    # BZ fields to include in the queries
    BZ_INCLUDE_FIELDS = ["id", "summary", "version", "status", "priority",
                         "comments", "weburl", "information_type",
                         "external_bugs", "keywords"]

    # filch configuration data
    config = configuration.get_config()

    # add bugzilla sources from the queries above
    bug_backlog = data.BugzillaURISource(
        config['bugzilla']['redhat'],
        BUG_BACKLOG_BY_RELEASE,
        BZ_INCLUDE_FIELDS,
        default_labels=['Bug']
    )

    open_untriaged_bzs = data.BugzillaURISource(
        config['bugzilla']['redhat'],
        OPEN_UNTRIAGED_BUGS,
        BZ_INCLUDE_FIELDS,
        default_labels=['Bug']
    )

    rfe_backlog = data.BugzillaURISource(
        config['bugzilla']['redhat'],
        RFE_BACKLOG_BY_RELEASE,
        BZ_INCLUDE_FIELDS,
        default_labels=['RFE']
    )

    # launchpad blueprints don't have tags to associate them with specific
    # projects.  adding them manually seems to be the only way to ensure
    # specific blueprints are tracked.
    tripleo_blueprints = data.ManualBlueprintSource(
        "tripleo", ['tripleo-common-enhance-list-roles-action',
                    'tripleo-common-list-available-roles-action',
                    'tripleo-common-select-roles-workflow',
                    'update-roles-action', 'validate-roles-networks',
                    'get-networks-action', 'update-networks-action'],
        default_labels=['RFE']
    )

    board_manager = boards.BoardManager(config['trello'], BOARD_NAME)

    # add DFG-specific customizations to the board
    # add labels needed for our purposes
    # there are 11 label color options available
    # yellow, purple, blue, red, green, orange,
    # black, sky, pink, lime, null

    # Warning Status Labels (Red)
    # These labels denote something impeding progress
    board_manager.add_labels_by_color("red",
                                      ['UNTRIAGED', 'BLOCKED', 'CI-BLOCKED'])
    # Type Labels (Black)
    board_manager.add_labels_by_color("black", ["RFE", "Bug"])

    # Unplanned Work Labels (Orange)
    board_manager.add_labels_by_color("orange", ["Unplanned"])

    # Sprint Labels (Purple)
    board_manager.add_labels_by_color("purple", ["Sprint 1", "Sprint 2",
                                                 "Sprint 3", "Sprint 4"])

    # add the sources of external artifacts
    board_manager.sources.append(bug_backlog)
    board_manager.sources.append(open_untriaged_bzs)
    board_manager.sources.append(rfe_backlog)
    board_manager.sources.append(tripleo_blueprints)

    # execute the board manager logic
    board_manager.run()


if __name__ == "__main__":
    main()

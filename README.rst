=====
filch
=====

The purpose of this project is to retrieve data from external systems and
import or update trello cards.  The external systems are the source of truth
for details and status while the trello card only holds comments or downstream
specific information.

************
Installation
************

Filch is still under development and not released on PyPi yet. ::

    git clone https://github.com/rbrady/filch.git
    cd filch
    virtualenv .myenv
    source .myenv/bin/activate
    pip install -IU .

*************
Configuration
*************

Filch expects a yaml configuration file in the root of your home directory named
".filch.yaml".  There are three main sections titled 'trello', 'bugzilla', and
'gerrit'.

You'll need to visit https://trello.com/app-key and generate an
api key.  once you have your api key, you'll also need to visit the following
URI, substituting your api key in <your_key>.

`<https://trello.com/1/authorize?expiration=never&scope=read,write,account&response_type=token&name=Server%20Token&key=\<your_key\>>`_

Next, you'll need to update the ~/.filch.yaml file and insert your api key and
access token: ::

    trello:
      api_key: deadbeefdeadbeefbeadbeef
      access_token: 123456789012345678901234567890
      default_board: My-Board
    bugzilla:
      redhat:
        url: https://bugzilla.redhat.com/xmlrpc.cgi
        user: username@example.org
        password: password
        sslverify: True
    gerrit:
      openstack:
        url: https://review.openstack.org
      rdo:
        url: https://review.rdoproject.org


You will also need to update values for Bugzilla and Gerrit hosts if applicable.
Both the Bugzilla and Gerrit services can have multiple hosts listed (as in the
Gerrit example above).  A host can be selected when running the command by
passing the --host argument.  If you do not pass a host for Gerrit, it defaults
to the upstream OpenStack Gerrit instance at https://review.openstack.org.  If
you do not pass a host argument when using the Bugzilla service, it will use the
first listed host in the configuration section.

Managed Boards
--------------

In an effort to further reduce manual interaction with the Trello board, Filch
now has the concept of a managed board.  You can create a script (see examples
directory) that is idempotent to create and populate a Trello board with cards
based on external artifacts.  If the artifact is already represented in the
board, the card will be updated.  For any updates needed to a given card, make
the update to the source artifact and re-run the script.

Importing External Artifacts To Trello
======================================

The import command supports the following format: ::

    filch-import SERVICE [Options]

The service value can be gerrit, blueprint, bug, story or bugzilla (bz).  The
command also accepts the following arguments, some of which are reusable
between the different services: --id, --url, --host, --user, --password,
--project, --board, --labels, --list_name.

Gerrit
======

The following example demonstrates importing a change from gerrit: ::

    filch-import gerrit --id 299937


Launchpad Blueprint
===================

The following example demonstrates importing the mistral-deployment-library
blueprint from the TripleO project.  Importing a blueprint requires you pass
both the blueprint id and project it belongs to. ::

    filch-import blueprint --id mistral-deployment-library --project tripleo


Launchpad Bug
=============

The following example demonstrates importing a bug from launchpad: ::

    filch-import bug --id 1594879


Bugzilla
========

The following example demonstrates importing a bug from Bugzilla: ::

    filch-import bz --id 1546122


Storyboard
==========

The following example demonstrates importing a story from Storyboard: ::

    filch-import story --id 2001596


Overriding Default Values
=========================

You can override the values of the board (--board) or list (--list_name) where
the card is created in Trello ::

    filch-import gerrit --id 299937 --board Example-Board --list_name Backlog


Adding Labels
=============

You can add one or more labels to a card created in Trello by passing  -l <Label>
to the command for each label you want to add.  The label must correspond to a
label name already in Trello. ::

    filch-import gerrit --id 299937 -l Imported -l Blocked


Using Hosts
===========

When you have multiple hosts listed in a given service, you can use the --host
argument to select which host to use. ::

    filch-import gerrit --id 299937 --host rdo


*******
Testing
*******

To run unit tests: ::

    python -m pytest

filch
======

The purpose of this project is to retrieve data from external systems and
import or update trello cards.  The external systems are the source of truth
for details and status while the trello card only holds comments or downstream
specific information.

To use filch, you'll need to visit https://trello.com/app-key and generate an
api key.  once you have your api key, you'll also need to visit the following
URI, substituting your api key in <your_key>.

https://trello.com/1/authorize?expiration=never&scope=read,write,account&response_type=token&name=Server%20Token&key=<your_key>

Next, you'll need to create a ~/.filch.conf file and insert your api key and
access token:

    [trello]
    api_key=xxxxxxx
    access_token=xxxxxxxxxxxxxxxxxx
    default_board=My-Favorite-Trello-Board


Usage Examples
--------------

Gerrit
~~~~~~

The following example demonstrates importing a change from gerrit.

trello_import --gerrit 299937


Importing a Blueprint Launchpad
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following example demonstrates importing the mistral-deployment-library from
the TripleO project.

trello_import --blueprint mistral-deployment-library --project tripleo


Overriding Default Values
~~~~~~~~~~~~~~~~~~~~~~~~~

You can override the values of the board (--board) or list (--list_name) where the card is created in
Trello.

trello_import --gerrit 299937 --board Example-Board --list_name Backlog


Adding Labels
~~~~~~~~~~~~~

You can add one or more labels to a card created in Trello by passing  -l <Label>
to the command for each label you want to add.  The label must correspond to a
label name already in Trello.

trello_import --gerrit 299937 -l Imported
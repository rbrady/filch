filch
-----

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
""" Parse XIVAPI item JSON and create items. 
"""

# TODO: track task completion time.

import json

from django.core.management.base import BaseCommand, CommandError

from app.models import *


INPUT_FILE = "data/xivapi_item_list.json"


def ingest_item_list():
    api_resp = json.load(open(INPUT_FILE))

    new_items = []

    for i in api_resp:
        # Ignore invalid items.
        if i['Name'] == "": continue

        try:
            item = Item.objects.get(guid=i['ID'])
        except Item.DoesNotExist:
            item      = Item()
            item.name = i['Name']
            item.guid = i['ID']
            item.icon = i['Icon']

            new_items.append(item)

    Item.objects.bulk_create(new_items)


class Command(BaseCommand):
    """Required class for using manage.py to invoke tasks.
    """
    help = ''

    def handle(self, *args, **options):
        ingest_item_list()

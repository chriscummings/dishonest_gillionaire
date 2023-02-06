# TODO: thread api requests, XIVAPI limit is 20/req/sec.
# TODO: track task completion time.
# TODO: this task takes forever, print some kind of current id or status..

import json

from django.core.management.base import BaseCommand, CommandError
import requests

from app.models import *
from app.utils import fetch_json


INPUT_FILE  = "data/xivapi_item_list.json"
OUTPUT_FILE = "data/xivapi_items.json"


def ingest_item_list():
	item_list_json = json.load(open(INPUT_FILE))

	items = []

	for i in item_list_json:
		guid = i['ID']

		endpoint = "https://xivapi.com/Item/"+str(i['ID'])+"?private_key=dd9f8560cb57415684fcfa1d1005e17eb5450d1a1c0f46ba8dd7ed9565bcb8ce"
		api_resp = fetch_json(endpoint)

		items.append(api_resp)

	with open(OUTPUT_FILE, "w") as json_file:
		json_file.write(json.dumps(items, indent=4))


class Command(BaseCommand):
	""" Required class for using manage.py to invoke tasks. """

	help = ''

	def handle(self, *args, **options):
		ingest_item_list()

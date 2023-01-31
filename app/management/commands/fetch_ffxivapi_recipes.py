# TODO: thread api requests, XIVAPI limit is 20/req/sec.
# TODO: track task completion time.
# TODO: this task takes forever, print some kind of current id or status..

import json

from django.core.management.base import BaseCommand, CommandError
import requests

from app.models import *
from app.utils import fetch_json


INPUT_FILE = "data/ffxivapi_recipe_list.json"
OUTPUT_FILE = "data/ffxivapi_recipes.json"


def ingest_recipe_list():
	recipe_list_json = json.load(open(INPUT_FILE))

	recipes = []

	for r in recipe_list_json:
		guid = r['ID']

		endpoint = "https://xivapi.com/Recipe/"+str(r['ID'])+"?private_key=dd9f8560cb57415684fcfa1d1005e17eb5450d1a1c0f46ba8dd7ed9565bcb8ce"
		api_resp = fetch_json(endpoint)

		recipes.append(api_resp)

	with open(OUTPUT_FILE, "w") as json_file:
		json_file.write(json.dumps(recipes, indent=4))


class Command(BaseCommand):
	"""Required class for using manage.py to invoke tasks.
	"""
	help = ''

	def handle(self, *args, **options):
		ingest_recipe_list()

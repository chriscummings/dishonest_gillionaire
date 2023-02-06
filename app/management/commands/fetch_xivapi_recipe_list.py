# TODO: thread api requests, XIVAPI limit is 20/req/sec.
# TODO: track task completion time.

import json

from django.core.management.base import BaseCommand, CommandError
import requests

from app.models import *
from app.utils import fetch_json


# FIXME: private key in repo
ENDPOINT = "https://xivapi.com/recipe?private_key=dd9f8560cb57415684fcfa1d1005e17eb5450d1a1c0f46ba8dd7ed9565bcb8ce"
OUTPUT_FILE = "data/xivapi_recipe_list.json"


def generate_item_list_json():
	recipes = []

	# Get initial page.
	api_resp = fetch_json(ENDPOINT)

	for result in api_resp["Results"]:
		recipes.append(result)

	# Get subsequent pages.
	next_page = api_resp["Pagination"]["PageNext"]
	while next_page:
		print("Handling page: "+str(next_page)+"/"+str(api_resp["Pagination"]["PageTotal"]))
		api_resp = fetch_json(ENDPOINT+"&page="+str(next_page))
		next_page = api_resp["Pagination"]["PageNext"]
		for result in api_resp["Results"]:
			recipes.append(result)

	with open(OUTPUT_FILE, "w") as json_file:
		json_file.write(json.dumps(recipes, indent=4))


class Command(BaseCommand):
	"""Required class for using manage.py to invoke tasks.
	"""
	help = ''

	def handle(self, *args, **options):
		generate_item_list_json()
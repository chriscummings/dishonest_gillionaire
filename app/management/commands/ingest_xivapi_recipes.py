""" Parse XIVAPI recipe JSON and create recipes and relationships. 
"""

# TODO: track task completion time.

import json
import time
import datetime

from django.core.management.base import BaseCommand, CommandError
import requests

from app.models import *


INPUT_FILE = "data/ffxivapi_recipes.json"


def create_ingredient(recipe, item, count):
	ingredient = RecipeItemIngredient()
	ingredient.count = count
	ingredient.item = item
	ingredient.recipe = recipe
	ingredient.save()

def ingest_recipes():
	start_time = datetime.datetime.now()
	recipe_json = json.load(open(INPUT_FILE))

	for r in recipe_json:
		recipe = Recipe.objects.filter(guid=r['ID'])
		if not recipe:
			# Ignore old/invalid recipes.
			if r['AmountResult'] == 0: continue
			if not r['ItemResult']: continue

			# Get the item this recipe creates.
			item = Item.objects.get(guid=r['ItemResult']['ID'])

			# FIXME: handle this.
			if not item:
				raise "OH SNAP, ITEM "+str(item_guid)+" NOT FOUND"

			recipe               = Recipe()
			recipe.name          = r['Name']
			recipe.icon          = r['ItemResult']['Icon']
			recipe.guid          = r['ID']
			recipe.profession    = r['ClassJob']['Name']
			recipe.item          = item
			recipe.result_amount = r['AmountResult']
			recipe.save()

			# There are 10 (0-9) recipe ingredients max. There are always "static" keys for each of the 10 possible ingredients.
			for i in range(0,10):
				if r['AmountIngredient'+str(i)] > 0:
					count     = r['AmountIngredient'+str(i)]
					item_guid = r['ItemIngredient'+str(i)]['ID']

					item = Item.objects.get(guid=item_guid)
					if not item:
						raise "OH SNAP, ITEM "+str(item_guid)+" NOT FOUND"

					create_ingredient(recipe, item, count)

	print(datetime.datetime.now() - start_time)


class Command(BaseCommand):
	"""Required class for using manage.py to invoke tasks.
	"""
	help = ''

	def handle(self, *args, **options):
		ingest_recipes()

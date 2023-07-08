from app.models import *
from django.core.management.base import BaseCommand, CommandError
import json
from glob import glob
import shutil


class Command(BaseCommand):

	"""Required class for using manage.py to invoke tasks.
	"""
	help = ''

	def handle(self, *args, **options):
		
		item_guids = [19584, 19947, 19957, 5116, 8, 19947, 9, 19928, 19933, 10, 19983, 19984, 19984, 19985, 19986, 5522, 5491, 5518, 7, 12, 11]

		items_dir = 'data/item_details'
		recipes_dir = 'data/recipe_details'
		output_dir = 'app/test_data'

		item_json_files = glob(f"{items_dir}/*.json")
		for json_file in item_json_files:
			f = open(json_file)
			data = json.load(f)

			item_guid = data["ID"]

			if item_guid in item_guids:
				shutil.copyfile(json_file, f"{output_dir}/item_{item_guid}.json")

		recipe_json_files = glob(f"{recipes_dir}/*.json")
		for json_file in recipe_json_files:
			f = open(json_file)
			data = json.load(f)

			item_guid = data["ItemResultTargetID"]
			recipe_guid = data['ID']

			if item_guid in item_guids:
				shutil.copyfile(json_file, f"{output_dir}/recipe_{recipe_guid}.json")




from django.core.management.base import BaseCommand, CommandError
from app.facts_handling import derive_to_craft_pricing


class Command(BaseCommand):
	""" Required class for using manage.py to invoke tasks.
	"""
	help = ''

	def handle(self, *args, **options):
		derive_to_craft_pricing()

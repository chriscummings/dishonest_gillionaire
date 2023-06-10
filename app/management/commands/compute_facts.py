from django.core.management.base import BaseCommand, CommandError
from app.facts_handling import compute_item_facts


class Command(BaseCommand):
	""" Required class for using manage.py to invoke tasks.
	"""
	help = ''

	def handle(self, *args, **options):
		compute_item_facts()

""" Fetches market board item listings from Universalis API. 
"""

from django.core.management.base import BaseCommand, CommandError
from app.api_handling import Universalis


class Command(BaseCommand):
	""" Required class for using manage.py to invoke tasks.
	"""
	help = ''

	def handle(self, *args, **options):
		handler = Universalis()
		handler.fetch_listings()

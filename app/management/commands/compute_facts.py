from django.core.management.base import BaseCommand, CommandError
from app.facts_handling import summarize_market_stats


class Command(BaseCommand):
	""" Required class for using manage.py to invoke tasks.
	"""
	help = ''

	def handle(self, *args, **options):
		summarize_market_stats()

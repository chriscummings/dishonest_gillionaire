import requests
import time
import json
from app.forms import SearchBarForm
import inspect
from app.models import *
from datetime import datetime


def captute_runtime(func):
	def wrapper(*args, **kwargs):
		runtime = RunTime()
		runtime.process_name = func.__name__
		runtime.process_caller = inspect.stack()[1][3] #?
		runtime.started_at = datetime.now()
		runtime.save()		
		func(*args, **kwargs)
		runtime.ended_at = datetime.now()
		runtime.run_time = runtime.ended_at - runtime.started_at
		runtime.save()
		print(runtime.run_time)
	return wrapper

def inject_form(request):
    return {'search_form': SearchBarForm()}

def fetch_json(url):
	""" 
	"""
	print('Fetching data..')
	retries = 0
	success = False
	while not success:
		try:
			req = requests.get(url, timeout=30)
			if  req.status_code == 200:
				return req.json()
			else:
				with open("last-call.json", "w") as json_file:
					json_file.write(json.dumps(req.json(), indent=4))
			success = True
			retries += 1
		except Exception as error:
			print(error)
			time.sleep(retries)


# https://na.finalfantasyxiv.com/lodestone/worldstatus/
SERVER_TOPOLOGY = {
	'regions': [
		{
			'name': 'North-America',
			'data_centers': [
				{
					'name': 'Aether',
					'worlds': [
						'Adamantoise',
						'Cactuar',
						'Faerie',
						'Gilgamesh',
						'Jenova',
						'Midgardsormr',
						'Sargatanas',
						'Siren'		
					]
				},
				{
					'name': 'Crystal',
					'worlds': [
						'Balmung',
						'Brynhildr',
						'Coeurl',
						'Diabolos',
						'Goblin',
						'Malboro',
						'Mateus',
						'Zalera'
					]
				},
				{
					'name': 'Dynamis',
					'worlds': [
						'Halicarnassus',
						'Maduin',
						'Marilith',
						'Seraph'
					]
				},
				{
					'name': 'Primal',
					'worlds': [
						'Behemoth',
						'Excalibur',
						'Exodus',
						'Famfrit',
						'Hyperion',
						'Lamia',
						'Leviathan',
						'Ultros'
					]
				}												
			]
		}
	]
}

def seed_region_dc_world():
	for r in SERVER_TOPOLOGY['regions']:
		region_name = r['name']

		try:
			region = Region.objects.get(name=region_name)
			print(region.id)
		except Region.DoesNotExist as error:
			region = Region()
			region.name = region_name
			region.save()

		for dc in r['data_centers']:
			dc_name = dc['name']

			try:
				data_center = DataCenter.objects.get(name=dc_name)
			except DataCenter.DoesNotExist as error:
				data_center = DataCenter()
				data_center.name = dc_name
				data_center.region = region
				data_center.save()

			for world_name in dc['worlds']:

				try:
					world = World.objects.get(name=world_name)
				except World.DoesNotExist as error:
					world = World()
					world.name = world_name
					world.data_center = data_center
					world.save()




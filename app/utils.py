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

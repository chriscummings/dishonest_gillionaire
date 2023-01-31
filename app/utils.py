import requests
import time
import json

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

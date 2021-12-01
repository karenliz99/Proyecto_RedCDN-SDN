import requests
import time
import random

flag=True
while(flag):
	delay = random.uniform(0.002,2)
	url = "http://10.0.0.34"
	solicitud = requests.get(url)
	time.sleep(delay)
	

import requests
import time
import random
import sys

i=100
f=open("6_latencyh1h37.txt", "a")

while i>0:
	url = "http://10.0.0.37"
	solicitud = requests.get(url)
	f.write(str(solicitud.elapsed.total_seconds())+"\n")
	i = i-1

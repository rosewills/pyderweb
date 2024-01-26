#!/usr/bin/env python
'''
PyderWeb

Version: 0.1.0
Created: 2024-01-19 (by Rose Wills)
Status: working (needs documentation)

This script is for anyone planning a move who is considering multiple
possible locations for your new home, and would like to compare the driving
distance/time of each place to a fixed set of points of interest (family
members' homes, work/school, favorite vacation spots, airports, etc.)

I wrote it because I am currently job searching, my family lives all over
the place, and I don't much care for driving long distances.

This script takes a set of potential home addresses ("homes") and a set
of destination addresses ("dests"), and fetches data about the shortest
routes between them. Output can be presented in the following forms:

	- saved to a csv file
	- plotted on an illustrated map (or set of maps), saved to an .html
	- printed directly to the terminal

Data about each individual route (from openrouteservice) can also optionally
be saved to its own json file.

NOTES:
	- The home & destination lists can be arbitrarily long; however once the
	  total number of requested routes (homes * dest) reaches above ~20,
	  OpenRouteService tends to throw rate usage warnings and the script slows
	  down considerably.
	- Sometimes 

This script is currently a work-in-progress.

'''

import re				# regex support
import random			# used to generate random colors for plotting routes
import math				# used to present 
from time import sleep
import json
import pandas as pd
import folium

from geopy.exc import GeocoderTimedOut
# from geopy.geocoders import Nominatim
from geopy.geocoders import GoogleV3
import openrouteservice
from openrouteservice import convert

# geolocator = Nominatim(user_agent="pyderweb")
geolocator = GoogleV3(api_key="INSERT_GOOGLE_MAPS_API_KEY_HERE")
client = openrouteservice.Client(key='INSERT_OPENROUTESERVICE_API_KEY_HERE')

class colors:
    purple = '\033[95m'
    blue = '\033[94m'
    cyan = '\033[96m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    bold = '\033[1m'
    underline = '\033[4m'
    endc = '\033[0m'

homes = pd.read_csv("rw/rw-homes.csv", sep="\t", index_col="name")
dests = pd.read_csv("rw/rw-dests.csv", sep="\t", index_col="name")

# print(homes['address'])
# print(dests['address'])


homeShort = pd.read_csv("rw/rw-homes-test.csv", index_col=0, sep="\t")
destShort = pd.read_csv("rw/rw-dests-test.csv", index_col=0, sep="\t")

def filename_formatter(name):
	fileName = name.replace(" ", "-")
	fileName = fileName.replace(".", "")
	fileName = fileName.replace(",", "")
	fileName = fileName.replace("'", "")
	return fileName


def get_geocode(address, name, attempt=1, maxAttempts=5):
	try:
		location = geolocator.geocode(address)
		return location
		sleep(1)

	except GeocoderTimedOut:
		if attempt <= maxAttempts:
			attempt = attempt + 1
			get_geocode(address, name, attempt)
		else:
			errmess = colors.red+"ERROR [get_geocode]: GeocoderTimedOut >>> "+name+"\n\t"+colors.yellow+"giving up after 5 attempts."+colors.endc
			return errmess

	except AttributeError as e:
		errmess = colors.red+"ERROR [get_geocode]: AttributeError >>> "+name+"\n\t"+colors.yellow+str(e)+colors.endc
		return errmess

	except Exception as e:
		errmess = colors.red+"ERROR [get_geocode]: unknown error >>> "+name+"\n\t"+colors.yellow+str(e)+colors.endc
		return errmess
	


def get_data(startLoc, endLoc, saveJson="None"):
	try:
		startCoorFlip = (startLoc.longitude, startLoc.latitude)
		endCoorFlip = (endLoc.longitude, endLoc.latitude)

	except Exception as e:
		errmess = colors.red+"ERROR [get_route]: unknown error >>>\t"+colors.red+str(e)+colors.endc
		return errmess

	coors = (startCoorFlip, endCoorFlip)
	res = client.directions(coors)		

	distance = round(res['routes'][0]['summary']['distance']/1609.34,1)
	duration = round(res['routes'][0]['summary']['duration']/60,1)
	
	if saveJson != "None":
		# Save Route Data to .json File
		with(open(saveJson+'.json','+w')) as f:
			f.write(json.dumps(res,indent=4, sort_keys=True))
	
	return coors, distance, duration



def get_routes(dfStart, dfEnd, saveJsons="None", saveCSV="None", saveMap="None"):

	startLocs = {}
	endLocs = {}
	colorDict = {}
	startLen = 1
	endLen = 1

	table = pd.DataFrame(index = dfStart.index)

	for startName,info in dfStart.iterrows():
		startLoc = get_geocode(info["address"],startName)
		if "Error" in startLoc:
			print(colors.red+endLoc+colors.endc)
		else:
			startLocs[startName] = startLoc
			locLat= str(round(startLoc.latitude,5))[:7]
			locLon = str(round(startLoc.longitude,5))[:7]
			print("...added", "("+locLat+","+locLon+")", startName)
			if len(startName) > startLen:
				startLen = len(startName)

	for endName,info in dfEnd.iterrows():
		endLoc = get_geocode(info["address"],endName)
		if "Error" in endLoc:
			print(colors.red+endLoc+colors.endc)
		else:
			endLocs[endName] = endLoc
			locLat= str(round(endLoc.latitude,5))[:7]
			locLon = str(round(endLoc.longitude,5))[:7]
			print("...added", "("+locLat+","+locLon+")", endName)
			if len(endName) > endLen:
				endLen = len(endName)

	for end in endLocs:
		cVals = random.choices(range(256), k=3)
		endColor = "rgb("+str(cVals[0])+","+str(cVals[1])+","+str(cVals[2])+")"
		colorDict[end] = endColor
	
	# Output Data Files
	for start in startLocs:
		print("Generating Route Data for ", start)

		if saveMap != "None":
			m = folium.Map(location=(startLocs[start].latitude, startLocs[start].longitude),zoom_start=7, control_scale=True,tiles="cartodbpositron")

		for end in endLocs:
			sleep(1)
			if saveJsons != "None":
				dataOut = get_data(endLocs[end], startLocs[start], saveJson=saveJsons+filename_formatter(start)+"-"+filename_formatter(end))
			else:
				dataOut = get_data(endLocs[end], startLocs[start])
			try:
				coors, distance, duration = dataOut
			except ValueError as e:
				print(dataOut)
				break
				
			# Convert Time to Human-Readable Format
			hours = math.floor(duration / 60)
			mins = round(duration % 60)
			if hours > 0 and mins > 0:
				humanTime = str(hours)+"hr "+str(mins)+"min"
			elif hours > 0:
				humanTime = str(hours)+"hr"
			elif mins > 0:
				humanTime = str(mins)+"min"
			else:
				humanTime = "(n/a)"

			# Terminal Output Text
			endMargin = " " * ( endLen - len(end) )
			startMargin = " " * ( startLen - len(start) )
			print(start, startMargin, "<--", end, endMargin, distance, "miles", "("+humanTime+")")

			# Add to Table
			table.at[start, re.split(' |\'', end)[0]+" (D)"] = distance
			table.at[start, re.split(' |\'', end)[0]+" (T)"] = humanTime


			if saveMap != "None":
				# Generate Map
				geometry = client.directions(coors)['routes'][0]['geometry']
				decoded = convert.decode_polyline(geometry)

				routeName = end+" --> "+start

				labeltxt = "<b><strong>"+routeName+"</strong></b></br>"
				distancetxt = "<b><strong>"+str(distance)+" miles </strong></b></br>"
				durationtxt = "<b><strong>"+str(humanTime)+"</strong></b>"

				routeColor = colorDict[end]
				fillColor = routeColor
				color = routeColor

				folium.GeoJson(
					decoded,
					name=routeName,
					style_function=lambda x, fillColor=fillColor, color=color: {
						"fillColor": fillColor,
						"color": color,
					},
				).add_child(folium.Popup(labeltxt+distancetxt+durationtxt,max_width=300)).add_to(m)

				folium.Marker(
					location=list(coors[0][::-1]),
					popup=end,
					icon=folium.Icon(color="green"),
				).add_to(m)

				folium.Marker(
					location=list(coors[1][::-1]),
					popup=start,
					icon=folium.Icon(color="red"),
				).add_to(m)
		
		if saveMap != "None":
			mapFile = saveMap+filename_formatter(start)+".html"
			m.save(mapFile)
	print(table)
	if saveCSV != "None":
		table.to_csv(saveCSV+".csv")

def quick_add(dfAdd, dfExist, type="start", saveJsons="None", saveCSV="None", saveMap="None"):
	if type == "start":
		get_routes(dfAdd, dfExist, saveJsons=saveJsons, saveCSV=saveCSV, saveMap=saveMap)
	elif type == "end":
		get_routes(dfExist, dfAdd, saveJsons=saveJsons, saveCSV=saveCSV, saveMap=saveMap)
	else:
		print("Quick_Add() Error: type \""+type+"\" not understood. Please specify type as either \"start\" or \"end\" only.")



# get_routes(homeShort, destShort, saveCSV="test")

quickDict = {
	"St. Mary's College of Maryland": "47645 College Dr, St Marys City"
}
dfQuick = pd.DataFrame.from_dict(quickDict, orient='index', columns=['address'])

quick_add(dfQuick, destShort, saveCSV="quickTest")


# testcoors = ((80.21787585263182,6.025423265401452),(80.23990263756545,6.018498276842677))
# testres = client.directions(testcoors)
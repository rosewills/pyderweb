#!/usr/bin/env python
'''
PyderWeb

Version: 0.1.1
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

# IMPORTS #
###########
# Basic Functions
import re				# regex support
import random			# generates random colors for plotting routes on maps
import math				# used when converting time to human-readable format
from time import sleep	# prevents flooding openrouteservice server with requests

# Data & Files
import pandas as pd		# reading in and working with dataframes
from shapely.geometry import Point
import folium			# generates maps
import json				# saves json files

# Geospatial Info
import geopandas as gpd
from geopandas.tools import geocode
from geopy.exc import GeocoderTimedOut	# handles errors due to geocoder taking too long to find a match
import openrouteservice					# Gets shortest route between two locations
from openrouteservice import convert	# decodes route data from openstreetmap for folium to interpret


# GEOCODING & ROUTES #
######################
gcService = 'GoogleV3'

keys = pd.read_csv("rw/rw-apikeys.csv",		# csv file listing personal api keys
					sep=",",				# character used to delimit columns
					quotechar='"',			# character used to quote strings
					skipinitialspace=True,	# True if a space is added after each column delimiter
					index_col="service")	# Name of column to be used as row labels
keyCol = "key"

gcKey = keys.at[gcService, keyCol]

# client = openrouteservice.Client(key='INSERT_OPENROUTESERVICE_API_KEY_HERE')	# Update key= field with your own Openrouteservice API key
client = openrouteservice.Client(key=keys.at["openrouteservice", keyCol])	# Update key= field with your own Openrouteservice API key
																				# Openrouteservice API keys are available (for free!) here: https://openrouteservice.org/plans/

# [NOTE] Choose your preferred Geocoder below (by uncommenting it)
# from geopy.geocoders import Nominatim			# Geocoder (Open-Source Option) - uses Openstreetmap
# from geopy.geocoders import GoogleV3			# Geocoder (Proprietary Option) - uses Google Maps API

# [NOTE] Choose the geolocator below that matches your geocoder (remember to update any API key fields to with your own key)
# geolocator = Nominatim(user_agent="pyderweb")	# user_agent field is arbitrary; can change if you like
# geolocator = GoogleV3(api_key='INSERT_GOOGLE_MAPS_API_KEY_HERE')	# Update api_key= field with your own Google Maps API key 
																	# Google Maps API keys are available here: https://developers.google.com/maps
# geolocator = GoogleV3(api_key=keys.at["GoogleV3", keyCol])


# INPUT DATA #
##############
# Read in CSV Files
homes = pd.read_csv("homes-demo.csv",		# csv file listing potential home names & addresses
					sep=",",				# character used to delimit columns
					quotechar='"',			# character used to quote strings
					skipinitialspace=True,	# True if a space is added after each column delimiter
					index_col="name")		# Name of column to be used as row labels

dests = pd.read_csv("dests-demo.csv",		# csv file listing potential destination names & addresses
					sep=",",				# character used to delimit columns
					quotechar='"',			# character used to quote strings
					skipinitialspace=True,	# True if a space is added after each column delimiter
					index_col="name")		# Name of column to be used as row labels

# Quick-Add Option
quickDict = {
	"St. Mary's College of Maryland": "47645 College Dr, St Marys City"
}

dfQuick = pd.DataFrame.from_dict(quickDict, orient='index', columns=['address'])


# FUNCTIONS #
#############

# [Optional] Pretty Colors for Terminal Errors (Bash-specific)
class colors:
	green = '\033[92m'
	blue = '\033[94m'
	yellow = '\033[93m'
	red = '\033[91m'
	bold = '\033[1m'
	endc = '\033[0m'

# [TEMPORARY HACK] Format labels for use in filenames ([to-fix] - there are better ways to do this)
def filename_formatter(name):
	fileName = name.replace(" ", "-")
	fileName = fileName.replace(".", "")
	fileName = fileName.replace(",", "")
	fileName = fileName.replace("'", "")
	return fileName

# Fetch Geocode
def get_geocode(address, name, attempt=1, maxAttempts=5):
	try:
		# location = geolocator.geocode(address)
		location = geocode(address, provider=gcService, api_key=gcKey)
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


def store_geocode(df):
	failcount = 0
	nameLen = 0
	gcDict = {}

	for name,info in df.iterrows():
		loc = get_geocode(info["address"],name)
		try:
			if "Error" in loc:
				print(colors.red+loc+colors.endc)
				raise Exception
			else:
				df.at[name, 'found'] = loc.address
				gcDict[name] = loc
				# df.at[name, 'data'] = loc
				locLat= str(round(loc.latitude,5))[:7]
				locLon = str(round(loc.longitude,5))[:7]
				print("...added", "("+locLat+","+locLon+")", name)
				if len(name) > nameLen:
					nameLen = len(name)
		except Exception as e:
			print(str(e))
			print(colors.red+"Geocoder could not locate", name, "(skipping)"+colors.endc)
			failcount += 1
	return df, gcDict, failcount, nameLen


# Fetch Route Data
def get_route(startLoc, endLoc, saveJson="None"):
	try:
		startCoorFlip = (startLoc.x, startLoc.y)
		endCoorFlip = (endLoc.x, endLoc.y)

	except Exception as e:
		errmess = colors.red+"ERROR [get_route]: unknown error >>>\t"+colors.red+str(e)+colors.endc
		return errmess

	coors = (startCoorFlip, endCoorFlip)
	res = client.directions(coors)		

	distance = round(res['routes'][0]['summary']['distance']/1609.34,1)
	duration = round(res['routes'][0]['summary']['duration']/60,1)
	
	# Save Route Data to .json File
	if saveJson != "None":
		with(open(saveJson+'.json','+w')) as f:
			f.write(json.dumps(res,indent=4, sort_keys=True))
	
	return coors, distance, duration


# Generate Results & Save Output Files
def get_data(dfStart, dfEnd, saveJsons="None", saveCSV="None", saveMap="None"):
	startLen = 1
	endLen = 1

	totalStart = len(dfStart)
	totalEnd = len(dfEnd)
	startFail = 0
	endFail = 0

	table = pd.DataFrame(index = dfStart.index)

	sGeocodes = geocode(dfStart['address'], provider=gcService, api_key=gcKey)
	eGeocodes = geocode(dfEnd['address'], provider=gcService, api_key=gcKey)

	sData = dfStart.join(sGeocodes, rsuffix="_gc")
	eData = dfEnd.join(eGeocodes, rsuffix="_gc")

	


	if startFail > 0 and endFail > 0:
		print(colors.bold+colors.green+str(totalStart-startFail)+"/"+str(totalStart), "homes &", str(totalEnd-endFail)+"/"+str(totalEnd), "destinations located."+colors.endc)
		print(colors.bold+colors.red+str(startFail), "homes &", str(endFail), "destinations skipped."+colors.endc)
	elif startFail > 0:
		print(colors.bold+colors.green+str(totalStart-startFail)+"/"+str(totalStart), "homes located. (All destinations found successfully.)"+colors.endc)
		print(colors.bold+colors.red+str(startFail), "homes skipped."+colors.endc)
	elif endFail > 0:
		print(colors.bold+colors.green+str(totalStart-endFail)+"/"+str(totalEnd), "destinations located. (All homes found successfully.)"+colors.endc)
		print(colors.bold+colors.red+str(endFail), "destinations skipped."+colors.endc)
	else:
		print(colors.bold+colors.green+"All locations found!"+colors.endc)
	
	for endName,info in eData.iterrows():
		cVals = random.choices(range(256), k=3)
		endColor = "rgb("+str(cVals[0])+","+str(cVals[1])+","+str(cVals[2])+")"
		print("color for", endName, endColor)
		eData.at[endName, 'color'] = endColor
	
	# Output Data Files
	for start,sInfo in sData.iterrows():
		print("Generating Route Data for ", start)

		if saveMap != "None":
			m = folium.Map(location=(sData.geometry[start].y, sData.geometry[start].x),zoom_start=7, control_scale=True,tiles="cartodbpositron")

		for end,eInfo in eData.iterrows():
			sleep(1)
			if saveJsons != "None":
				dataOut = get_route(eData[end], sData[start], saveJson=saveJsons+filename_formatter(start)+"-"+filename_formatter(end))
			else:
				dataOut = get_route(eData.geometry[end], sData.geometry[start])
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

				routeColor = eData.at[end, 'color']
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
		sData.to_csv(saveCSV+"-homes.csv")
		eData.to_csv(saveCSV+"-dests.csv")


# Quickly Get Data for One Home/Destination
def quick_add(dfAdd, dfExist, type="start", saveJsons="None", saveCSV="None", saveMap="None"):
	if type == "start":
		get_data(dfAdd, dfExist, saveJsons=saveJsons, saveCSV=saveCSV, saveMap=saveMap)
	elif type == "end":
		get_data(dfExist, dfAdd, saveJsons=saveJsons, saveCSV=saveCSV, saveMap=saveMap)
	else:
		print("Quick_Add() Error: type \""+type+"\" not understood. Please specify type as either \"start\" or \"end\" only.")



get_data(homes, dests, saveCSV="demo-output/demo", saveMap="demo-output/demo_")

#quick_add(dfQuick, dests, saveCSV="quickTest")
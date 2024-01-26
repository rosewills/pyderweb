#!/usr/bin/env python
'''
PyderWeb

Version: 0.0.0
Created: 2024-01-19 (by Rose Wills)
Status: not finished

This script takes a list of potential home addresses ("homes") and a list
of destination addresses ("dests"), and returns a csv file with the driving
distance (dis) and time (eta) between each home (1 row/home, 1 column/dest
with dis in miles, 1 column/dest with eta in minutes)

	- home addresses (rows)
	- driving distance to dest from home (1 column/dest)
	- driving time to dest from home

'''

import re
import random
import math
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


homes = { "University of Georgia": "101 Sanford Dr, Athens",
			"Delaware State University": "1200 N Dupont Hwy, Dover",
			"University of Pennsylvania": "3620 Walnut Street, Philadelphia",
			"University of Maryland": "620 W Lexington St, College Park",
			"Towson University": "8000 York Rd, Towson",
			"Johns Hopkins University": "3101 Wyman Park Drive, Baltimore",
			"Bowie State University": "14000 Jericho Park Rd, Bowie",
			"Loyola University Maryland": "4501 N. Charles Street, Baltimore",
			"Notre Dame of Maryland University": "4701 N Charles St, Baltimore",
			"Morgan State University": "1700 E Cold Spring Ln, Baltimore",
			"Coppin State University": "2500 W North Ave, Baltimore",
			"Maryland Institute College of Art": "1300 W Mount Royal Ave, Baltimore",
			"Goucher College": "949 Dulaney Valley Rd, Baltimore",
			"St. John's College": "60 College Ave, Annapolis",
			"United States Naval Academy": "121 Blake Rd, Annapolis",
			"Capitol Technology University": "11301 Springfield Rd, Laurel",
			"University of Maryland, Baltimore County": "1000 Hilltop Circle, Baltimore",
			"University of Baltimore": "1420 N Charles St, Baltimore",
			"University of Delaware": "210 S College Ave, Newark, DE 19711",
			"Baltimore City Community College": "2901 Liberty Heights Ave, Baltimore",
			"St. Mary's College of Maryland": "47645 College Dr, St Marys City" }

dests = { "BWI Departures": "7051 Friendship Rd, Baltimore",
			"Boyfriend": "698 N Atlantic Ave, Ocean City",
			"Brother's House": "2450 S Milledge Ave, Athens",
			"Family": "85554 Blue Rdg Pkwy, Bedford" }

homeShort = { "Delaware State University": "801 College Rd, Dover",
			 "University of Pennsylvania": "3620 Walnut Street, Philadelphia",
			 "University of Maryland": "7999 Regents Dr, College Park",
			 "University of Baltimore": "1420 N Charles St, Baltimore" }

destShort = { "Boyfriend": "698 N Atlantic Ave, Ocean City",
			 "Brother's House": "2450 S Milledge Ave, Athens",
			 "Family": "85554 Blue Rdg Pkwy, Bedford" }

quickAdd = { "St. Mary's College of Maryland": "47645 College Dr, St Marys City" }

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
	


def get_data(startLoc, endLoc):
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
	
	return coors, distance, duration

	# # Save Data (to .json)
	# with(open(startName+'-'+endName+'.json','+w')) as f:
	# 	f.write(json.dumps(res,indent=4, sort_keys=True))


def gen_table(startDict, endDict, csvName, mapDir, genMap=False):

	startLocs = {}
	endLocs = {}
	colorDict = {}
	startLen = 1
	endLen = 1
	# cols = []
	# for key in endDict.keys():
	# 	cols.append(re.split(' |\'', key)[0]+"-DIST")
	# 	cols.append(re.split(' |\'', key)[0]+"-TIME")
	table = pd.DataFrame(index = startDict.keys())

	for startName in startDict:
		startLoc = get_geocode(startDict[startName],startName)
		if "Error" in startLoc:
			print(colors.red+endLoc+colors.endc)
		else:
			startLocs[startName] = startLoc
			locLat= str(round(startLoc.latitude,5))[:7]
			locLon = str(round(startLoc.longitude,5))[:7]
			print("...added", "("+locLat+","+locLon+")", startName)
			if len(startName) > startLen:
				startLen = len(startName)

	for endName in endDict:
		endLoc = get_geocode(endDict[endName],endName)
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

		if genMap == True:
			m = folium.Map(location=(startLocs[start].latitude, startLocs[start].longitude),zoom_start=7, control_scale=True,tiles="cartodbpositron")

		for end in endLocs:
			sleep(1)
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


			if genMap == True:
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
		
		if genMap == True:
			mapName = start.replace(" ", "-")
			mapName = mapName.replace(".", "")
			mapName = mapName.replace(",", "")
			mapName = mapName.replace("'", "")
			mapFile = mapDir+mapName+".html"
			m.save(mapFile)
	print(table)
	table.to_csv(csvName+".csv")

gen_table(homeShort, destShort, "test", "saved-maps/")



# testcoors = ((80.21787585263182,6.025423265401452),(80.23990263756545,6.018498276842677))
# testres = client.directions(testcoors)
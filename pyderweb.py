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

import csv
import random
import math
from time import sleep
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
geolocator = Nominatim(user_agent="pyderweb")

import openrouteservice
from openrouteservice import convert
import folium
import json

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

# print(colors.purple, "purple",
# 	  colors.green, "green",
# 	  colors.blue, "blue",
# 	  colors.cyan, "cyan",
# 	  colors.yellow, "yellow",
# 	  colors.red, "red",
# 	  colors.endc, "endc",
# 	  colors.bold, "bold",
# 	  colors.underline, "underline",
# 	  colors.endc)

client = openrouteservice.Client(key='INSERT_OPENROUTESERVICE_API_KEY_HERE')
testcoors = ((80.21787585263182,6.025423265401452),(80.23990263756545,6.018498276842677))
testres = client.directions(testcoors)

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
			"Goucher College": "1021 Dulaney Valley Rd, Baltimore",
			"St. John's College": "60 College Ave, Annapolis",
			"United States Naval Academy": "121 Blake Rd, Annapolis",
			"Capitol Technology University": "11301 Springfield Rd, Laurel",
			"University of Maryland, Baltimore County": "1000 Hilltop Circle, Baltimore",
			"University of Baltimore": "1420 N Charles St, Baltimore",
			"University of Delaware": "210 S College Ave, Newark, DE 19711",
			"Baltimore City Community College": "2901 Liberty Heights Ave, Baltimore" }

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

center = dests["BWI Departures"]

destLocs = {}
homeLocs = {}



def get_geocode(address, name, attempt=1, maxAttempts=5):
	try:
		location = geolocator.geocode(address)
		# print(name+":",location.address)
		return location
		sleep(1)

	except GeocoderTimedOut:
		# print("GeocoderTimedOut for", address)
		if attempt <= maxAttempts:
			# print("timeout for", address+",","re-attempt #"+str(attempt))
			attempt = attempt + 1
			get_geocode(address, name, attempt)
		else:
			# print("giving up on", name, "("+address+")")
			errmess = colors.red+"ERROR [get_geocode]: GeocoderTimedOut >>> "+name+"\n\t"+colors.yellow+"giving up after 5 attempts."+colors.endc
			return errmess

	except AttributeError as e:
		# print("AttributeError for", address+":", e)
		errmess = colors.red+"ERROR [get_geocode]: AttributeError >>> "+name+"\n\t"+colors.yellow+str(e)+colors.endc
		return errmess

	except Exception as e:
		# print("Error:", name, "failed to run." )
		errmess = colors.red+"ERROR [get_geocode]: unknown error >>> "+name+"\n\t"+colors.yellow+str(e)+colors.endc
		return errmess
	
		# errmess = colors.red+"get_geocode("+name+") [AttributeError]\n\t"+colors.yellow+str(e)+colors.endc


def get_data(startLoc, startName, endLoc, endName):
	# startLoc = get_geocode(startPlace, startName)
	# endLoc = get_geocode(endPlace, endName)

	try:
		startCoor = (startLoc.latitude, startLoc.longitude)
		endCoor = (endLoc.latitude, endLoc.longitude)
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


# Get focus point of map
def gen_map(destDict, homeDict, focus, mapName):
	focusLoc = get_geocode(focus, focus+" (CENTER)")
	if "Error" in focusLoc:
		print(colors.red+focusLoc+colors.endc)
		return

	destLen = 1
	homeLen = 1

	for destName in destDict:
		destLoc = get_geocode(destDict[destName],destName)
		destLocs[destName] = destLoc
		print("...added", destName, "to destLocs")
		if len(destName) > destLen:
			destLen = len(destName)


	for homeName in homeDict:
		homeLoc = get_geocode(homeDict[homeName],homeName)
		if "Error" in homeLoc:
			print(colors.red+homeLoc+colors.endc)
		else:
			homeLocs[homeName] = homeLoc
			print("...added", homeName, "to homeLocs")
			if len(homeName) > homeLen:
				homeLen = len(homeName)

	# Generate Map
	m = folium.Map(location=(focusLoc.latitude, focusLoc.longitude),zoom_start=10, control_scale=True,tiles="cartodbpositron")

	for dest in destLocs:

		for home in homeLocs:
			# Get Data
			coors, distance, duration = get_data(homeLocs[home], home, destLocs[dest], dest)

			# Convert Time to Human-Readable
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

			# Fix Margins on Terminal Output Text
			homeMargin = " " * ( homeLen - len(home) )
			destMargin = " " * ( destLen - len(dest) )
			print(dest, destMargin, "<--", home, homeMargin, distance, "miles", "("+humanTime+")")

			geometry = client.directions(coors)['routes'][0]['geometry']
			decoded = convert.decode_polyline(geometry)

			routeName = home+" --> "+dest

			labeltxt = "<b><strong>"+routeName+"</strong></b></br>"
			distancetxt = "<b><strong>"+str(distance)+" miles </strong></b></br>"
			durationtxt = "<b><strong>"+str(duration)+" mins</strong></b>"

			cVals = random.choices(range(256), k=3)
			routeColor = "rgb("+str(cVals[0])+","+str(cVals[1])+","+str(cVals[2])+")"
			# print(routeColor)

			fillColor = routeColor
			color = routeColor
			# routeStyle = {'fillColor': routeColor, 'color': routeColor } # {'fillColor': '#00FFFFFF', 'color': '#00FFFFFF'} {'fillColor': '#228B22', 'color': '#228B22'}

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
				popup=home,
				icon=folium.Icon(color="green"),
			).add_to(m)

			folium.Marker(
				location=list(coors[1][::-1]),
				popup=dest,
				icon=folium.Icon(color="red"),
			).add_to(m)

			# print(colors.purple+home+colors.endc+" to "+colors.cyan+dest+colors.endc+" added to "+mapName)

			
	m.save(mapName+'.html')

gen_map(destShort, homeShort, center, "genmap-test")

		# else:
		# 	print(destName, "<-----", homeName+":", "<<< ERROR [unknown]: ", str(e), ">>>")

# for homePlace,homeName in umd:
# 	get_geocode(homePlace,homeName)

			# print(homeName+":",type(homeLoc))
			# print(homePlace, homeName, "----->", destPlace, destName)


# humanTime = str(math.floor(duration / 60)+"hrs, "+str(duration % 60)+"mins")

# print("Distance:", distance, "miles,", humanTime)


# # Generate Map
# distance_txt = "<h4> <b>Distance :&nbsp" + "<strong>"+str(distance)+" Km </strong>" +"</h4></b>"
# duration_txt = "<h4> <b>Duration :&nbsp" + "<strong>"+str(duration)+" Mins. </strong>" +"</h4></b>"

# m = folium.Map(location=startCoor,zoom_start=5, control_scale=True,tiles="cartodbpositron")

# folium.GeoJson(decoded).add_child(folium.Popup(distance_txt+duration_txt,max_width=300)).add_to(m)

# folium.Marker(
# 	location=list(coors[0][::-1]),
# 	popup="Home",
# 	icon=folium.Icon(color="green"),
# ).add_to(m)

# folium.Marker(
# 	location=list(coors[1][::-1]),
# 	popup="Dest",
# 	icon=folium.Icon(color="red"),
# ).add_to(m)


# m.save('map-rw.html')






# coors = ((39.95285175,-75.19578558111155),(38.61995497051513,-75.10309938399392))
# res = client.directions(coors)


# with(open('test-ex3.json','+w')) as f:
# 	f.write(json.dumps(testres,indent=4, sort_keys=True))





# for homePlace,homeName in umd:
# 	for destPlace,destName in destShort:
# 		# print(homePlace, homeName, "----->", destPlace, destName)
# 		get_route(homePlace, homeName, destPlace, destName)


# coors = ((int(startLoc.latitude), int(startLoc.longitude)), (int(endLoc.latitude), int(endLoc.longitude)))



# cat list-scratch | while read -r line; do echo $line | sed 's|^\(.*[(]\)\(".*"\)\(, \)\(".*"\)\(.*\)|\1\4\3\2\5|g' ; done

# homeList = [ ("101 Sanford Dr, Athens", "University of Georgia"),
# 			("1200 N Dupont Hwy, Dover", "Delaware State University"),
# 			("3620 Walnut Street, Philadelphia", "University of Pennsylvania"),
# 			("620 W Lexington St, College Park", "University of Maryland"),
# 			("8000 York Rd, Towson", "Towson University"),
# 			("3101 Wyman Park Drive, Baltimore", "Johns Hopkins University"),
# 			("14000 Jericho Park Rd, Bowie", "Bowie State University"),
# 			("4501 N. Charles Street, Baltimore", "Loyola University Maryland"),
# 			("4701 N Charles St, Baltimore", "Notre Dame of Maryland University"),
# 			("1700 E Cold Spring Ln, Baltimore", "Morgan State University"),
# 			("2500 W North Ave, Baltimore", "Coppin State University"),
# 			("1300 W Mount Royal Ave, Baltimore", "Maryland Institute College of Art"),
# 			("1021 Dulaney Valley Rd, Baltimore", "Goucher College"),
# 			("60 College Ave, Annapolis", "St. John's College"),
# 			("121 Blake Rd, Annapolis", "United States Naval Academy"),
# 			("11301 Springfield Rd, Laurel", "Capitol Technology University"),
# 			("1000 Hilltop Circle, Baltimore", "University of Maryland, Baltimore County"),
# 			("1420 N Charles St, Baltimore", "University of Baltimore"),
# 			("210 S College Ave, Newark, DE 19711", "University of Delaware"),
# 			("2901 Liberty Heights Ave, Baltimore", "Baltimore City Community College") ]

# destList = [ ("7051 Friendship Rd, Baltimore", "BWI Departures"),
# 			("698 N Atlantic Ave, Ocean City", "Boyfriend"),
# 			("2450 S Milledge Ave, Athens", "Brother's House"),
# 			("85554 Blue Rdg Pkwy, Bedford", "Family") ]

# homeShort = [ ("801 College Rd, Dover", "Delaware State University"),
# 			("3620 Walnut Street, Philadelphia", "University of Pennsylvania"),
# 			("7999 Regents Dr, College Park", "University of Maryland"),
# 			("1420 N Charles St, Baltimore", "University of Baltimore") ]

# destShort = [ ("698 N Atlantic Ave, Ocean City", "Boyfriend"),
# 			("2450 S Milledge Ave, Athens", "Brother's House"),
# 			("85554 Blue Rdg Pkwy, Bedford", "Family") ]

# hPlace,hName = ("3620 Walnut Street, Philadelphia", "University of Pennsylvania")
# dPlace,dName = ("698 N Atlantic Ave, Ocean City", "Boyfriend")

# umd = [ ("620 W Lexington St, College Park", "University of Maryland") ]
# upa = [ ("3620 Walnut Street, Philadelphia", "University of Pennsylvania") ]






# timeList = [ ("3620 Walnut Street, Philadelphia", "University of Pennsylvania"),
# 			("8000 York Rd, Towson", "Towson University"),
# 			("4701 N Charles St, Baltimore", "Notre Dame of Maryland University"),
# 			("2500 W North Ave, Baltimore", "Coppin State University"),
# 			("11301 Springfield Rd, Laurel", "Capitol Technology University") ]

# homeList = [ "University of Georgia Chapel, Herty Dr, Athens, GA 30602",
# 			"1200 N Dupont Hwy, Dover, DE 19901",
# 			"3620 Walnut Street, Philadelphia, PA 19104",
# 			"620 W Lexington St, Baltimore, MD 21201",
# 			"8000 York Rd, Towson, MD 21252",
# 			"3101 Wyman Park Drive, Baltimore, MD 21218",
# 			"14000 Jericho Park Rd, Bowie, MD 20715",
# 			"4501 N. Charles Street, Baltimore, MD 21210",
# 			"4701 N Charles St, Baltimore, MD 21210",
# 			"1700 E Cold Spring Ln, Baltimore, MD 21251",
# 			"2500 W North Ave, Baltimore, MD 21216",
# 			"1300 W Mount Royal Ave, Baltimore, MD 21217",
# 			"1021 Dulaney Valley Rd, Baltimore, MD 21204",
# 			"60 College Ave, Annapolis, MD 21401",
# 			"121 Blake Rd, Annapolis, MD 21402",
# 			"11301 Springfield Rd, Laurel, MD 20708",
# 			"1000 Hilltop Circle, Baltimore, MD 21250",
# 			"1420 N Charles St, Baltimore, MD 21202",
# 			"2901 Liberty Heights Ave, Baltimore, MD 21215",
#			"210 S College Ave, Newark, DE 19711" ]

# destList = [ "7051 Friendship Rd, Baltimore, MD 21240",
# 			"698 N Atlantic Ave, Ocean City, MD 21842",
# 			"2450 S Milledge Ave, Athens, MD 20636",
# 			"85554 Blue Rdg Pkwy, Bedford, PA 18508" ]
			
#			North Dupont Highway, Dover, Kent County, Delaware, 19901, United States
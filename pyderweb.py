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
from time import sleep
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
geolocator = Nominatim(user_agent="pyderweb")

def do_geocode(address, name, attempt=1, maxAttempts=5):
	try:
		# print("sleep")
		location = geolocator.geocode(address)
		print(name+":",location.address)
		sleep(1)

	except GeocoderTimedOut:
		if attempt <= maxAttempts:
			# print("timeout for", address+",","re-attempt #"+str(attempt))
			attempt = attempt + 1
			do_geocode(address, name, attempt)
		else:
			print("giving up on", name, "("+address+")")

	except AttributeError as e:
		print("Error for", address, e)

homeList = [ ("101 Sanford Dr, Athens", "University of Georgia"),
			("1200 N Dupont Hwy, Dover", "Delaware State University"),
			("3620 Walnut Street, Philadelphia", "University of Pennsylvania"),
			("620 W Lexington St, College Park", "University of Maryland"),
			("8000 York Rd, Towson", "Towson University"),
			("3101 Wyman Park Drive, Baltimore", "Johns Hopkins University"),
			("14000 Jericho Park Rd, Bowie", "Bowie State University"),
			("4501 N. Charles Street, Baltimore", "Loyola University Maryland"),
			("4701 N Charles St, Baltimore", "Notre Dame of Maryland University"),
			("1700 E Cold Spring Ln, Baltimore", "Morgan State University"),
			("2500 W North Ave, Baltimore", "Coppin State University"),
			("1300 W Mount Royal Ave, Baltimore", "Maryland Institute College of Art"),
			("1021 Dulaney Valley Rd, Baltimore", "Goucher College"),
			("60 College Ave, Annapolis", "St. John's College"),
			("121 Blake Rd, Annapolis", "United States Naval Academy"),
			("11301 Springfield Rd, Laurel", "Capitol Technology University"),
			("1000 Hilltop Circle, Baltimore", "University of Maryland, Baltimore County"),
			("1420 N Charles St, Baltimore", "University of Baltimore"),
			("2901 Liberty Heights Ave, Baltimore", "Baltimore City Community College") ]

destList = [ ("7051 Friendship Rd, Baltimore", "BWI Departures"),
			("698 N Atlantic Ave, Ocean City", "Boyfriend"),
			("2450 S Milledge Ave, Athens", "Brother's House"),
			("85554 Blue Rdg Pkwy, Bedford", "Family") ]

startLoc = ("3620 Walnut Street, Philadelphia", "University of Pennsylvania")
endLoc = ("698 N Atlantic Ave, Ocean City", "Boyfriend")

for loc,name  in homeList:
	# print(dest)
	do_geocode(loc, name)
	# location = geolocator.geocode(loc)
	# print(location.address)
	



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
# 			"2901 Liberty Heights Ave, Baltimore, MD 21215" ]

# destList = [ "7051 Friendship Rd, Baltimore, MD 21240",
# 			"698 N Atlantic Ave, Ocean City, MD 21842",
# 			"2450 S Milledge Ave, Athens, MD 20636",
# 			"85554 Blue Rdg Pkwy, Bedford, PA 18508" ]
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
from geopy.geocoders import Nominatim
geolocator = Nominatim()


homeList = [ "University of Georgia Chapel, Herty Dr, Athens, GA 30602",
            "1200 N Dupont Hwy, Dover, DE 19901",
			"Philadelphia, PA 19104",
			"620 W Lexington St, Baltimore, MD 21201",
			"8000 York Rd, Towson, MD 21252",
			"Baltimore, MD 21218",
			"14000 Jericho Park Rd, Bowie, MD 20715",
			"4501 N. Charles Street, Baltimore, MD 21210",
			"4701 N Charles St, Baltimore, MD 21210",
			"1700 E Cold Spring Ln, Baltimore, MD 21251",
			"2500 W North Ave, Baltimore, MD 21216",
			"1300 W Mount Royal Ave, Baltimore, MD 21217",
			"1021 Dulaney Valley Rd, Baltimore, MD 21204",
			"60 College Ave, Annapolis, MD 21401",
			"121 Blake Rd, Annapolis, MD 21402",
			"11301 Springfield Rd, Laurel, MD 20708",
			"1000 Hilltop Circle, Baltimore, MD 21250",
			"1420 N Charles St, Baltimore, MD 21202",
			"2901 Liberty Heights Ave, Baltimore, MD 21215" ]

destList = [ "BWI Departures, Maryland 21240",
            "698 N Atlantic Ave, Ocean City, MD 21842",
            "2450 S Milledge Ave, Athens, MD 20636",
            "85554 Blue Rdg Pkwy, Bedford, PA 18508" ]

for dest in destList:
    # print(dest)
    location = geolocator.geocode(dest)
    print(location.address)
    

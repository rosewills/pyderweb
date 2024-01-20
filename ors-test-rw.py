#!/usr/bin/env python


import openrouteservice
from openrouteservice import convert
from openrouteservice import geocode
import folium
import json

client = openrouteservice.Client(key='INSERT_OPENROUTESERVICE_API_KEY_HERE')

startLoc = "3620 Walnut Street, Philadelphia"
endLoc = "698 N Atlantic Ave, Ocean City"

startData = geocode.pelias_search(client,startLoc)
endData = geocode.pelias_search(client,endLoc)

with(open('test-start.json','+w')) as f:
	f.write(json.dumps(startData,indent=4, sort_keys=True))
with(open('test-end.json','+w')) as f:
	f.write(json.dumps(endData,indent=4, sort_keys=True))

startCoor = startData['features'][0]['geometry']['coordinates']
endCoor = endData['features'][0]['geometry']['coordinates']
coors = startCoor, endCoor
print(coors)
res = client.directions(coors)
# geometry = client.directions(coors)['routes'][0]['geometry']
# decoded = convert.decode_polyline(geometry)



# with(open('test-rw.json','+w')) as f:
# 	f.write(json.dumps(res,indent=4, sort_keys=True))

# testcoors = ((80.21787585263182,6.025423265401452),(80.23990263756545,6.018498276842677))
# testres = client.directions(testcoors)

# with(open('test-ex.json','+w')) as f:
# 	f.write(json.dumps(testres,indent=4, sort_keys=True))

# distance_txt = "<h4> <b>Distance :&nbsp" + "<strong>"+str(round(res['routes'][0]['summary']['distance']/1000,1))+" Km </strong>" +"</h4></b>"
# duration_txt = "<h4> <b>Duration :&nbsp" + "<strong>"+str(round(res['routes'][0]['summary']['duration']/60,1))+" Mins. </strong>" +"</h4></b>"

# m = folium.Map(location=startCoor,zoom_start=1, control_scale=True,tiles="cartodbpositron")
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


# m.save('map.html')




# print(startData, "("+startLoc+")")
# print(endData, "("+endLoc+")")

# coors = ((80.21787585263182,6.025423265401452),(80.23990263756545,6.018498276842677))
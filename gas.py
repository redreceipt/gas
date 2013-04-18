#! /usr/bin/env python
# This will calculate how much the user will spend on gas per month
"""
	This application will calculate how much you will spend on gas per month.
	It will ask for home address, work address, and year, make, and model of
	the vehicle being driven.
	
	API Credits:
	Google Maps Directions Matrix
	Google Maps Geocode
	myGasFeed.com
	fueleconomy.gov
"""

# TODO
#
# !2 	debug functions for user error
# !2 	debug functions for connection errors

# imports
import time
import urllib2 as url
import simplejson as json
from xml.etree import ElementTree as et
from PIL import Image

def _googleStrip(input):
	"""This will parse a string into Google Maps API format"""
	
	output = ""
	for char in input:
		if char not in (" ", ","):
			output += char
			plus = False
		else:
			if plus == False:
				output += "+"
				plus = True
	return output
	
def _processDistanceAPI(response):
		
	html = response.read()
	mapsJSON = json.loads(html)
	
	distanceStr = mapsJSON[u"rows"][0][u"elements"][0][u"distance"][u"text"]
	distance = int(float(distanceStr.split(" ")[0]))
	return distance
	
def _processGeocodeAPI(response):
		
	html = response.read()
	mapsJSON = json.loads(html)
	address = mapsJSON[u"results"][0][u"formatted_address"]
	addressParts = address.split(", ")
	name = addressParts[0] + ", " + addressParts[1] + ", " + addressParts[2][0:2]
	lat = float(mapsJSON[u"results"][0][u"geometry"][u"location"][u"lat"])
	long = float(mapsJSON[u"results"][0][u"geometry"][u"location"][u"lng"])
	return [name, lat, long]
		
def _processGasAPI(response):
		
	html = response.read()
	gasJSON = json.loads(html)
	
	totalPrice = 0
	noPrice = 0
	prices = []
	addresses = []
	for i, station in enumerate(gasJSON[u"stations"]):
		if station[u"reg_price"] != "N/A":
			
			price = float(station[u"reg_price"])
			date = station[u"reg_date"]
			address = station[u"address"] + " " + station[u"city"] + " " + station[u"region"]
			
			prices.append(price)
			addresses.append(address)
			
			totalPrice += price
			
		else: noPrice += 1
	avgPrice = totalPrice / (i + 1 - noPrice)
	return [avgPrice, prices, addresses]
	
def _processYearMenuAPI(response):

	html = response.read()
	root = et.fromstring(html)
	
	yearList = []
	for menuItem in root:
		if len(menuItem):
			yearList.append(menuItem[0].text)
	
	return [int(yearList[len(yearList) - 1]), int(yearList[0])]
	
def _processMakeMenuAPI(response):

	html = response.read()
	root = et.fromstring(html)
	
	makeList = []
	for menuItem in root:
		if len(menuItem):
			makeList.append(menuItem[0].text)
	
	return makeList
	
def _processModelMenuAPI(response):

	html = response.read()
	root = et.fromstring(html)
	
	modelList = []
	for menuItem in root:
		modelList.append(menuItem[0].text)
	
	return modelList
	
def _processModelTypeMenuAPI(response):

	html = response.read()
	root = et.fromstring(html)
	
	modelTypeList = []
	for menuItem in root:
		modelType = menuItem.find("text").text
		vehicleID = int(menuItem.find("value").text)
		modelTypeList.append([modelType, vehicleID])
	
	return modelTypeList
	
def _processFuelEconomyAPI(response):

	html = response.read()
	root = et.fromstring(html)
	
	return int(root.find("comb08").text)
	
def getDistance(startStr = "Start", endStr = "End", question = "How far?\n"):
	"""Gets the distance between two locations."""
	
	# ask for the origin and destination	
	startR = raw_input("%s address: " % startStr)
	endR = raw_input("%s address: " % endStr)
	
	# parse raw inputs
	start = _googleStrip(startR)
	end = _googleStrip(endR)
	
	# Google Maps Distance API - get distance to work
	request = "https://maps.googleapis.com/maps/api/distancematrix/json?origins="
	request += start
	request += "&destinations="
	request += end
	request += "&sensor=false&units=imperial"
	
	distance = 0
	try:
		print "Getting distance..."
		response = url.urlopen(request)
		distance = _processDistanceAPI(response)
		
		# build a static Google Map
		request = "http://maps.googleapis.com/maps/api/staticmap?size=480x480&markers=size:large%7Ccolor:red"
		request += "%7C" + start + "%7C" + end + "%7C&sensor=false"
		imgData = url.urlopen(request).read()
		
		# save map file
		f = open("./distance.png", "wb")
		f.write("")
		f.write(imgData)
		f.close()
		bmp = Image.open("./distance.png")
		
	except url.URLError:
		print "Can't connect to Google Maps"
		
		# ask for the distance to work in miles
		while True:
			try:
				distance = float(raw_input(question))
				break
			except ValueError:
				print "Please enter a number..."
	
	if startStr == "Home":
		return [start, end, distance]
		
	bmp.show()
	return distance
	
def getGasPrice(locationR = "Columbia, SC"):
	"""Gets the average gas price."""
	
	try:
		location = _googleStrip(locationR)

		# Google Maps Geocode API - get lat/long and name of home address
		request = "https://maps.googleapis.com/maps/api/geocode/json?address="
		request += location
		request += "&sensor=false&units=imperial"
		response = url.urlopen(request)
		homeList = _processGeocodeAPI(response)

		# myGasFeed API - get prices of gas near home address
		lat = str(homeList[1])
		long = str(homeList[2])
		radius = "5"
		type = "reg" # [reg|mid|pre|diesel]
		apiKey = "fk6pblixp6"
		request = "http://api.mygasfeed.com/stations/radius/" 
		request += lat + "/" + long + "/" + radius + "/" + type + "/price/" + apiKey + ".json"
		
		print "Getting gas prices..."
		response = url.urlopen(request)
		gasData = _processGasAPI(response)
		price = gasData[0]
		print "The average price of gas near {0} is ${1:.2f}".format(homeList[0], price)
		
		# build a static Google Map
		request = "http://maps.googleapis.com/maps/api/staticmap?size=480x480&markers=size:medium%7Ccolor:green"
		for i, address in enumerate(gasData[2]):
			request += "%7C" + _googleStrip(address)
			if i == 4: break
		request += "%7C&sensor=false"
		imgData = url.urlopen(request).read()
		
		# save map file
		f = open("./stations.png", "wb")
		f.write("")
		f.write(imgData)
		f.close()
		bmp = Image.open("./stations.png")
		
	except url.URLError:
		print "Can't connect to Google Maps and myGasFeed.com"
		
		# ask for price of gas
		while True:
			try:
				price = float(raw_input("How much does gas cost? "))
				break
			except ValueError:
				print "Please enter a number..."
	
	print ("Showing the 5 cheapest stations near you...")
	bmp.show()
	return price
	
def getMPG():
	"""Gets the fuel economy of your vehicle."""
	
	try:
		# ask for year
		request = "http://www.fueleconomy.gov/ws/rest/vehicle/menu/year"
		response = url.urlopen(request)
		years = _processYearMenuAPI(response)
		
		while True:
			try:
				year = int(raw_input("What is the year of your vehicle? "))
				if year < years[0] or year > years[1]:
					print "Year must be between {0} and {1}.".format(years[0], years[1])
					continue
				break
			except ValueError:
				print "Please enter a year..."
	
		# get list of makes
		print "Getting list of makes..."		
		request = "http://www.fueleconomy.gov/ws/rest/vehicle/menu/make?year={0}".format(year)
		response = url.urlopen(request)
		makeList = _processMakeMenuAPI(response)
		
		# let the user help find the make
		userMake = raw_input("What is the make of your vehicle (Press 'Enter' to see full list)? ")
		userMakeList = []
		for makeOption in makeList:
			if userMake == "":
				userMakeList = makeList
				break
			if makeOption[0].upper() == userMake[0].upper():
				userMakeList.append(makeOption)
				
		if userMakeList == []: userMakeList = makeList
		
		# list out make choices
		for i, make in enumerate(userMakeList):
			print "[" + str(i + 1) + "] " + make
		
		# choose the make from the list
		while True:
			try:
				choice = int(raw_input("Choose your make by number: "))
				if choice < 1 or choice > len(userMakeList):
					print "That's not a choice!"
					continue
				make = userMakeList[choice - 1]
				makeURL = make.replace(" ", "%20")
				break
			except ValueError:
				print "Please enter a number..."
			
		request = "http://www.fueleconomy.gov/ws/rest/vehicle/menu/model?year="
		request += str(year) + "&make=" + makeURL
	
		# get list of models
		print "Getting list of", make[0].upper() + make[1:], "models..."
		response = url.urlopen(request)
		modelList = _processModelMenuAPI(response)
		
		# let the user help find the model
		userModel = raw_input("What is the model of your vehicle (Press 'Enter' to see full list)? ")
		userModelList = []
		for modelOption in modelList:
			if userModel == "":
				userModelList = modelList
				break
			if modelOption[0].upper() == userModel[0].upper():
				userModelList.append(modelOption)
				
		if userModelList == []: userModelList = modelList
		
		# list out model choices
		for i, model in enumerate(userModelList):
			print "[" + str(i + 1) + "] " + model
		
		# choose the model from the list
		while True:
			try:
				choice = int(raw_input("Choose your model by number: "))
				if choice < 1 or choice > len(userModelList):
					print "That's not a choice!"
					continue
				model = userModelList[choice - 1]
				modelURL = model.replace(" ", "%20")
				break
			except ValueError:
				print "Please enter a number..."
		
		# get the list of model types
		request = "http://www.fueleconomy.gov/ws/rest/vehicle/menu/options?year="
		request += str(year) + "&make=" + make + "&model=" + modelURL
		print "Getting list of", make[0].upper() + make[1:], model, "types..."
		response = url.urlopen(request)
		modelTypeList = _processModelTypeMenuAPI(response)
		
		# list out model type choices
		for i, modelTypePair in enumerate(modelTypeList):
			print "[" + str(i + 1) + "] " + modelTypePair[0]
		
		# choose the model type from the list
		while True:
			try:
				choice = int(raw_input("Choose your model type by number: "))
				if choice < 1 or choice > len(modelTypeList):
					print "That's not a choice!"
					continue
				modelID = modelTypeList[choice - 1][1]
				break
			except ValueError:
				print "Please enter a number..."
		
		# get the EPA vehicle data
		request = "http://www.fueleconomy.gov/ws/rest/vehicle/"
		request += str(modelID)
		print "Getting data for your", make, model + "..."
		response = url.urlopen(request)
		fuelEfficiency = _processFuelEconomyAPI(response)
		print "Your", make, model, "gets an estimated", str(fuelEfficiency), "MPG"
		
	except url.URLError:
		print "Can't connect to fueleconomy.gov"
		
		# ask for fuel efficiency
		while True:
			try:
				fuelEfficiency = float(raw_input("What is the fuel efficiency of your vehicle? (MPG): "))
				break
			except ValueError:
				print "Please enter a number..."

	return fuelEfficiency
	
def getExpenses():
	"""Calculates cost of fuel per month using commute to work."""
	
	distanceList = getDistance("Home", "Work", "How many miles to work? ")
	home = distanceList[0]
	work = distanceList[1]
	distanceToWork = distanceList[2]
	
	# ask for other destinations
	otherDistance = 0;
	while True:
		choice = raw_input("Are you going anywhere else this month? (y/n): ")
		if choice in ("n", "N", "no"): break
		elif choice not in ("y", "Y", "yes"):
			print "Yes or no!"
			continue
		else:
			otherDistance += getDistance()
	
	# add up various driving distances
	print "Adding round trip distance to work every day for four weeks..."
	time.sleep(1)
	if otherDistance: print "Adding other destination round trips..."
	time.sleep(1)
	distance = distanceToWork * 40 + otherDistance
	print "You will travel", distance, "miles"
					
	priceOfGas = getGasPrice(home)
	fuelEfficiency = getMPG()
	
	# calculate cost
	print "Calculating total gallons of gas used..."
	gallons = distance / fuelEfficiency
	cost = priceOfGas * gallons
	print "You will spend ${0:.2f} on fuel per month".format(cost)
	
if __name__ == "__main__":
	getExpenses()
	
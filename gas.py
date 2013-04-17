#! /usr/bin/env python
##############################################
# Copyright 2013 Michael Neeley
#
# See the file LICENSE for copying permission.
##############################################


# gas.py will help calculate how much you will spend on gas per month

# library imports
import urllib2

def getExpenses():
	"""Calculates cost of fuel in one month (four weeks)."""
	
	# ask for the distance to work in miles
	while True:
		try:
			distanceToWork = float(raw_input("How many miles to work?\n"))
			break
		except ValueError:
			print "Please enter a number..."
			
	# ask for other destinations
	otherDistance = 0;
	while True:
		choice = raw_input("Are you going anywhere else this month? (y/n)\n")
		if choice in ("n", "N", "no"): break
		elif choice not in ("y", "Y", "yes"):
			print "Yes or no!"
			continue
		else:
			while True:
				try:
					otherDistance += float(raw_input("How far one way?\n")) * 2
					break
				except ValueError:
					print "Please enter a number..."
					
	# ask for price of gas
	while True:
		try:
			priceOfGas = float(raw_input("How much does gas cost?\n"))
			break
		except ValueError:
			print "Please enter a number..."
			
	# ask for fuel efficiency
	while True:
		try:
			fuelEfficiency = float(raw_input("What is the fuel efficiency of your vehicle? (MPG)\n"))
			break
		except ValueError:
			print "Please enter a number..."
			
	# calculate cost
	print "Adding round trip distance to work every day for four weeks..."
	if otherDistance: print "Adding other destinations..."
	distance = distanceToWork * 40 + otherDistance
	print "Calculating total gallons of gas used..."
	gallons = distance / fuelEfficiency
	cost = priceOfGas * gallons
	print "You will spend ${0:.2f} on fuel per month".format(cost)
	
def googleStrip(input):
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
	
def getMapsRequest():
	"""This function writes a location into a URL Request."""
	
	# ask for the origin and destination
	startR = raw_input("Start address: ")
	endR = raw_input("End address: ")
	
	# parse raw inputs
	start = googleStrip(startR)
	end = googleStrip(endR)
	
	# piece together the request
	request = "https://maps.googleapis.com/maps/api/distancematrix/json?origins="
	request += start
	request += "&destinations="
	request += end
	request += "&sensor=false&units=imperial"
	
	print request
	
def test():
	getMapsRequest()
	
def main():
	getExpenses()

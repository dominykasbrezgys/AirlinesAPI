import sys
from Client import Client
import requests
import json

def main():


	baseURL = "http://sc14db.pythonanywhere.com"
	c = Client(baseURL)

	c.findFlight()
	c.bookFlight()
	c.paymentMethods()
	c.payForBooking()
	c.finalizeBooking()
	c.bookingStatus()
	# c.cancelBooking()

	# List all payment service provider companies
	#URL = "http://directory.pythonanywhere.com"
	#try:
	#	res = requests.get(URL+"/api/list/", json = {'company_type':'airline'})
	#except requests.ConnectionError as e:
	#	print("Connection error: {0}".format(e))
	#	sys.exit(1)

	#print (res.text)


if __name__ == "__main__":
    # execute only if run as a script
    main()

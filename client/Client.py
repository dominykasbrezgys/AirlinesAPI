import sys
import requests
import json


class Client:

	def __init__(self, baseURL):
		self.baseURL = baseURL
		self.numberOfPassengers = None
		self.booking_num = None
		self.tot_price = None
		self.pay_provider_id = None
		self.invoice = None

	'''
	FIND FLIGHT
	'''
	def findFlight(self):

		#1. User needs to enter all flight details
		#For sc14db.pythonanywhere.com use the following details to test the API:
		# y = 2018
		# m = 7
		# d = 1
		# dep_airport: Vilnius VNO
		# dest_airport: Heathrow London LHR
		# numberOfPassenger: 2
		# is_flex = y
		print("Please enter the date of you flight: ")
		y = input("Year: ")
		m = input("Month: ")
		d = input("Day: ")
		dep_date = y+"-"+m+"-"+d
		print("Please enter the departure and destination airports (e.g. New York JFK): ")
		dep_airport = input("Departure: ")
		dest_airport = input("Destination: ")
		self.numberOfPassengers = int(input("Please enter a number of passengers: "))
		is_flex = input("Flexible? (y/n): ")
		
		if is_flex=='y':
			is_flex = True
		elif is_flex=='n':
			is_flex == False
		else:
			print("Wrong value for is_flex")
			sys.exit(1)
			
		payload = {
			'dep_airport' : dep_airport,
			'dest_airport' : dest_airport,
			'dep_date' : dep_date,
			'num_passengers' : self.numberOfPassengers,
			'is_flex' : True
		}

		#2. Sends a request to the airline wit user specified details
		try:
			res = requests.get(self.baseURL+"/api/findflight/", json = payload)
		except requests.ConnectionError as e:
			print("Connection error: {0}".format(e))
			sys.exit(1)

		if (res.status_code != 200):
			print (res.reason+" ("+str(res.status_code)+")")
			if res.status_code != 500:
				print (res.text)
			sys.exit(1)

		responsePayload = json.loads(res.text)
		flights = responsePayload['flights']

		#3 Listing all the flights
		print ("Found these flights:\n")

		for flight in flights:
			print ("Flight id: "+ str(flight['flight_id']))
			print ("Flight No: "+str(flight['flight_num']))
			print ("Departure: "+str(flight['dep_airport']))
			print ("Destination: "+str(flight['dest_airport'])) 
			print ("Departure date/time: "+str(flight['dep_datetime'])) 
			print ("Arrival date/time: "+str(flight['arr_datetime'])) 
			print ("Flight duration: "+str(flight['duration']))
			print ("Flight price: "+str(flight['price']) +"\n")

	'''
	2. BOOK FLIGHT
	'''
	def bookFlight(self):

		#1. User selects a flight ID he/she wants to book and enters details about each passenger
		flightID = input("Select ID of a flight you want to book: ")
		print ("Please enter details about each passenger: ")
		passengers = []
		passenger = {}
		for i in range(1,self.numberOfPassengers+1):
			print ("Passenger " + str(i)+":")
			firstName = input("First Name: ")
			surname = input("Surname: ")
			email = input("Email: ")
			phoneNumber = input("Phone number: ")
			print("\n")
			
			#firstName = "Name"+str(i)
			#surname = "Surname"+str(i)
			#email = "email" + str(i) + "@gmail.com"
			#phoneNumber = "000000000" + str(i)

			passenger['first_name'] = firstName
			passenger['surname'] = surname
			passenger['email'] = email
			passenger['phone'] = phoneNumber

			passengers.append(passenger)
			passenger = {}

		#2. Sending the details to the airlines service
		payload = {"flight_id" : flightID , "passengers" : passengers}

		try:
			res = requests.post(self.baseURL+"/api/bookflight/", json = payload)
		except requests.ConnectionError as e:
			print("Connection error: {0}".format(e))
			sys.exit(1)

		#Expecting a response 201 CREATED
		if (res.status_code != 201):
			print (res.reason+" ("+str(res.status_code)+")")
			if res.status_code != 500:
				print(res.text)
			sys.exit(1)

		res_payload = json.loads(res.text)
		self.booking_num = res_payload['booking_num']
		self.tot_price = res_payload['tot_price']

	'''
	3. GET PAYMENT METHODS
	'''
	def paymentMethods(self):
		try:
			res = requests.get(self.baseURL+"/api/paymentmethods/")
		except requests.ConnectionError as e:
			print("Connection error: {0}".format(e))
			sys.exit(1)

		#Expecting status code 200 OK
		if (res.status_code != 200):
			print (res.reason+" ("+str(res.status_code)+")")
			if res.status_code != 500:
				print (res.text)
			sys.exit(1)

		responsePayload = json.loads(res.text)
		providers = responsePayload['pay_providers']

		for provider in providers:
			print ("Payment provider ID: "+ str(provider['pay_provider_id']))
			print ("Payment provider name: "+str(provider['pay_provider_name'])+'\n')
			
		#Only one payment provider is available with sc14db.pythonanywhere.com
		pay_provider_id = input("Please select id from the above payment providers: ")

		self.pay_provider_id = pay_provider_id 

	'''
	4. PAY FOR THE BOOKING
	'''
	def payForBooking(self):
		#1. Get an invoice from the airline company
		payload = {'booking_num': self.booking_num, 'pay_provider_id': self.pay_provider_id}
		try:
			res = requests.post(self.baseURL+"/api/payforbooking/", json = payload)
		except requests.ConnectionError as e:
			print("Connection error: {0}".format(e))
			sys.exit(1)

		invoice = json.loads(res.text)

		#2. User needs to log in to the account of payment service provider
		# You can use the following credentials to test sc14db.pythonanywhere.com
		# 	'username' : 'john',
		# 	'password' : 'password123'
		print('PLease log in to your bank account:')
		username = input('Username: ')# NOTE: use raw_input() with Python 2.7
		password = input('Password: ')
		payload = {'username': username, 'password' : password }

		s = requests.Session()
		try:
			res = s.post(invoice['url']+"/api/login/", data = payload, headers={'Content-Type':'application/x-www-form-urlencoded'})
		except requests.ConnectionError as e:
			print("Connection error: {0}".format(e))
			sys.exit(1)

		if (res.status_code != 200):
			print (res.reason+" ("+str(res.status_code)+")")
			print(res.text)
			sys.exit(1)

		print('LOGIN SUCCESSFUL!')

		#3 Pay the invoice
		payload = {'payprovider_ref_num' : invoice['invoice_id'], 
					#'client_ref_num': invoice['booking_num'],
					'client_ref_num' : invoice['booking_num']+'_PAYMENT',
					'amount': self.tot_price}
		try:
			res = s.post(invoice['url']+"/api/payinvoice/", json = payload)
		except requests.ConnectionError as e:
			print("Connection error: {0}".format(e))
			sys.exit(1)

		#4. Check if the payment's gone through
		if (res.status_code != 201):
			print('Something went wrong with your payment!')
			print(res.reason+" ("+str(res.status_code)+")")
			print(res.text)
			sys.exit(1)

		print('Payment successful!')

		res_payload = json.loads(res.text)
		self.stamp = res_payload['stamp_code']

	def finalizeBooking(self):
		payload = {'booking_num': self.booking_num, 
					'pay_provider_id': self.pay_provider_id,
					'stamp': self.stamp
					}
		try:
			res = requests.post(self.baseURL+"/api/finalizebooking/", json = payload)
		except requests.ConnectionError as e:
			print("Connection error: {0}".format(e))
			sys.exit(1)

		if (res.status_code != 201):
			print (res.reason+" ("+str(res.status_code)+")")
			print(res.text)
			sys.exit(1)

		res_payload = json.loads(res.text)

		if (res_payload['booking_status'] == 'CONFIRMED'):
			print ('Your booking is now confirmed!')
		else:
			print('Something went wrong...')
			print('Status: '+res_payload['booking_status'])

	def bookingStatus(self):
		try:
			res = requests.get(self.baseURL+"/api/bookingstatus/", json = {'booking_num': self.booking_num})
		except requests.ConnectionError as e:
			print("Connection error: {0}".format(e))
			sys.exit(1)

		print(res.text)

	def cancelBooking(self):
		try:
			res = requests.get(self.baseURL+"/api/cancelbooking/", json = {'booking_num': self.booking_num})
		except requests.ConnectionError as e:
			print("Connection error: {0}".format(e))
			sys.exit(1)

		print (res.text)

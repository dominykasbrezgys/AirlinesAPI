from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .models import *
from datetime import datetime, date, timedelta
import time
import json
import requests

def findFlight(request):
	if request.method != 'GET':
		HttpResponse('This url only accepts GET request!', status = 503)

	requestPayload = json.loads(request.body)
	#1. Check if the request payload contain all required data
	try:
		depAirport = requestPayload['dep_airport']
		destAirport = requestPayload['dest_airport']
		departureDate = requestPayload['dep_date'].split("-")
		numberOfPassengers = requestPayload['num_passengers']
		isFlex = requestPayload['is_flex']
	except KeyError as e:
		return HttpResponse('ERROR: Request findflights must provide: '+str(e) , status = 503)

	#2. Check if requested seats is equal to or greater than 1
	if (numberOfPassengers<1):
		return HttpResponse('ERROR: Please give a valid num_passengers',status = 503)

	day = int(departureDate[2])
	month = int(departureDate[1])
	year = int(departureDate[0])

	#3. Check if date format is correct
	try:
		departureDate = date(year, month, day)
	except ValueError as e:
		return HttpResponse("ERROR: "+str(e), status = 503)

	#4. Filter all flights according to client's preference
	results = Flight.objects.filter(
		departureDateTime__date = departureDate,
		departureAirport__name = requestPayload['dep_airport'], 
		destinationAirport__name = requestPayload['dest_airport'] )

	#5. If no flights found - response with 503: Service Unuavailable 
	if (results.count() == 0):
		return HttpResponse("Couldn't find any flights for "+requestPayload['dep_date']+"\nPlease pick another date!", status = 503)

	#Converting QuerySet to appropriate serializable
	flightsList = []
	flight = {}
	for result in results:
		#Check if there are seats available before adding it to the response payload
		if (result.seatsLeft<numberOfPassengers):
			continue
		flight['flight_id'] = result.id
		flight['flight_num'] = result.flightNumber
		flight['dep_airport'] = result.departureAirport.name
		flight['dest_airport'] = result.destinationAirport.name
		flight['dep_datetime'] = str(result.departureDateTime)
		flight['arr_datetime'] = str(result.arrivalDateTime)
		flight['duration'] = str(result.duration)
		flight['price'] = result.seatPrice
		flightsList.append(flight)
		flight = {}

	return HttpResponse(json.dumps({"flights": flightsList}), content_type="application/json")

#Too allow POST requests
@csrf_exempt
def bookFlight(request):
	if request.method != 'POST':
		HttpResponse('This url only accepts POST request!', status = 503)

	requestPayload = json.loads(request.body)
	#1. Check if the request payload contain all required data
	try:
		flightID = requestPayload['flight_id']
		passengers = requestPayload['passengers']
	except KeyError as e:
		return HttpResponse('ERROR: Request book flight must provide: '+str(e) , status = 503)

	seatsRequested = len(requestPayload['passengers'])

	#2. Check if selected flight exists
	try:
		flight = Flight.objects.get(id = flightID)
	except ObjectDoesNotExist:
		return HttpResponse("ERROR: No such flight, please select the correct flight ID!",status=503)

	#3. Update a value of seats left for the flight
	flight.seatsLeft -= seatsRequested
	flight.save()

	print (flight.seatsLeft)

	#4. If enough seats, make a booking
	numberOfBookings = Booking.objects.all().count()
	bookingID = ("BOOKING"+str(numberOfBookings+1))

	booking = Booking.objects.create(
		bookingNumber = bookingID,
		flight = flight,
		numberOfSeats = seatsRequested,
		invalidAtDateTime = datetime.now() + timedelta(hours = 1)
	 	)

	booking.save()

	#5. Add passengers to a booking
	for passenger in passengers:
		p = Passenger.objects.create(
			firstName = passenger['first_name'],
			surname = passenger['surname'],
			email = passenger['email'],
			phoneNumber = passenger['phone']
			)
		p.save()
		booking.passengers.add(p)

	#6. Calculate total price of a booking
	tot_price = flight.seatPrice * seatsRequested
	return HttpResponse(json.dumps({"booking_num": booking.bookingNumber, "booking_status":booking.status,"tot_price":tot_price}),status = 201)

def paymentMethods(request):

	paymentProviders = PaymentProvider.objects.all()

	if (paymentProviders.count() == 0):
		return HttpResponse("No payment providers currently available", status = 503)

	#Converting QuerySet to appropriate serializable
	providersList = []

	for provider in paymentProviders:
		providersList.append({'pay_provider_id': provider.id, 'pay_provider_name': provider.name})

	return HttpResponse(json.dumps({"pay_providers": providersList}), content_type="application/json", status =200)

@csrf_exempt
def payForBooking(request):
	if request.method != 'POST':
		HttpResponse('This url only accepts POST request!', status = 503)

	requestPayload = json.loads(request.body)
	#1. Check if the request payload contain all required data
	try:
		pay_provider_id = requestPayload['pay_provider_id']
		booking_num = requestPayload['booking_num']
	except KeyError as e:
		return HttpResponse('ERROR: Request payForBooking must provide: '+str(e) , status = 503)

	#2. Check if objects exist in the database
	try:
		pay_provider = PaymentProvider.objects.get(id = pay_provider_id)
		booking = Booking.objects.get(bookingNumber = booking_num)
	except ObjectDoesNotExist:
		return HttpResponse("ERROR: No such payment provider or booking!",status=503)

	#3. Check if booking status is ONHOLD

	if booking.status != 'ONHOLD':
		return HttpResponse('Cannot proceed with the payment. Booking status: '+booking.status, status = 503)

	#4. Log in to the payment service provider server using session
	login_payload = {'username':pay_provider.loginName, 'password' : pay_provider.loginPassword }
	s = requests.Session()
	try:
		res = s.post(pay_provider.address+"/api/login/", data = login_payload, headers={'Content-Type':'application/x-www-form-urlencoded'})
	except requests.ConnectionError as e:
		print("Connection error: {0}".format(e))
		return HttpResponse("ERROR: Couldn't connect to "+pay_provider.name+" payment service provider!", status=503)
		sys.exit(1)

	#5. Request the creation of an electronic invoice

	#Reference number for this invoice at the airlines side
	refLocal = booking.bookingNumber+'_PAYMENT'

	#Calculate amount that needs to be paid
	amount = booking.numberOfSeats * booking.flight.seatPrice

	payload = {'account_num': pay_provider.accountNumber,
			'client_ref_num' : refLocal,
			'amount': amount}
	try:
		res = s.post(pay_provider.address+"/api/createinvoice/", json = payload)
	except requests.ConnectionError as e:
		print("Connection error: {0}".format(e))
		return HttpResponse("ERROR: Couldn't connect to "+pay_provider.name+" payment service provider!", status=503)
		sys.exit(1)

	print (res.text)
	res_payload = json.loads(res.text)
	#6. Store the invoive in aitlines database
	invoice = Invoice.objects.create(
		refLocal = refLocal,
		refExternal = res_payload['payprovider_ref_num'],
		booking = booking,
		amount = amount,
		wasPaid = False,
		stamp = res_payload['stamp_code']
		)

	#7. Send response to client

	#response described in CWK description:
	response_payload = {'pay_provider_id': pay_provider.id, 
						'invoice_id': invoice.refExternal,
	 					'booking_num': booking.bookingNumber,
	 					'url' : pay_provider.address}

	#response that would make more sense:
	# response_payload = {'pay_provider_ref_num': invoice.refExternal, 
	# 					'airline_ref_num': invoice.refLocal,
	#  					'booking_num': booking.bookingNumber,
	#  					'amount' : invoice.amount,
	#  					'url' : pay_provider.address }

	return HttpResponse(json.dumps(response_payload), content_type="application/json",status =201)

@csrf_exempt
def finalizeBooking(request):
	if request.method != 'POST':
		HttpResponse('This url only accepts POST request!', status = 503)

	requestPayload = json.loads(request.body)
	#1. Check if the request payload contain all required data
	try:
		booking_num = requestPayload['booking_num']
		pay_provider_id = requestPayload['pay_provider_id']
		stamp = requestPayload['stamp']
	except KeyError as e:
		return HttpResponse('ERROR: Request finalize booking must provide: '+str(e) , status = 503)

	#2. Verify electronic stamp
	try:
		booking = Booking.objects.get(bookingNumber = booking_num)
	except ObjectDoesNotExist:
		return HttpResponse("ERROR: No such booking!",status=503)

	try:
		invoice = Invoice.objects.get(stamp = stamp)
	except ObjectDoesNotExist:
		return HttpResponse("ERROR: Stamp doesn't match!",status=503)

	#3. Change state of booking and the invoice
	booking.status = 'CONFIRMED'
	invoice.wasPaid = True
	booking.save()
	invoice.save()

	response_payload = {'booking_num':booking.bookingNumber, 'booking_status': booking.status}
	return HttpResponse(json.dumps(response_payload), content_type="application/json",status = 201)

def bookingStatus(request):
	if request.method != 'GET':
		HttpResponse('This url only accepts GET request!', status = 503)

	requestPayload = json.loads(request.body)
	#1. Check if the request payload contain all required data
	try:
		booking_num = requestPayload['booking_num']
	except KeyError as e:
		return HttpResponse('ERROR: Request finalize booking must provide: '+str(e) , status = 503)

	#2. Check if the booking exists
	try:
		booking = Booking.objects.get(bookingNumber = booking_num)
	except ObjectDoesNotExist:
		return HttpResponse("ERROR: No such booking!",status=503)

	response_payload = {'booking_num': booking.bookingNumber,
						'booking_status': booking.status,
						'flight_num': booking.flight.flightNumber,
						'dep_airport': booking.flight.departureAirport.name,
						'dest_airport': booking.flight.destinationAirport.name,
						'dep_datetime': str(booking.flight.departureDateTime),
						'arr_datetime': str(booking.flight.arrivalDateTime),
						'duration': booking.flight.duration}

	return HttpResponse(json.dumps(response_payload), content_type="application/json",status = 200)

@csrf_exempt
def cancelBooking(request):
	if request.method != 'POST':
		HttpResponse('This url only accepts POST request!', status = 503)

	requestPayload = json.loads(request.body)
	#1. Check if the request payload contain all required data
	try:
		booking_num = requestPayload['booking_num']
	except KeyError as e:
		return HttpResponse('ERROR: Request finalize booking must provide: '+str(e) , status = 503)

	#2. Check if the booking exists
	try:
		booking = Booking.objects.get(bookingNumber = booking_num)
	except ObjectDoesNotExist:
		return HttpResponse("ERROR: No such booking!",status=503)

	#3. change state of the booking
	if booking.status != 'ONHOLD':
		return HttpResponse('Cannot cancel this booking. Booking status: '+booking.status, status = 503)

	booking.status = 'CANCELLED'
	booking.save()

	response_payload = {'booking_num': booking.bookingNumber,
						'booking_status': booking.status}

	return HttpResponse(json.dumps(response_payload), content_type="application/json", status = 201)

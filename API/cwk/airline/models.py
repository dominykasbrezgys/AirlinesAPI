from django.db import models

#MODELS for the airline

class Aircraft(models.Model):
	aircraftType = models.CharField(max_length = 30)
	tailNumber = models.CharField(max_length = 30)
	numberOfSeats = models.IntegerField()

class Airport(models.Model):
	name = models.CharField(max_length = 30)
	country = models.CharField(max_length = 30)
	timeZone = models.CharField(max_length = 30)

class Flight(models.Model):
	flightNumber = models.CharField(max_length = 6) #i.e. DOM123
	departureAirport = models.ForeignKey(Airport, on_delete = models.CASCADE, related_name='departure')
	destinationAirport = models.ForeignKey(Airport, on_delete = models.CASCADE, related_name='destination')
	departureDateTime = models.DateTimeField()
	arrivalDateTime = models.DateTimeField()
	duration = models.FloatField()
	aircraft = models.ForeignKey(Aircraft, on_delete = models.CASCADE)
	seatPrice = models.FloatField()
	seatsLeft = models.IntegerField(default = 150 )

class Passenger(models.Model):
	firstName = models.CharField(max_length = 30)
	surname = models.CharField(max_length = 30)
	email = models.EmailField()
	phoneNumber = models.CharField(max_length = 30)

	#Properties that were described in the lecture but not CWK specification
	nationality = models.CharField(max_length = 30, default = "Not known")
	passportNumber = models.CharField(max_length = 9, default= "Not known")

class Booking(models.Model):
	bookingNumber = models.CharField(max_length = 6)
	flight = models.ForeignKey(Flight, on_delete = models.CASCADE)
	numberOfSeats = models.IntegerField()
	passengers = models.ManyToManyField(Passenger, default = "None")
	status = models.CharField(max_length = 6, default = "ONHOLD")
	invalidAtDateTime = models.DateTimeField()

class PaymentProvider(models.Model):
	name = models.CharField(max_length = 30)
	address = models.URLField()
	accountNumber = models.CharField(max_length = 30)
	loginName = models.CharField(max_length = 30)
	loginPassword = models.CharField(max_length = 30)

class Invoice(models.Model):
	#Reference number in airlines database
	refLocal = models.CharField(max_length = 30)
	#Reference number in Payment provider's system
	refExternal = models.CharField(max_length = 30)
	booking = models.ForeignKey(Booking, on_delete = models.CASCADE)
	amount = models.FloatField()
	wasPaid = models.BooleanField()
	stamp = models.CharField(max_length = 30)


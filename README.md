# Airlines Web service

Airlines API as a part of the Web Services and Web Data module

### Installing

Full book on Django [here](https://djangobook.com/installing-django/


## Running the Client

**NOTE:** Python v3.6.1, errors may occur when using with Python v2.7

There are a few flight instances created for testing purposes:

run main.py, which can be found in client/main.py

```
python main.py
```

API can be tested with the following details:

```
Year: 2018
Month: 7
Day: 1
Departure: Vilnius VNO
Destination: Heathrow London LHR
numberOfPassenger: 2
Flexible? (y/n): y

Select ID of a flight you want to book: 6

Passenger 1:
First Name: name1
Surname: surname1
Email: name1@whatever.com
Phone number: 123

Passenger 2:
First Name: name2
Surname: surname2
Email: name2@whatever.com
Phone number: 456

Please select id from the above payment providers: 1

```

For logging to a bank account use the following:

```
Username: john
Password: password123
```
Your booking should now be confirmed!

## Extra info

Modify main.py to play around with other APIs

## Deployment

This web API is deployed on sc14db.pythonanywhere.com, in order to run it on the localhost follow the instructions described in [here](https://djangobook.com/installing-django/

## Authors

**Dominykas Brezgys**



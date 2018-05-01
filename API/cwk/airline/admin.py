from django.contrib import admin

'''
REGISTERED MODULES
'''

from .models import *

admin.site.register(Aircraft)
admin.site.register(Airport)
admin.site.register(Flight)
admin.site.register(Passenger)
admin.site.register(Booking)
admin.site.register(PaymentProvider)
admin.site.register(Invoice)
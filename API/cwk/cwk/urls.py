"""cwk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url

from airline.views import *

urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^api/findflight/$', findFlight),
    url(r'^api/bookflight/$', bookFlight),
    url(r'^api/paymentmethods/$', paymentMethods),
    url(r'^api/payforbooking/$', payForBooking),
    url(r'^api/finalizebooking/$', finalizeBooking),
    url(r'^api/bookingstatus/$', bookingStatus),
    url(r'^api/cancelbooking/$', cancelBooking),
]

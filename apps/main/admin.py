from django.contrib import admin

from .models import *

admin.site.register(
    [
        Category, Doctor, Appointment, Service, Like, Rating, Comment, Favorite
    ]
)
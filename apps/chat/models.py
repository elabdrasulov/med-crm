from datetime import datetime
from django.db import models
from django.contrib.auth import get_user_model


class Room(models.Model):
    name = models.CharField(max_length=1000)

    def __str__(self):
        return self.name

class Message(models.Model):
    value = models.CharField(max_length=100000)
    date = models.DateTimeField(default=datetime.now, blank=True)
    user = models.CharField(max_length=100)
    room = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.user} -> {self.value}'

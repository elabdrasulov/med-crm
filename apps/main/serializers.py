from datetime import datetime

from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime

from rest_framework import serializers
from rest_framework.response import Response


from .models import Doctor, Comment, Rating, Category, Favorite, Appointment, Service


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["comments"] = CommentSerializer(instance.comments.all(), many=True).data
        rep["likes"] = instance.likes.all().count()
        rep["rating"] = instance.average_rating
        rep["categories"] = CategorySerializer(instance.categories.all(), many=True).data
        rep["service"] = ServiceSerializer(instance.service.all(), many=True).data
        
        return rep


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ['user']

    def create(self, validated_data):
        validated_data["user"] = self.context.get("request").user
        return super().create(validated_data)

    def to_representation(self, instance):
        rep  = super().to_representation(instance)
        rep["user"] = instance.user.username
        return rep


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        exclude = ['user']
        
    def create(self, validated_data):
        validated_data["user"] = self.context.get("request").user
        return super().create(validated_data)

    def to_representation(self, instance):
        rep  = super().to_representation(instance)
        rep['user'] = instance.user.email
        return rep


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        exclude = ['user']
    
    def create(self, validated_data):
        validated_data["user"] = self.context.get("request").user
        return super().create(validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['user'] = instance.user.email
        rep['time'] = instance.time
        rep['doctor'] = f'{instance.doctor.first_name} {instance.doctor.last_name} id:{instance.doctor.id}'
        rep['service'] = f'{instance.service.title}, price {instance.service.price}c.'
        rep['appointment_time'] = parse_datetime(str(instance.appointment_time)).strftime("%Y-%m-%d %H:%M:%S")
        return rep


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'
# Connect between the views.py to the database

from rest_framework import serializers
from .models import Babysitter, Meetings, Requests, Parents, Kids, Reviews, AvailableTime
from django.contrib.auth.models import User

__all__ = ["RegistrationSerializer", "BabysitterSerializer", "BabysitterSerializerForParents", "KidsSerializer",
           "ParentsSerializer", "ParentsSerializerForBabysitter", "MeetingsSerializer", "ReviewsSerializer",
           "AvailableTimeSerializer", "RequestsSerializer", "RequestsStatusSerializer"]

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username' , 'email' , 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
        
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value
    
    # def validate_password(self, value):
    #     if User.objects.filter(password=value).exists():
    #         raise serializers.ValidationError("A user with that password already exists.")
    #     return value        

class BabysitterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Babysitter
        fields = ['name', 'age', 'address', 'hourly_rate', 'description', 'profile_picture', 'phone_number', 'user']

class BabysitterSerializerForParents(serializers.ModelSerializer):
    class Meta:
        model = Babysitter
        fields = ['name', 'age', 'address', 'hourly_rate', 'description', 'profile_picture']    

class KidsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kids
        fields = [ 'name', 'age']

class ParentsSerializer(serializers.ModelSerializer):
    kids = KidsSerializer(many=True, read_only=True)
    class Meta:
        model = Parents
        fields = ['dad_name' , 'mom_name' , 'address' , 'last_name' , 'profile_picture' , 'phone_number' , 'user' , 'kids']
   
class ParentsSerializerForBabysitter(serializers.ModelSerializer):
    kids = KidsSerializer(many=True, read_only=True)
    class Meta:
        model = Parents
        fields = ['dad_name' , 'mom_name' , 'address' , 'last_name' , 'profile_picture' , 'kids']    

class MeetingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meetings
        fields = '__all__'

class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ['review_text', 'rating']

class AvailableTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableTime
        fields = [ 'babysitter' ,'date', 'start_time', 'end_time']
        read_only_fields = ['id', 'babysitter']

class RequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requests
        fields = '__all__'

class RequestsStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requests
        fields = ['id', 'status']
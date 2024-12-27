# Connect between the views.py to the database

from rest_framework import serializers
from .models import Babysitter, Meetings, Requests, Parents, Kids, Reviews, AvailableTime
from django.contrib.auth.models import User

__all__ = ["RegistrationSerializer", "BabysitterSerializer", "BabysitterSerializerForParents", "KidsSerializer",
           "ParentsSerializer", "ParentsSerializerForBabysitter", "MeetingsSerializer", "MeetingsSerializerForCreating",
            "ReviewsSerializer", "AvailableTimeSerializer", "RequestsSerializer", "RequestsIsActiveSerializer",
            "RequestsStatusSerializer", "MeetingsStatusSerializer"]

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

class MeetingsSerializerForCreating(serializers.ModelSerializer):
    class Meta:
        model = Meetings
        fields = ['start_time', 'end_time']

    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("start_time must be before end_time.")
        return data

class MeetingsStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requests
        fields = ['id', 'status']

class MeetingsSerializer(serializers.ModelSerializer):
    babysitter_id = serializers.SerializerMethodField()

    class Meta:
        model = Meetings
        fields = ['start_time', 'end_time', 'babysitter_id']

    def get_babysitter_id(self, obj):
        # This assumes `babysitter` is a related field to the `Babysitter` model
        return obj.babysitter.id if obj.babysitter else None

class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ['review_text', 'rating']

class AvailableTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableTime
        fields = [ 'babysitter', 'start_time', 'end_time']
        read_only_fields = ['id', 'babysitter']

    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("start_time must be before end_time.")
        return data

class RequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requests
        fields = '__all__'

class RequestsStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requests
        fields = ['id', 'status']

class RequestsIsActiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requests
        fields = ['id', 'is_active']
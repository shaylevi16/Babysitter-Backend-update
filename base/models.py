from django.db import models
from django.contrib.auth.models import User

class Babysitter(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    address = models.CharField(max_length=255)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    profile_picture = models.ImageField(upload_to='babysitters_profile_pics/', blank=False, null=False, default='static/default_image.jpg')
    phone_number = models.CharField(max_length=15 , unique=True)
    created_time = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, unique=True , related_name="Babysitter")
    
    def __str__(self):
        return self.name

class Parents(models.Model):
    family_id = models.AutoField(primary_key=True)
    dad_name = models.CharField(max_length=255)
    mom_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to='parents_profile_pics/', blank=False, null=False, default='static/default_image.jpg')
    phone_number = models.CharField(max_length=15 , unique=True)
    created_time = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, unique=True , related_name="Parent")

    def __str__(self):
        return self.last_name

class Kids(models.Model):
    id = models.AutoField(primary_key=True)
    family = models.ForeignKey(Parents, related_name='kids', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, )
    age = models.IntegerField(default=0)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class AvailableTime(models.Model):
    id = models.AutoField(primary_key=True)
    babysitter = models.ForeignKey(Babysitter, related_name='available_times', on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=False)
    end_time = models.DateTimeField(null=False)

    def __str__(self):
        return f"from {self.start_time} to {self.end_time}"

class Meetings(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]

    id = models.AutoField(primary_key=True)
    start_time = models.DateTimeField(null=False)  # Start time of the meeting
    end_time = models.DateTimeField(null=False)  # End time of the meeting
    family = models.ForeignKey(Parents, null=False, related_name='meetings', on_delete=models.CASCADE)
    babysitter = models.ForeignKey(Babysitter, null=False, related_name='meetings', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Meeting on {self.meeting_time} between {self.family} and {self.babysitter}"
    
class Reviews(models.Model):
    id = models.AutoField(primary_key=True)
    family = models.ForeignKey(Parents, related_name='reviews', on_delete=models.CASCADE)
    babysitter = models.ForeignKey(Babysitter, related_name='reviews', on_delete=models.CASCADE)
    review_text = models.TextField(null=False, blank=False , default="Write")
    rating = models.IntegerField(null=False, blank=False , default=5)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.babysitter} by {self.family}"

class Requests(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    
    id = models.AutoField(primary_key=True)
    family = models.ForeignKey(Parents, related_name='requests',  on_delete=models.CASCADE)
    babysitter = models.ForeignKey(Babysitter, related_name='requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default='True')

    def __str__(self):
        return f"Request from {self.family} to {self.babysitter} - {self.status}"
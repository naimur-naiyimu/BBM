from django.db import models
from users.models import CustomUser
# Create your models here.

class BloodRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    GENDER = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    requester = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blood_requests')
    patient_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER, null=True, blank=True)
    blood_group = models.CharField(max_length=3, choices=CustomUser.BLOOD_GROUP_CHOICES)
    units_required = models.PositiveIntegerField(default=1)
    purpose = models.TextField()
    hospital = models.CharField(max_length=100)
    urgency = models.CharField(max_length=20, choices=[
        ('normal', 'Normal (48hrs)'),
        ('urgent', 'Urgent (24hrs)'),
        ('emergency', 'Emergency (Immediate)'),
    ])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='approved')
    request_date = models.DateTimeField(auto_now_add=True)
    needed_by = models.DateTimeField()
    mobile = models.CharField(max_length=15, null=True, blank=True)
    
    def __str__(self):
        return f"Request for {self.blood_group} by {self.requester.email}"
    
    def save(self, *args, **kwargs):
        if not self.mobile:
            self.mobile = self.requester.mobile
        super().save(*args, **kwargs)
    
class Donation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    donor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='donations')
    units_donated = models.FloatField()  # in milliliters
    donation_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    
    related_request = models.ForeignKey(BloodRequest, on_delete=models.SET_NULL, null=True, blank=True,related_name='donations')
    
    
    def set_donation_date(self, request):
        self.donation_date = request.needed_by
    
    def save(self, *args, **kwargs):
        # Update donor's last donation date when donation is completed
        if self.status == 'completed' and not self.pk:
            self.donor.last_donation_date = self.donation_date.date()
            self.donor.donation_times += 1
            self.donor.save()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Donation by {self.donor.email} on {self.donation_date}"
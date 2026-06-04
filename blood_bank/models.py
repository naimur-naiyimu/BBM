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
    
    
    def save(self, *args, **kwargs):
        from django.utils import timezone
        # Check if the instance already exists to compare status changes
        if self.pk:
            old_donation = Donation.objects.get(pk=self.pk)
            # If status is changing to 'completed' and it wasn't completed before
            if self.status == 'completed' and old_donation.status != 'completed':
                self.donor.last_donation_date = self.donation_date.date() if self.donation_date else timezone.now().date()
                self.donor.donation_times += 1
                self.donor.is_available = False # Set is_available to False
                self.donor.save()
        else:
             # For new donations, if status is 'completed' upon creation (less common)
             if self.status == 'completed':
                self.donor.last_donation_date = timezone.now().date()
                self.donor.donation_times += 1
                self.donor.is_available = False # Set is_available to False
                self.donor.save()

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Donation by {self.donor.email} on {self.donation_date}"
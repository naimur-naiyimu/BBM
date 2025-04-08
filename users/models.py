from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import datetime


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    GENDER = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    addres = models.CharField(null=True, blank=True, max_length=100)
    mobile = models.CharField(max_length=15)
    mobile2 = models.CharField(null=True, blank=True, max_length=15)

    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER, null=True, blank=True)  
    is_available = models.BooleanField(default=True)
    
    donation_times = models.PositiveIntegerField(default=0)
    last_donation_date = models.DateField(null=True, blank=True)
    
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager() 
    
    def __str__(self):
        return  f"{self.first_name} {self.last_name} {self.email}"
    
    @property
    def is_available(self):
        if self.last_donation_date and (datetime.date.today() - self.last_donation_date).days < 90:
            return False
        return True

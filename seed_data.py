import os
import django
import random
from django.utils import timezone
from datetime import timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blood_bank_management.settings')
django.setup()

from users.models import CustomUser
from blood_bank.models import BloodRequest, Donation

def run_seed():
    print("Seeding demo data...")

    # Blood groups and other choices
    blood_groups = [choice[0] for choice in CustomUser.BLOOD_GROUP_CHOICES]
    genders = ['male', 'female']
    request_statuses = ['pending', 'approved', 'rejected', 'completed']
    urgencies = ['normal', 'urgent', 'emergency']
    donation_statuses = ['pending', 'approved', 'rejected', 'completed']

    # 1. Create demo users
    print("Creating users...")
    users = []
    for i in range(1, 16):
        email = f"demo_user_{i}@example.com"
        # Check if exists
        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                'first_name': f"Demo",
                'last_name': f"User {i}",
                'mobile': f"5550100{i:02d}",
                'addres': f"{i} Demo Street, City",
                'blood_group': random.choice(blood_groups),
                'age': random.randint(20, 50),
                'gender': random.choice(genders),
                'is_verified': True,
                'is_available': random.choice([True, True, False]), # Mostly true
            }
        )
        if created:
            user.set_password('password123')
            user.save()
        users.append(user)
    
    print(f"Created/found {len(users)} users.")

    # 2. Create demo blood requests
    print("Creating blood requests...")
    requests = []
    hospitals = ['City Hospital', 'General Medical Center', 'Hope Clinic', 'St. Marys']
    for i in range(1, 11):
        requester = random.choice(users)
        request = BloodRequest.objects.create(
            requester=requester,
            patient_name=f"Patient {i}",
            gender=random.choice(genders),
            blood_group=random.choice(blood_groups),
            units_required=random.randint(1, 3),
            purpose=random.choice(["Surgery", "Accident", "Anemia", "Childbirth"]),
            hospital=random.choice(hospitals),
            urgency=random.choice(urgencies),
            status=random.choice(request_statuses),
            needed_by=timezone.now() + timedelta(days=random.randint(-2, 5)),
            mobile=requester.mobile
        )
        requests.append(request)
    
    print(f"Created {len(requests)} blood requests.")

    # 3. Create demo donations
    print("Creating donations...")
    donations_count = 0
    for user in users:
        # Each user might have 0-2 donations
        num_donations = random.randint(0, 2)
        for _ in range(num_donations):
            status = random.choice(donation_statuses)
            related_req = None
            if status in ['approved', 'completed'] and random.choice([True, False]):
                # Try to link to a request with same blood group
                matching_reqs = [r for r in requests if r.blood_group == user.blood_group]
                if matching_reqs:
                    related_req = random.choice(matching_reqs)

            donation = Donation.objects.create(
                donor=user,
                units_donated=random.choice([350.0, 450.0]),
                status=status,
                notes="Demo donation",
                related_request=related_req
            )
            # Adjust creation date manually since it uses auto_now_add
            if status == 'completed':
                donation.donation_date = timezone.now() - timedelta(days=random.randint(5, 60))
                donation.save()
            donations_count += 1
            
    print(f"Created {donations_count} donations.")
    print("Demo data seeding completed successfully!")
    print("You can log in with any demo_user_X@example.com (X from 1 to 15) and password: password123")

if __name__ == '__main__':
    run_seed()

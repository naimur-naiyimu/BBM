from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.hashers import make_password
from .models import CustomUser
from .utils import send_verification_email
from .authentication import EmailBackend
import re
from django.views.decorators.csrf import  csrf_exempt

# Registration and Verification
@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            # Extract data
            email = request.POST.get('email').strip()
            password = request.POST.get('password')
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            mobile = request.POST.get('mobile', '').strip()
            blood_group = request.POST.get('blood_group')

            # Basic validation
            if not all([email, password, first_name, last_name, mobile, blood_group]):
                raise ValidationError("All required fields must be filled")

            validate_email(email)
            
            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError("Email already exists")

            # Create user with hashed password
            user = CustomUser(
                email=email,
                password=make_password(password),  # Properly hash the password
                first_name=first_name,
                last_name=last_name,
                mobile=mobile,
                blood_group=blood_group,
                is_verified=False
            )

            # Optional fields
            if request.POST.get('age'):
                user.age = int(request.POST.get('age'))
            if request.POST.get('gender'):
                user.gender = request.POST.get('gender')
            if request.POST.get('addres'):
                user.addres = request.POST.get('addres')
            if request.POST.get('mobile2'):
                user.mobile2 = request.POST.get('mobile2')

            user.save()
            
            # Debug print (remove in production)
            print(f"User created: {user.email} | {user.first_name} {user.last_name}")
            
            # Send verification email
            messages.success(request, 'Registration successful! Please check your email.')
            send_verification_email(request, user)
            
            return redirect('login')
            
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            # Print full error for debugging
            import traceback
            traceback.print_exc()
    
    return render(request, 'register.html', {
        'blood_groups': CustomUser.BLOOD_GROUP_CHOICES,
        'genders': CustomUser.GENDER
    })

def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_verified = True
        user.save()
        messages.success(request, 'Email verified! You can now login.')
        return redirect('login')
    messages.error(request, 'Invalid verification link.')
    return redirect('register')

@csrf_exempt
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        # print(f"Email: {email}, Password: {password}")
        user = authenticate(request, email=email, password=password)
        if not user:
            messages.error(request, "Invalid username or password.")
        # elif not user.is_verified:
        #     messages.error(request, "Your email is not verified yet.")
        else:
            # print(f"User logged in: {user.email} | {user.first_name} {user.last_name}")	
            login(request, user)
            messages.success(request, "You have successfully logged in.")
            return redirect("index")

    # TODO: use a form and show form errors in template
    return render(request, "login.html")


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect("index")

@login_required
def user_dashboard(request, user_id=None):
    if user_id:
        user = get_object_or_404(CustomUser, pk=user_id)
    else:
        user = request.user
    donations_count = user.donations.count()
    requests_count = user.blood_requests.count()
    
    return render(request, 'profile.html', {
        'user': user,
        'donations_count': donations_count,
        'requests_count': requests_count
    })

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        # Update user fields manually
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.mobile = request.POST.get('mobile', user.mobile)
        user.blood_group = request.POST.get('blood_group', user.blood_group)
        user.age = request.POST.get('age', user.age)
        user.gender = request.POST.get('gender', user.gender)
        user.addres = request.POST.get('addres', user.addres)
        
        try:
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    return render(request, 'edit_profile.html', {'user': user})

def user_list(request):
    users = CustomUser.objects.all()
    print(f"Final query: {users}") 
    city = request.GET.get('city', '').strip()
    blood_type = request.GET.get('blood-type', '').strip()
    
    if city and city.lower() != "none":
        users = users.filter(addres__icontains=city)
    
    if blood_type:
        users = users.filter(blood_group=blood_type)
    
    print(f"Final query: {users}")  # Debug the SQL being generated
    
    return render(request, 'searchDonor.html', {
        'users': users,
        'users_count': users.count(),
        'current_city': city,
        'current_blood_type': blood_type
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import BloodRequest, Donation
from users.models import CustomUser

from django.utils import timezone
from datetime import datetime
from django.http import HttpResponse
from django.db.models import Case, When, Value, IntegerField
from users.utils import send_blood_request_email
# Create your views here.
def index(request):
    requests = BloodRequest.objects.all().filter(status='approved' ).order_by('-request_date')
    user_count = CustomUser.objects.count()
    request_count = BloodRequest.objects.count()
    donation_count = Donation.objects.count()
    return render(request, 'index.html', {'blood_requests': requests, 'user_count': user_count, 'request_count': request_count, 'donation_count': donation_count})

# Blood Request CRUD
@login_required
def create_blood_request(request):
    if request.method == 'POST':
        try:
            requester = request.user if request.user.is_authenticated else CustomUser.objects.get(id=1)
            patient_name = request.POST.get('patient_name')
            blood_group = request.POST.get('blood_group')
            units_required = request.POST.get('units_required')
            if units_required:
                units_required = int(units_required)
            purpose = request.POST.get('purpose')
            hospital = request.POST.get('hospital')
            urgency = request.POST.get('urgency')
            needed_by_str = request.POST.get('needed_by')
            if needed_by_str:
                naive_datetime = datetime.strptime(needed_by_str, '%Y-%m-%dT%H:%M')
                needed_by = timezone.make_aware(naive_datetime)
            else:
                needed_by = None
            
            mobile = request.POST.get('mobile') 
            mobile = mobile or requester.mobile
            gender = request.POST.get('gender')
            # print(requester, patient_name, blood_group, units_required, purpose, hospital, urgency, needed_by)
            try:
                blood_request=BloodRequest.objects.create(
                    requester=requester,
                    patient_name=patient_name,
                    blood_group=blood_group,
                    units_required=units_required,
                    purpose=purpose,
                    hospital=hospital,
                    urgency=urgency,
                    needed_by=needed_by,
                    mobile=mobile,
                    gender=gender,
                    status= 'approved'	
                )
            except Exception as e:
                print(request, f'Error: {str(e)}')
            
            messages.success(request, 'Blood request submitted successfully!')
            send_blood_request_email(request, blood_request.pk)
            return redirect('blood_request_list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'bloodRequestForm.html', {
        'blood_groups': CustomUser.BLOOD_GROUP_CHOICES,
        'urgency_choices': BloodRequest._meta.get_field('urgency').choices,
        'genders': CustomUser.GENDER
    })

@login_required
def blood_request_list(request):
    # Get all requests with prefetch for efficiency
    from django.db.models import Prefetch
    requests = BloodRequest.objects.filter(requester=request.user)\
        .prefetch_related(
            Prefetch('donations', 
                queryset=Donation.objects.select_related('donor'),
                to_attr='all_donations'
            )
        )\
        .order_by('-request_date')
    
    # Get counts
    pending_count = requests.filter(status='pending').count()
    approved_count = requests.filter(status='approved').count()
    
    return render(request, 'myRequests.html', {
        'requests': requests, 
        'pending_count': pending_count, 
        'approved_count': approved_count
    })

@login_required
def update_blood_request(request, pk):
    blood_request = get_object_or_404(BloodRequest, pk=pk, requester=request.user)
    
    if request.method == 'POST':
        try:
            blood_request.patient_name = request.POST['patient_name']
            blood_request.units_required = int(request.POST['units_required'])
            blood_request.purpose = request.POST['purpose']
            blood_request.hospital = request.POST['hospital']
            blood_request.urgency = request.POST['urgency']
            
            from datetime import datetime
            needed_by_str = request.POST.get('needed_by')
            if needed_by_str:
                naive_datetime = datetime.strptime(needed_by_str, '%Y-%m-%dT%H:%M')
                blood_request.needed_by = timezone.make_aware(naive_datetime)
            
            blood_request.save()
            messages.success(request, 'Request updated successfully!')
            return redirect('blood_request_list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    # Format the needed_by datetime for the template input
    needed_by_formatted = ""
    if blood_request.needed_by:
        needed_by_formatted = timezone.localtime(blood_request.needed_by).strftime('%Y-%m-%dT%H:%M')
        
    return render(request, 'update_request.html', {
        'request_obj': blood_request,
        'needed_by_formatted': needed_by_formatted,
        'blood_groups': CustomUser.BLOOD_GROUP_CHOICES,
        'urgency_choices': BloodRequest._meta.get_field('urgency').choices
    })

@login_required
def delete_blood_request(request, pk):
    blood_request = get_object_or_404(BloodRequest, pk=pk, requester=request.user)
    if request.method == 'POST':
        blood_request.delete()
        messages.success(request, 'Request deleted successfully!')
        return redirect('blood_request_list')
    return render(request, 'confirm_delete.html', {'object': blood_request})


def view_blood_request(request, pk):
    blood_request = get_object_or_404(BloodRequest, pk=pk)
    
    return render(request, 'view_request.html', {
        'request': blood_request,
        'blood_groups': CustomUser.BLOOD_GROUP_CHOICES,
        'urgency_choices': BloodRequest._meta.get_field('urgency').choices,
    })


    
# Donation CRUD
@login_required
def create_donation(request, request_id):
    blood_request = get_object_or_404(BloodRequest, pk=request_id)
    print("Blood Request Found:", blood_request)  # Debug print
    
    if request.method == 'POST':
        try:
            status = 'pending'
            Donation.objects.create(
                donor=request.user,
                units_donated=1,
                status=status,
                notes=f"Donation for request #{blood_request.id}",
                related_request=blood_request
            )
            blood_request.status = status
            blood_request.save()
            messages.success(request, 'Donation recorded successfully!')
            return redirect('donation_list')
        except Exception as e:
            print("Error creating donation:", str(e))  # Debug print
            messages.error(request, f'Error: {str(e)}')
    
    return redirect('index')

@login_required
def donation_list(request):
    donations = Donation.objects.filter(donor=request.user).order_by(
    Case(
        When(status='pending', then=0),
        When(status='completed', then=1),
        When(status='rejected', then=2),
        default=3,
        output_field=IntegerField()
    ),
    '-donation_date'
)
    return render(request, 'pendingRequests.html', {'donations': donations, 'status': Donation.STATUS_CHOICES})

@login_required
def update_donation(request, pk):
    from django.db.models import Q
    if request.user.is_staff:
        donation = get_object_or_404(Donation, pk=pk)
    else:
        donation = get_object_or_404(
            Donation, 
            Q(pk=pk) & (Q(donor=request.user) | Q(related_request__requester=request.user))
        )
    
    if request.method == 'POST':
        try:
            new_status = request.POST.get('status')
            is_donor = (donation.donor == request.user)
            is_requester = (donation.related_request and donation.related_request.requester == request.user)
            is_staff = request.user.is_staff
            
            if new_status in ['approved', 'completed'] and is_donor and not (is_requester or is_staff):
                messages.error(request, 'You cannot approve or complete your own donation.')
                return redirect('donation_list')
                
            donation.status = new_status
            donation.save()
            messages.success(request, 'Donation record updated successfully!')
            if is_requester:
                return redirect('blood_request_list')
            return redirect('donation_list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'pendingRequests.html', {
        'donation': donation,
        'status_choices': Donation._meta.get_field('status').choices
    })

@login_required
def delete_donation(request, pk):
    donation = get_object_or_404(Donation, pk=pk, donor=request.user)
    if request.method == 'POST':
        donation.delete()
        messages.success(request, 'Donation record deleted!')
        return redirect('donation_list')
    return render(request, 'confirm_delete.html', {'object': donation})

@login_required
def reject_blood_request(request, request_id):
    if request.user.is_staff:
        blood_request = get_object_or_404(BloodRequest, pk=request_id)
    else:
        blood_request = get_object_or_404(BloodRequest, pk=request_id, requester=request.user)
        
    if request.method == 'POST':
        blood_request.status = 'rejected' 
        blood_request.save()
        messages.success(request, 'Blood request rejected.')
        return redirect('blood_request_list')  
    messages.error(request, 'Invalid request method.')
    return redirect('blood_request_list')
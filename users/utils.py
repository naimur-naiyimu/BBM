from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .models import CustomUser
from blood_bank.models import BloodRequest
from django.shortcuts import get_object_or_404

def send_verification_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    current_site = get_current_site(request)
    # TODO: use reverse()
    verification_link = f"http://{current_site.domain}/verify/{uid}/{token}"

    email_subject = "Verify Your Email Address"
    email_body = render_to_string(
        "verification_email.html",
        {"user": user, "verification_link": verification_link, 'current_site': current_site.domain},
    )

    email = EmailMessage(
        subject=email_subject,
        body=email_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.content_subtype = "html"
    email.send()


def send_password_reset_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    current_site = get_current_site(request)
    # TODO: use reverse()
    verification_link = (
        f"http://{current_site.domain}/accounts/reset-password-confirm/{uid}/{token}"
    )

    email_subject = "Reset Your Password"
    email_body = render_to_string(
        "accounts/verification_email.html",
        {"user": user, "verification_link": verification_link},
    )

    email = EmailMessage(
        subject=email_subject,
        body=email_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.content_subtype = "html"
    email.send()
    
    
def send_blood_request_email(request, pk):
    
    blood_request = get_object_or_404(BloodRequest, pk=pk)
    users = CustomUser.objects.filter(blood_group=blood_request.blood_group)
    

    current_site = get_current_site(request)
    # TODO: use reverse()
    verification_link = f"http://{current_site.domain}/requests/{pk}"

    email_subject = "Request to you for blood"
    email_body = render_to_string(
        "request_email.html",
        {"verification_link": verification_link, 'blood_request':blood_request , 'current_site': current_site.domain},
    )
    
    recipient_list = [user.email for user in users]
    print(recipient_list)

    if recipient_list:
        email = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[],
            bcc = recipient_list,
        )

        email.content_subtype = "html"
        email.send()


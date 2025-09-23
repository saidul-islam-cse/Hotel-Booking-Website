from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site

def send_verification_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    current_site = get_current_site(request)
    verification_link = f"http://{current_site.domain}/verify/{uid}/{token}"

    email_subject = "Verify Your Email Address"
    email_body = render_to_string(
        "hotel/verification_email.html",
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

from django.core.mail import send_mail
from django.conf import settings

def send_user_mail(user, subject, message):
    
    if not user.email:
        return False  
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False, 
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

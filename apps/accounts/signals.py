from django.conf import settings
from django.core.mail import send_mail
from django.conf import settings
from django.template import Context, loader
from django.core.mail import send_mail,EmailMessage
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from apps.accounts.models import UserProfile, create_api_key


from django.db import models
models.signals.post_save.connect(create_api_key, sender=UserProfile)

@receiver(post_save,sender=UserProfile)                
def send_contact_mail(sender, created, **kwargs):
	obj = kwargs['instance']
	if created:
		subject = "Thank you for registering with us"
		to = [obj.email]
		verification_code = obj.activation_token
		val =  { 
				'site_url': settings.SITE_URL,
				'subject':subject,
				'verification_code':verification_code,
				}
		
		html_content = render_to_string('mails/registration.html',val)
		text_content = strip_tags(html_content)
		from_email = settings.DEFAULT_FROM_EMAIL
		msg_html = render_to_string('mails/registration.html',val)
		send_mail(subject, None, from_email,to,html_message=msg_html)

	from tastypie.models import create_api_key

from django import forms
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import send_mail
from django.conf import settings
from django.template import Context, loader
from django.core.mail import send_mail,EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.tokens import default_token_generator
from apps.accounts.models import UserProfile
 
class PasswordResetForm(forms.Form):
	email = forms.EmailField(label= 'Email', max_length=254)
	def save(self):
		email = self.cleaned_data['email']
		active_users = UserProfile.objects.filter(email__iexact=email, is_active=True)
		for user in active_users:
			# Make sure that no email is sent to a user that actually has
			# a password marked as unusable
			if not user.has_usable_password():
				continue
			token_generator=default_token_generator
			subject = "Password Reset mail"
			site_name = settings.SITE_URL
			protocol = settings.SITE_URL.lower()
			val = {
				'email': user.email,
				'location': 'passwordchange',
				'site_name': site_name,
				'uid': urlsafe_base64_encode(force_bytes(user.pk)),
				'user': user,
				'token': token_generator.make_token(user),
				'protocol': protocol,
			}
			to = [user.email]
			html_content = render_to_string('mails/password_reset_email.html',val)
			text_content = strip_tags(html_content)
			from_email = settings.DEFAULT_FROM_EMAIL
			msg_html = render_to_string('mails/password_reset_email.html',val)
			send_mail(subject, None, from_email,to,html_message=msg_html)













		
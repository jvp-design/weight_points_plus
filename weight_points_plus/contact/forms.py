from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

from weight_points_plus.utils.recaptcha import ReCaptchaFormMixin


class ContactForm(ReCaptchaFormMixin, forms.Form):
    recaptcha_action = "contact"

    name = forms.CharField()
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
    bot = forms.CharField(required=False)

    def clean_bot(self):
        data = self.cleaned_data.get("bot", "")
        if data:
            raise ValidationError(_("Robots stink"))
        return data

    def send_email(self, user):
        email = self.cleaned_data.get("email")
        if user.is_authenticated:
            email = user.email
        name = self.cleaned_data.get("name")
        message = self.cleaned_data.get("message")
        text_msg = f"""
Hello,
You have a new contact form submission on WeightPoints.plus. The message is from {name} with email address {email}.

The message is:
{message}
        """
        html_msg = f"""
        <html>
        <body>
        <p>Hello,</p>
        <p>
        You have a new contact form submission on WeightPoints.plus. The message is from {escape(name)} with email address {escape(email)}.
        </p>
        <br />
        <p>The message is</p>
        <p>{escape(message)}</p>
        </body>
        </html>
        """
        # The visitor's address goes in Reply-To rather than From: sending "from"
        # a domain we don't control fails SPF/DKIM/DMARC and SES rejects it.
        msg = EmailMultiAlternatives(
            subject="New Contact Message from WeightPoints.plus",
            body=text_msg,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=settings.CONTACT_FORM_RECIPIENTS,
            reply_to=[email],
        )
        msg.attach_alternative(html_msg, "text/html")
        msg.send()

from typing import Dict, Any

from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import gettext_lazy as _


class ContactForm(forms.Form):
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
        text_msg = f"""
Hello,
You have a new contact form submission on WeightPoints.plus. The message is from {self.cleaned_data.get('name')} with email address {email}.

The message is:
{self.cleaned_data.get('message')}
        """
        html_msg = f"""
        <html>
        <body>
        <p>Hello,</p>
        <p>
        You have a new contact form submission on WeightPoints.plus. The message is from {self.cleaned_data.get('name')} with email address {email}.
        </p>
        <br />
        <p>The message is</p>
        <p>{self.cleaned_data.get('message')}</p>
        </body>
        </html>
        """
        msg = EmailMultiAlternatives(
            "New Contact Message from WeightPoints.plus",
            text_msg,
            self.cleaned_data.get("email"),
            ["info@jvp.design"],
        )
        msg.attach_alternative(html_msg, "text/html")
        msg.send()

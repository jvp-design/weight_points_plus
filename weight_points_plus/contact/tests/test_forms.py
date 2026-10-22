import pytest
from django.contrib.auth.models import AnonymousUser
from django.core import mail

from weight_points_plus.contact.forms import ContactForm

pytestmark = pytest.mark.django_db


def _valid_form(**overrides):
    data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "message": "Hello <there>",
        "bot": "",
    }
    data.update(overrides)
    form = ContactForm(data=data)
    assert form.is_valid(), form.errors
    return form


def test_send_email_uses_app_sender_and_visitor_reply_to(settings):
    settings.DEFAULT_FROM_EMAIL = "Weight Points Plus <noreply@weightpointsplus.com>"
    settings.CONTACT_FORM_RECIPIENTS = ["inbox@weightpointsplus.com"]

    _valid_form().send_email(AnonymousUser())

    assert len(mail.outbox) == 1
    sent = mail.outbox[0]
    assert sent.from_email == settings.DEFAULT_FROM_EMAIL
    assert sent.to == ["inbox@weightpointsplus.com"]
    assert sent.reply_to == ["jane@example.com"]
    assert "jane@example.com" in sent.body
    assert "Hello <there>" in sent.body
    html, mimetype = sent.alternatives[0]
    assert mimetype == "text/html"
    assert "Hello &lt;there&gt;" in html


def test_send_email_prefers_authenticated_users_address(user):
    _valid_form(email="typed@example.com").send_email(user)

    sent = mail.outbox[0]
    assert sent.reply_to == [user.email]
    assert user.email in sent.body
    assert "typed@example.com" not in sent.body


def test_honeypot_rejects_bots():
    form = ContactForm(
        data={"name": "x", "email": "x@example.com", "message": "x", "bot": "spam"}
    )
    assert not form.is_valid()
    assert "bot" in form.errors

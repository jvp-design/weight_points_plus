from django.conf import settings
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3


class ReCaptchaFormMixin:
    """Adds an invisible reCAPTCHA v3 field to a form.

    v3 never shows a puzzle. Google scores the visitor from 0.0 (almost
    certainly a bot) to 1.0 (almost certainly a human) and anything below
    ``settings.RECAPTCHA_REQUIRED_SCORE`` is rejected.

    The field is only added when ``settings.RECAPTCHA_ENABLED`` is on, which
    keeps local development and the test suite from calling out to Google and
    doubles as a kill switch if reCAPTCHA ever starts turning real people away.
    """

    recaptcha_action = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if settings.RECAPTCHA_ENABLED:
            self.fields["captcha"] = ReCaptchaField(
                widget=ReCaptchaV3(action=self.recaptcha_action), label=""
            )

from django.contrib import messages
from django.urls import reverse

from weight_points_plus.contact.forms import ContactForm
from django.views.generic.edit import FormView


class ContactFormView(FormView):
    template_name = "pages/contact.html"
    form_class = ContactForm

    def get_success_url(self):
        if self.request.user.is_authenticated:
            return reverse("day:today")
        return reverse("home")

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.send_email(self.request.user)
        messages.add_message(
            self.request, messages.SUCCESS, "Thank you for reaching out."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(
            self.request,
            messages.ERROR,
            "There was an error submitting your form. Please try again later.",
        )
        return super().form_invalid(form)


contact_form_view = ContactFormView.as_view()

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import include, path, reverse
from django.views import defaults as default_views
from django.views.generic import TemplateView

from weight_points_plus.contact.views import contact_form_view
from weight_points_plus.utils.points_calculators import ajax_calculate_points


class LandingView(TemplateView):
    template_name = "pages/home.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("day:today"))
        return HttpResponseRedirect(reverse("home"))


urlpatterns = [
    path("", LandingView.as_view(), name="landing"),
    path("/home", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "about/", TemplateView.as_view(template_name="pages/about.html"), name="about"
    ),
    path(
        "contact/",
        view=contact_form_view,
        name="contact",
    ),
    path(
        "disclaimer/",
        TemplateView.as_view(template_name="pages/disclaimer.html"),
        name="disclaimer",
    ),
    path(
        "fallback/",
        TemplateView.as_view(template_name="pages/fallback.html"),
        name="fallback",
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("weight_points_plus.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    path("day/", include("weight_points_plus.day.urls", namespace="day")),
    path(
        "food/", include("weight_points_plus.foods_recipes.food.urls", namespace="food")
    ),
    path(
        "recipe/",
        include("weight_points_plus.foods_recipes.recipe.urls", namespace="recipe"),
    ),
    path("meal/", include("weight_points_plus.meal.urls", namespace="meal")),
    path("ajax/calculate-points/", ajax_calculate_points, name="ajax-calculate-points"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
else:
    urlpatterns += [
        path("admin/", include("admin_honeypot.urls", namespace="admin_honeypot"))
    ]

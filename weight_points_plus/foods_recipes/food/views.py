from typing import Any, Dict

import django_filters
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import QuerySet, Q
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.translation import gettext_lazy as _
from django_filters.views import FilterView

from .forms import FoodForm
from ..models import FoodItem
from weight_points_plus.utils.mixins import (
    UserIsOwnerMixin,
    UserCanViewMixin,
    UserHasAllInfoMixin,
)
from weight_points_plus.utils.points_calculators import calculate_food_points
from ..utils import FoodItemListView, check_conversion_status
from ...utils.misc import is_each_serving


class AllFoodsListView(FoodItemListView):
    def get_queryset(self) -> QuerySet[FoodItem]:
        self.queryset = FoodItem.objects.filter(
            Q(food_item_type="food")
            & (Q(user__isnull=True) | Q(user=self.request.user))
        )
        return super().get_queryset()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["food_item_type"] = "food"
        context["food_item_type_plural"] = "foods"
        context["create_url_string"] = "food:create"
        context["add_item_url"] = None
        if self.kwargs.get("meal_pk") is not None:
            context["add_item_url"] = reverse(
                "meal:add-food-item", kwargs={"meal_pk": self.kwargs.get("meal_pk")}
            )
        context["detail_url_string"] = "food:detail"
        context["update_url_string"] = "food:update"
        context["delete_url_string"] = "food:delete"
        return context


all_food_list_view = AllFoodsListView.as_view()


class FoodDetailMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = [
            dict(lookup="food_item_type", display="Food/Recipe"),
            dict(lookup="fat", display="Fat"),
            dict(lookup="carbs", display="Carbs"),
            dict(lookup="fiber", display="Fiber"),
            dict(lookup="protein", display="Protein"),
            dict(lookup="serving_size", display="Serving Size"),
            dict(lookup="serving_unit", display="Serving Unit"),
            dict(lookup="conversion_unit_weight", display="Weight Conversion Unit"),
            dict(lookup="conversion_unit_volume", display="Volume Conversion Unit"),
            dict(
                lookup="conversion_weight_to_volume",
                display="Weight-to-Volume Conversion Factor",
            ),
            dict(lookup="notes", display="Notes"),
            dict(lookup="points_per_serving", display="Points Per Serving"),
        ]
        context["food_item_fields"] = []
        for item in items:
            lookup = getattr(self.get_object(), item["lookup"])
            if lookup is not None:
                context["food_item_fields"].append(
                    dict(lookup=lookup, display=item["display"])
                )
        return context


class FoodDetailView(
    UserHasAllInfoMixin, UserCanViewMixin, FoodDetailMixin, DetailView
):
    model = FoodItem

    def get_permission_denied_url(self):
        return reverse("food:list")


food_detail_view = FoodDetailView.as_view()


class FoodInputMixin:
    form_class = FoodForm
    template_name = "foods_recipes/food_form.html"

    def get_success_url(self):
        return reverse("food:list")

    def get_form_class(self):
        form = super().get_form_class()
        choices = []
        for choice in form.base_fields["serving_unit"].choices:
            if choice[0] in ["Weight", "Volume"]:
                choices.extend([x for x in choice[1]])
            else:
                choices.append(choice)
        form.base_fields["serving_unit"].choices = choices
        form.base_fields["conversion_unit_weight"].choices = choices
        form.base_fields["conversion_unit_volume"].choices = choices
        return form


class FoodCreateView(UserHasAllInfoMixin, FoodInputMixin, CreateView):
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.points_per_serving = calculate_food_points(self.object)
            self.object.user = request.user
            self.object.food_item_type = "food"
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


food_create_view = FoodCreateView.as_view()


class FoodUpdateView(UserHasAllInfoMixin, UserIsOwnerMixin, FoodInputMixin, UpdateView):
    def get_permission_denied_url(self):
        return reverse("food:list")

    def get_queryset(self):
        return FoodItem.objects.filter(food_item_type="food")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            self.object.points_per_serving = calculate_food_points(self.object)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


food_update_view = FoodUpdateView.as_view()


class FoodDeleteView(
    UserHasAllInfoMixin, UserIsOwnerMixin, FoodDetailMixin, DeleteView
):
    model = FoodItem
    success_url = reverse_lazy("food:list")

    def get_permission_denied_url(self):
        return reverse("food:list")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = reverse(
            "food:detail", kwargs={"pk": self.kwargs.get("pk")}
        )
        return context


food_delete_view = FoodDeleteView.as_view()

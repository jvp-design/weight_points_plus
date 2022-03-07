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
            & (Q(user_created=False) | Q(user=self.request.user))
        )
        return super().get_queryset()


all_food_list_view = AllFoodsListView.as_view()


class UserFoodListView(FoodItemListView):
    def get_queryset(self) -> QuerySet[FoodItem]:
        self.queryset = FoodItem.objects.filter(
            Q(user=self.request.user) & Q(food_item_type="food")
        )
        return super().get_queryset()


user_food_list_view = UserFoodListView.as_view()


class FoodDetailView(UserHasAllInfoMixin, UserCanViewMixin, DetailView):
    model = FoodItem


food_detail_view = FoodDetailView.as_view()


class FoodInputMixin:
    form_class = FoodForm
    template_name = "foods_recipes/food_form.html"

    def get_success_url(self):
        return reverse("food:list")


class FoodCreateView(UserHasAllInfoMixin, FoodInputMixin, CreateView):
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.points_per_serving = calculate_food_points(self.object)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


food_create_view = FoodCreateView.as_view()


class FoodUpdateView(UserHasAllInfoMixin, UserIsOwnerMixin, FoodInputMixin, UpdateView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            self.object.points_per_serving = calculate_food_points(self.object)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


food_update_view = FoodUpdateView.as_view()


class FoodDeleteView(UserHasAllInfoMixin, UserIsOwnerMixin, DeleteView):
    model = FoodItem
    success_url = reverse_lazy("food:list")


food_delete_view = FoodDeleteView.as_view()

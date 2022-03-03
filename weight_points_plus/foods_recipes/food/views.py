from typing import Any, Dict

import django_filters
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import QuerySet, Q
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView

from ..models import FoodItem
from weight_points_plus.utils.mixins import (
    UserIsOwnerMixin,
    UserCanViewMixin,
    UserHasAllInfoMixin,
)
from weight_points_plus.utils.points_calculators import calculate_food_points
from ..utils import FoodItemListView


class AllFoodsListView(FoodItemListView):
    def get_queryset(self) -> QuerySet[FoodItem]:
        self.queryset = FoodItem.objects.filter(
            Q(food_item_type="food") & Q(user_created=False) | Q(user=self.request.user)
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


class FoodInputView:
    model = FoodItem
    fields = [
        "name",
        "fat",
        "carbs",
        "fiber",
        "protein",
        "serving_size",
        "serving_unit",
        "conversion_unit_weight",
        "conversion_unit_volume",
        "conversion_weight_to_volume",
        "notes",
    ]

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.user = request.user
            self.object.points_per_serving = calculate_food_points(self.object)
            self.object.food_item_type = "food"
            self.object.save()
            return HttpResponseRedirect(reverse("food:list"))
        else:
            return self.form_invalid(form)


class FoodCreateView(UserHasAllInfoMixin, FoodInputView, CreateView):
    pass


food_create_view = FoodCreateView.as_view()


class FoodUpdateView(UserHasAllInfoMixin, FoodInputView, UserIsOwnerMixin, UpdateView):
    pass


food_update_view = FoodUpdateView.as_view()


class FoodDeleteView(UserHasAllInfoMixin, DeleteView):
    model = FoodItem
    success_url = reverse_lazy("food:list")


food_delete_view = FoodDeleteView.as_view()

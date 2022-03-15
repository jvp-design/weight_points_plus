from typing import Any, Dict, Optional

import django_filters
from django_filters.views import FilterView

from weight_points_plus.foods_recipes.models import FoodItem
from weight_points_plus.utils.misc import (
    is_each_serving,
    is_weight_serving,
    is_volume_serving,
)
from weight_points_plus.utils.mixins import UserHasAllInfoMixin


class FoodItemFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    user = django_filters.BooleanFilter(method="filter_user")

    def filter_user(self, queryset, name, value):
        if value:
            return queryset.filter(user=self.request.user).exclude(user__isnull=True)
        return queryset.filter(user__isnull=True)

    class Meta:
        model = FoodItem
        fields = ["name", "user"]


class FoodItemListView(UserHasAllInfoMixin, FilterView):
    model = FoodItem
    paginate_by = 20
    filterset_class = FoodItemFilter
    template_name_suffix = "_list"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["query"] = dict()
        for k, v in context["filter"].data.items():
            if k != "page":
                context["query"][k] = v

        return context


def check_conversion_status(obj: Dict[str, Any]) -> Optional[str]:
    if is_each_serving(obj.get("conversion_unit_weight")) and is_each_serving(
        obj.get("conversion_unit_volume")
    ):
        return (
            "Conversion unit weight and conversion unit volume cannot both be 'each'."
        )
    if is_weight_serving(obj.get("serving_unit")) and is_each_serving(
        obj.get("conversion_unit_weight")
    ):
        return "If the serving unit is a weight the conversion unit weight cannot be 'each'."
    if is_volume_serving(obj.get("serving_unit")) and is_each_serving(
        obj.get("conversion_unit_volume")
    ):
        return "If the serving unit is a volume the conversion unit volume cannot be 'each'."
    return None

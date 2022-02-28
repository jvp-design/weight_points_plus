from typing import Any, Dict

import django_filters
from django_filters.views import FilterView

from weight_points_plus.foods_recipes.models import FoodItem


class FoodItemFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = FoodItem
        fields = ["name"]


class FoodItemListView(FilterView):
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

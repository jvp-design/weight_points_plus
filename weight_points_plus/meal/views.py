import django_filters
from django.db.models import QuerySet, Q
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from django_filters.views import FilterView

from weight_points_plus.foods_recipes.models import FoodItem
from weight_points_plus.foods_recipes.utils import FoodItemFilter


# class MealFoodListView(ListView):
#     paginate_by = 20
#     template_name = "meal/food_search.html"
#
#     def get_queryset(self) -> list:
#         name = self.request.GET.get("name")
#         user_filters = Q(user_created=False) | Q(user=self.request.user)
#         foods = FoodItem.objects.filter(user_filters)
#         # recipes = Recipe.objects.filter(user_filters)
#         if name is not None:
#             foods = foods.filter(name__icontains=name)
#             # recipes = recipes.filter(name__icontains=name)
#         return list(chain(foods, recipes))
#
#
# meal_food_list_view = MealFoodListView.as_view()

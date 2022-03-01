from django.db.models import QuerySet, Q
from django.views.generic import CreateView

from weight_points_plus.foods_recipes.models import FoodItem
from weight_points_plus.foods_recipes.utils import FoodItemListView


class MealFoodListView(FoodItemListView):
    paginate_by = 20
    template_name = "meal/food_search.html"

    def get_queryset(self) -> QuerySet[FoodItem]:
        self.queryset = FoodItem.objects.filter(
            Q(user_created=False) | Q(user=self.request.user)
        )
        return super().get_queryset()


meal_food_list_view = MealFoodListView.as_view()


class MealFoodAddView(CreateView):
    pass


meal_food_add_view = MealFoodAddView.as_view()

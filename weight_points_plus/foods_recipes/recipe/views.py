from typing import Any, Dict

from django.contrib import messages
from django.db.models import QuerySet, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.utils.translation import gettext_lazy as _

from weight_points_plus.foods_recipes.models import FoodItem, FoodItemInstance
from weight_points_plus.foods_recipes.recipe.forms import RecipeForm
from weight_points_plus.foods_recipes.utils import (
    FoodItemListView,
    check_conversion_status,
)
from weight_points_plus.utils.misc import (
    is_each_serving,
    is_weight_serving,
    is_volume_serving,
    servings,
)
from weight_points_plus.utils.mixins import (
    UserHasAllInfoMixin,
    UserCanViewMixin,
    UserIsOwnerMixin,
)
from weight_points_plus.utils.points_calculators import (
    calculate_food_points,
    get_multiplicative_factor,
    points_formula,
    NutritionItem,
)


def calculate_recipe_points(recipe):
    nutrition_item = NutritionItem(fat=0, carbs=0, fiber=0, protein=0)
    for item in recipe.recipe_items.all():
        factor = get_multiplicative_factor(
            item.food, item.serving_size, item.serving_unit
        )
        nutrition_item.fat += item.food.fat * factor
        nutrition_item.carbs += item.food.carbs * factor
        nutrition_item.fiber += item.food.fiber * factor
        nutrition_item.protein += item.food.protein * factor

    servings_in_recipe = 1
    if recipe.servings_in_recipe is not None:
        servings_in_recipe = recipe.servings_in_recipe
    nutrition_item.fat /= servings_in_recipe
    nutrition_item.carbs /= servings_in_recipe
    nutrition_item.fiber /= servings_in_recipe
    nutrition_item.protein /= servings_in_recipe
    recipe.fat = nutrition_item.fat
    recipe.carbs = nutrition_item.carbs
    recipe.fiber = nutrition_item.fiber
    recipe.protein = nutrition_item.protein
    recipe.points_per_serving = points_formula(nutrition_item)
    recipe.save()


class AllRecipesListView(FoodItemListView):
    def get_queryset(self) -> QuerySet[FoodItem]:
        self.queryset = FoodItem.objects.filter(
            Q(food_item_type="recipe")
            & (Q(user__isnull=True) | Q(user=self.request.user))
            | Q(public=True)
        )
        return super().get_queryset()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["food_item_type"] = "recipe"
        context["food_item_type_plural"] = "recipes"
        context["create_url_string"] = "recipe:create"
        context["add_item_url"] = None
        if self.kwargs.get("recipe_pk") is not None:
            context["add_item_url"] = reverse(
                "recipe:add-food", kwargs={"recipe_pk": self.kwargs.get("recipe_pk")}
            )
        context["detail_url_string"] = "recipe:detail"
        context["update_url_string"] = "recipe:update"
        context["delete_url_string"] = "recipe:delete"
        return context


all_recipe_list_view = AllRecipesListView.as_view()


class RecipeDetailMixin:
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        items = [
            dict(lookup="fat", display="Fat"),
            dict(lookup="carbs", display="Carbs"),
            dict(lookup="fiber", display="Fiber"),
            dict(lookup="protein", display="Protein"),
            dict(lookup="serving_size", display="Serving Size"),
            dict(lookup="serving_unit", display="Serving Unit"),
            dict(lookup="conversion_unit_weight", display="Weight Conversion Unit"),
            dict(lookup="conversion_unit_volume", display="Volume Conversion Unit"),
            dict(
                lookup="conversion_weight_value",
                display="Weight Conversion Value",
            ),
            dict(
                lookup="conversion_volume_value",
                display="Volume Conversion Value",
            ),
            dict(lookup="notes", display="Notes"),
            dict(lookup="directions", display="Directions"),
            dict(lookup="url", display="Url"),
            dict(lookup="servings_in_recipe", display="Servings In Recipe"),
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


class RecipeDetailView(
    UserHasAllInfoMixin, UserCanViewMixin, RecipeDetailMixin, DetailView
):
    model = FoodItem
    template_name = "foods_recipes/recipe_detail.html"

    def get_permission_denied_url(self):
        return reverse("recipe:list")


recipe_detail_view = RecipeDetailView.as_view()


class RecipeInputMixin:
    form_class = RecipeForm
    template_name = "foods_recipes/recipe_form.html"

    def get_queryset(self):
        return FoodItem.objects.filter(user=self.request.user, food_item_type="recipe")

    def get_success_url(self):
        return reverse("recipe:detail", kwargs={"pk": self.object.pk})

    # def get_form_class(self):
    #     form = super().get_form_class()
    #     choices = []
    #     for choice in form.base_fields["serving_unit"].choices:
    #         if choice[0] in ["Weight", "Volume"]:
    #             choices.extend([x for x in choice[1]])
    #         else:
    #             choices.append(choice)
    #     form.base_fields["serving_unit"].choices = choices
    #     return form


class RecipeCreateView(UserHasAllInfoMixin, RecipeInputMixin, CreateView):
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.user = request.user
            self.object.food_item_type = "recipe"
            messages.add_message(
                request,
                messages.SUCCESS,
                _(f"You have successfully created recipe {self.object.name}."),
            )
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


recipe_create_view = RecipeCreateView.as_view()


class RecipeUpdateView(
    UserHasAllInfoMixin, UserIsOwnerMixin, RecipeInputMixin, UpdateView
):
    def get_permission_denied_url(self):
        return reverse("recipe:list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        name = self.object.name
        form = self.get_form()
        if form.is_valid():
            form.save()
            self.object.name = name
            calculate_recipe_points(self.object)
            messages.add_message(
                request,
                messages.SUCCESS,
                _(f"You have successfully updated {self.object.name}."),
            )
            return HttpResponseRedirect(
                reverse("recipe:detail", kwargs={"pk": kwargs.get("pk")})
            )
        else:
            return self.form_invalid(form)


recipe_update_view = RecipeUpdateView.as_view()


class RecipeDeleteView(
    UserHasAllInfoMixin, UserIsOwnerMixin, RecipeDetailMixin, DeleteView
):
    model = FoodItem
    success_url = reverse_lazy("recipe:list")

    def get_permission_denied_url(self):
        return reverse("recipe:list")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = reverse(
            "recipe:detail", kwargs={"pk": self.kwargs.get("pk")}
        )
        return context

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        name = self.object.name
        self.object.delete()
        messages.add_message(
            request,
            messages.SUCCESS,
            _(f"You have successfully deleted {name}."),
        )
        return HttpResponseRedirect(success_url)


recipe_delete_view = RecipeDeleteView.as_view()


class RecipeFoodListView(FoodItemListView):
    paginate_by = 20
    # template_name = "foods_recipes/food_search.html"

    def get_queryset(self) -> QuerySet[FoodItem]:
        self.queryset = FoodItem.objects.filter(
            Q(user__isnull=True) | Q(user=self.request.user)
        )
        if not self.request.GET.get("restaurant"):
            self.queryset = self.queryset.filter(restaurant__isnull=True)
        return super().get_queryset()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["food_item_type"] = "food"
        context["food_item_type_plural"] = "foods"
        context["add_item_url"] = None
        if self.kwargs.get("recipe_pk") is not None:
            context["add_item_url"] = reverse(
                "recipe:add-food", kwargs={"recipe_pk": self.kwargs.get("recipe_pk")}
            )
        return context


recipe_food_list_view = RecipeFoodListView.as_view()


class BaseRecipeFoodEditView:
    model = FoodItemInstance
    fields = ["serving_size", "serving_unit"]

    def get_recipe(self):
        qs = FoodItem.objects.filter(user=self.request.user, food_item_type="recipe")
        return get_object_or_404(qs, pk=self.kwargs.get("recipe_pk"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["food"] = self.get_food()
        context["recipe_name"] = self.get_recipe().name
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
                lookup="conversion_weight_value",
                display="Weight Conversion Value",
            ),
            dict(
                lookup="conversion_volume_value",
                display="Volume Conversion Value",
            ),
            dict(lookup="notes", display="Notes"),
            dict(lookup="points_per_serving", display="Points Per Serving"),
        ]
        context["food_item_fields"] = []
        for item in items:
            lookup = getattr(context["food"], item["lookup"])
            if lookup is not None:
                context["food_item_fields"].append(
                    dict(lookup=lookup, display=item["display"])
                )
        return context

    def get_form_class(self):
        form = super().get_form_class()
        food = self.get_food()
        weight_choices = list(
            filter(
                lambda x: x in servings.get("weight"),
                form.base_fields["serving_unit"].choices,
            )
        )
        volume_choices = list(
            filter(
                lambda x: x in servings.get("volume"),
                form.base_fields["serving_unit"].choices,
            )
        )
        each_choices = list(
            filter(
                lambda x: x in servings.get("each"),
                form.base_fields["serving_unit"].choices,
            )
        )
        if food.conversion_weight_to_volume is None:
            if is_weight_serving(food.serving_unit):
                choices = weight_choices
            elif is_volume_serving(food.serving_unit):
                choices = volume_choices
            else:
                choices = each_choices
        else:
            if is_each_serving(food.conversion_unit_volume):
                choices = [*weight_choices, *each_choices]
            elif is_each_serving(food.conversion_unit_weight):
                choices = [*volume_choices, *each_choices]
            else:
                choices = form.base_fields["serving_unit"].choices
        form.base_fields["serving_unit"].choices = choices
        form.base_fields["serving_unit"].initial = food.serving_unit
        return form


class RecipeFoodAddView(UserHasAllInfoMixin, BaseRecipeFoodEditView, CreateView):
    object = None

    def get_food(self):
        qs = FoodItem.objects.filter(Q(user__isnull=True) | Q(user=self.request.user))
        return get_object_or_404(qs, pk=self.request.GET.get("food"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["submit_button_text"] = "Add Food"
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        recipe = self.get_recipe()
        if form.is_valid():
            food = self.get_food()
            if len(recipe.recipe_items.filter(food=food)) > 0:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "That food is already in the meal. Please update it instead of adding it again.",
                )
                return HttpResponseRedirect(
                    reverse("recipe:detail", kwargs={"pk": recipe.pk})
                )

            try:
                item = FoodItemInstance.objects.get(
                    food=food,
                    serving_unit=request.POST.get("serving_unit"),
                    serving_size=request.POST.get("serving_size"),
                    food_version=food.version,
                )
            except FoodItemInstance.DoesNotExist:
                item = form.save(commit=False)
                item.food = food
                item.food_version = food.version
                item.save()
            recipe.recipe_items.add(item)
            calculate_recipe_points(recipe)
            messages.add_message(
                request,
                messages.SUCCESS,
                _(f"You have successfully added {food.name} to your recipe."),
            )
            if "recipe-add-another" in request.POST:
                return HttpResponseRedirect(
                    f'{reverse("recipe:food-list", kwargs={"recipe_pk": recipe.pk})}?name={request.POST.get("next-food-search")}'
                )
            return HttpResponseRedirect(
                reverse("recipe:detail", kwargs={"pk": recipe.pk})
            )
        else:
            return self.form_invalid(form)


recipe_food_add_view = RecipeFoodAddView.as_view()


class RecipeFoodUpdateView(UserHasAllInfoMixin, BaseRecipeFoodEditView, UpdateView):
    def get_queryset(self):
        return self.get_recipe().recipe_items.all()

    def get_food(self):
        food_item = get_object_or_404(self.get_queryset(), pk=self.kwargs.get("pk"))
        return food_item.food

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["submit_button_text"] = "Update Food"
        return context

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        form = self.get_form()
        recipe = self.get_recipe()
        recipe.recipe_items.remove(obj)
        if form.is_valid():
            food = obj.food
            try:
                item = FoodItemInstance.objects.get(
                    food=food,
                    serving_unit=request.POST.get("serving_unit"),
                    serving_size=request.POST.get("serving_size"),
                    food_version=food.version,
                )
            except FoodItemInstance.DoesNotExist:
                item = form.save(commit=False)
                item.food = food
                item.food_version = food.version
                item.save()
            recipe.recipe_items.add(item)
            if len(obj.fooditem_set.all()) == 0:
                obj.delete()
            calculate_recipe_points(recipe)
            messages.add_message(
                request,
                messages.SUCCESS,
                _(f"You have successfully updated {food.name} in your recipe."),
            )
            return HttpResponseRedirect(
                reverse("recipe:detail", kwargs={"pk": recipe.pk})
            )
        else:
            return self.form_invalid(form)


recipe_food_update_view = RecipeFoodUpdateView.as_view()


class RecipeFoodDeleteView(UserHasAllInfoMixin, DeleteView):
    model = FoodItemInstance

    def get(self, request, recipe_pk=None, *args, **kwargs):
        qs = FoodItem.objects.filter(user=request.user, food_item_type="recipe")
        recipe = get_object_or_404(qs, pk=recipe_pk)
        obj = self.get_object()
        recipe.recipe_items.remove(obj)
        name = obj.food.name
        if len(obj.fooditem_set.all()) == 0:
            obj.delete()
        calculate_recipe_points(recipe)
        messages.add_message(
            request,
            messages.SUCCESS,
            _(f"You have successfully removed {name} from the recipe."),
        )
        return HttpResponseRedirect(reverse("recipe:detail", kwargs={"pk": recipe.pk}))

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        messages.add_message(
            request, messages.ERROR, "You cannot POST to this endpoint."
        )
        return redirect(request.META.get("HTTP_REFERER"))


recipe_food_delete_view = RecipeFoodDeleteView.as_view()

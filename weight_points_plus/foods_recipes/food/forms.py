from typing import Any, Dict

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from weight_points_plus.foods_recipes.models import FoodItem
from weight_points_plus.foods_recipes.utils import check_conversion_status


class FoodForm(forms.ModelForm):
    # def clean_public(self):
    #     if self.cleaned_data.get("public"):
    #         raise ValidationError(_("Foods cannot be made public"), code="invalid")

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        error = check_conversion_status(cleaned_data)
        if error is not None:
            raise ValidationError(_(error), code="invalid")

        if (
            cleaned_data["conversion_weight_value"] is None
            or cleaned_data["conversion_volume_value"] is None
            or cleaned_data["conversion_unit_weight"] is None
            or cleaned_data["conversion_unit_volume"] is None
        ):
            cleaned_data["conversion_weight_to_volume"] = None
            cleaned_data["conversion_weight_value"] = None
            cleaned_data["conversion_volume_value"] = None
            cleaned_data["conversion_unit_weight"] = None
            cleaned_data["conversion_unit_volume"] = None

        return cleaned_data

    class Meta:
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
            "conversion_weight_value",
            "conversion_volume_value",
            "notes",
            "public",
        ]

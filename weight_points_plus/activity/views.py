from typing import Any, Dict

import django_filters
from django.db.models import Q, QuerySet
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django_filters.views import FilterView

from weight_points_plus.activity.models import Activity, ActivityInstance
from weight_points_plus.utils.mixins import UserHasAllInfoMixin


class ActivityFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Activity
        fields = ["name"]


class ActivityListView(UserHasAllInfoMixin, FilterView):
    model = Activity
    paginate_by = 20
    filterset_class = ActivityFilter
    template_name_suffix = "_list"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["query"] = dict()
        for k, v in context["filter"].data.items():
            if k != "page":
                context["query"][k] = v

        return context


class AllActivityListView(ActivityListView):
    def get_queryset(self) -> QuerySet[Activity]:
        self.queryset = Activity.objects.filter(
            Q(user_created=False) | Q(user=self.request.user)
        )
        return super().get_queryset()


all_activity_list_view = ActivityListView.as_view()


class UserActivityListView(ActivityListView):
    def get_queryset(self) -> QuerySet[Activity]:
        self.queryset = Activity.objects.filter(Q(user=self.request.user))
        return super().get_queryset()


user_activity_list_view = UserActivityListView.as_view()


class ActivityCreateView(UserHasAllInfoMixin, CreateView):
    model = Activity
    fields = ["name"]

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.user = request.user
            self.object.save()
            return HttpResponseRedirect(reverse("activity:list"))
        else:
            return self.form_invalid(form)


activity_create_view = ActivityCreateView.as_view()


class ActivityDetailView(UserHasAllInfoMixin, DetailView):
    model = Activity

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        qs = ActivityInstance.objects.filter(activity__user=self.request.user).order_by(
            "-day__date"
        )[:5]
        context["recent_activities"] = qs
        return context


activity_detail_view = ActivityDetailView.as_view()


class ActivityUpdateView(UserHasAllInfoMixin, UpdateView):
    model = Activity
    fields = ["name"]


activity_update_view = ActivityUpdateView.as_view()


class ActivityDeleteView(UserHasAllInfoMixin, DeleteView):
    model = Activity


activity_delete_view = ActivityDeleteView.as_view()

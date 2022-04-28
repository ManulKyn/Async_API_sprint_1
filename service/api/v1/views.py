from django.contrib.postgres.aggregates import ArrayAgg
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from service.models.models import Filmwork


def aggregate_person_role(role=None):
    return ArrayAgg(
        'persons__full_name',
        distinct=True,
        filter=Q(personfilmwork__role=role)
    ) if role else ArrayAgg(
        'genres__name',
        distinct=True
    )


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        personrole = {
            "ACTOR": 'actor',
            'WRITER': 'screenwriter',
            'FILMMAKER': 'filmmaker'
        }

        return self.model.objects.values(
            'id', 'title', 'description', 'creation_date', 'rating',
            'type'
        ).annotate(
            genres=aggregate_person_role(),
            filmmakers=aggregate_person_role(role=personrole['FILMMAKER']),
            writers=aggregate_person_role(role=personrole['WRITER']),
            actors=aggregate_person_role(role=personrole['ACTOR'])
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):

    def get_context_data(self, *, object_list=None, **kwargs):
        self.paginate_by = 50
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            self.paginate_by
        )
        prevpage = page.previous_page_number() if page.has_previous() else None
        nextpage = page.next_page_number() if page.has_next() else None
        return {
            'count': paginator.count,
            "total_pages": paginator.num_pages,
            "prev": prevpage,
            "next": nextpage,
            'results': list(page.object_list),
        }


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        return kwargs['object']

from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls.base import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.generic import (
    DetailView, FormView, ListView, RedirectView, View
)
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import FormMixin

from apps.core.models import OmicsArea, PixelSet, Tag
from .forms import (
    PixelSetFiltersForm, PixelSetExportForm, PixelSetExportPixelsForm,
    PixelSetSelectForm
)
from .utils import export_pixelsets, export_pixels


def get_omics_units_for_export(session, default=[]):
    return session.get(
        'export', {}
    ).get(
        'pixels', {}
    ).get(
        'omics_units', default
    )


class PixelSetListView(LoginRequiredMixin, FormMixin, ListView):

    form_class = PixelSetFiltersForm
    model = PixelSet
    paginate_by = 10
    template_name = 'explorer/pixelset_list.html'

    def get_form_kwargs(self):

        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        if self.request.method == 'GET':
            kwargs.update({
                'data': self.request.GET,
            })

        return kwargs

    def get_queryset(self):

        qs = super().get_queryset()

        form = self.get_form()
        if form.is_valid():

            species = form.cleaned_data.get('species')
            if species:
                qs = qs.filter(
                    pixel__omics_unit__strain__species__id__in=species
                )

            omics_unit_types = form.cleaned_data.get('omics_unit_types')
            if omics_unit_types:
                qs = qs.filter(
                    pixel__omics_unit__type__id__in=omics_unit_types
                )

            parent_omics_areas = form.cleaned_data.get('omics_areas')
            if parent_omics_areas:
                omics_areas = OmicsArea.objects.get_queryset_descendants(
                    parent_omics_areas,
                    include_self=True
                )
                qs = qs.filter(
                    analysis__experiments__omics_area__id__in=omics_areas
                )

            parent_tags = form.cleaned_data.get('tags')
            if parent_tags:
                # Add descendants to the tags queryset
                tags = Tag.objects.filter(
                    id__in=parent_tags
                ).with_descendants()

                qs = qs.filter(
                    Q(analysis__tags__id__in=tags) |
                    Q(analysis__experiments__tags__id__in=tags)
                )

            search = form.cleaned_data.get('search')
            if len(search):
                qs = qs.filter(
                    Q(analysis__experiments__description__icontains=search) |
                    Q(analysis__description__icontains=search) |
                    Q(pixel__omics_unit__reference__identifier__iexact=search)
                )

        # optimize db queries
        qs = qs.select_related(
            'analysis',
            'analysis__pixeler',
        ).prefetch_related(
            'analysis__experiments__omics_area',
            'analysis__experiments__tags',
            'analysis__tags',
            'pixels__omics_unit__type',
            'pixels__omics_unit__strain__species',
        )

        return qs.distinct()

    def get_context_data(self, **kwargs):

        selected_pixelset = []
        if self.request.session.get('export', None):
            selected_pixelset_ids = self.request.session['export'].get(
                'pixelsets',
                []
            )
            selected_pixelset = PixelSet.objects.filter(
                id__in=selected_pixelset_ids
            )

        context = super().get_context_data(**kwargs)
        context.update({
            'export_form': PixelSetExportForm(),
            'select_form': PixelSetSelectForm(),
            'selected_pixelsets': selected_pixelset,
        })
        return context


class PixelSetSelectionClearView(LoginRequiredMixin, RedirectView):

    http_method_names = ['post', ]
    url = reverse_lazy('explorer:pixelset_list')

    def post(self, request, *args, **kwargs):

        request.session.update({
            'export': {
                'pixelsets': []
            }
        })

        messages.success(
            request,
            _("Pixel set selection has been cleared")
        )

        return super().post(request, *args, **kwargs)


class PixelSetSelectView(LoginRequiredMixin, FormView):

    form_class = PixelSetSelectForm
    http_method_names = ['post', ]
    success_url = reverse_lazy('explorer:pixelset_list')

    def form_valid(self, form):

        selection = []
        if self.request.session.get('export', None):
            selection = self.request.session['export'].get('pixelsets', [])
        selection += [str(p.id) for p in form.cleaned_data['pixel_sets']]
        selection = list(set(selection))

        self.request.session.update({
            'export': {
                'pixelsets': selection
            }
        })

        messages.success(
            self.request,
            _("{} pixelset(s) have been saved for exportation").format(
                len(form.cleaned_data['pixel_sets'])
            )
        )

        return super().form_valid(form)


class PixelSetExportView(LoginRequiredMixin, View):

    ATTACHEMENT_FILENAME = 'pixelsets_{date_time}.zip'
    http_method_names = ['post', ]

    @staticmethod
    def get_export_archive_filename():
        return PixelSetExportView.ATTACHEMENT_FILENAME.format(
            date_time=timezone.now().strftime('%Y%m%d_%Hh%Mm%Ss')
        )

    def post(self, request, *args, **kwargs):

        selection = []
        if self.request.session.get('export', None):
            selection = self.request.session['export'].get('pixelsets', [])

        if not len(selection):
            return self.empty_selection(request)

        qs = PixelSet.objects.filter(id__in=selection)
        content = export_pixelsets(qs).getvalue()

        # Reset selection
        request.session.update({
            'export': {
                'pixelsets': []
            }
        })

        response = HttpResponse(content, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename={}'.format(
            self.get_export_archive_filename()
        )
        return response

    def empty_selection(self, request):

        messages.error(
            request,
            _("Cannot export empty selection")
        )

        return HttpResponseRedirect(reverse('explorer:pixelset_list'))


class PixelSetDetailView(LoginRequiredMixin, FormMixin, DetailView):

    form_class = PixelSetExportPixelsForm
    http_method_names = ['get', 'post']
    model = PixelSet
    pixels_limit = 100
    template_name = 'explorer/pixelset_detail.html'

    def get_omics_units(self):

        return get_omics_units_for_export(self.request.session)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        qs = self.object.pixels.prefetch_related('omics_unit__reference')
        omics_units = self.get_omics_units()

        if len(omics_units) > 0:
            qs = qs.filter(omics_unit__reference__identifier__in=omics_units)

        pixels = qs[:self.pixels_limit]

        context.update({
            'pixels': pixels,
            'pixels_limit': self.pixels_limit,
        })
        return context

    def get_initial(self):

        initial = super().get_initial()

        initial.update({
            'omics_units': ' '.join(self.get_omics_units()),
        })
        return initial

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            omics_units = form.cleaned_data['omics_units']
            request.session.update({
                'export': {
                    'pixels': {
                        'omics_units': omics_units,
                    },
                },
            })

            return self.form_valid(form)
        else:
            # We should never reach this code because the form should always be
            # valid (no required field or validation)
            return self.form_invalid(form)  # pragma: no cover

    def get_success_url(self):

        return self.object.get_absolute_url()


class PixelSetExportPixelsView(LoginRequiredMixin, BaseDetailView):

    ATTACHEMENT_FILENAME = 'pixels_{date_time}.csv'

    model = PixelSet

    @staticmethod
    def get_export_archive_filename():
        return PixelSetExportPixelsView.ATTACHEMENT_FILENAME.format(
            date_time=timezone.now().strftime('%Y%m%d_%Hh%Mm%Ss')
        )

    def get(self, request, *args, **kwargs):
        omics_units = get_omics_units_for_export(request.session)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}'.format(
            self.get_export_archive_filename()
        )

        export_pixels(
            self.get_object(),
            omics_units=omics_units,
            output=response
        )

        return response

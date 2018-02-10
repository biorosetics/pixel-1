from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.urls.base import reverse
from django.views.generic import TemplateView, View

from apps.core.models import Pixel, PixelSet

from .helpers import get_selected_pixel_sets_from_session
from .mixins import DataTableMixin


class DataTableSelectionView(LoginRequiredMixin, DataTableMixin, View):

    def get_pixels_queryset(self):

        selected_pixelset_ids = get_selected_pixel_sets_from_session(
            self.request.session
        )

        return Pixel.objects.filter(pixel_set_id__in=selected_pixelset_ids)


class PixelSetSelectionValuesView(DataTableSelectionView):

    def get_headers(self):

        return {'id': ('string'), 'value': ('number')}


class PixelSetSelectionQualityScoresView(DataTableSelectionView):

    def get_headers(self):

        return {'id': ('string'), 'quality_score': ('number')}


class PixelSetSelectionView(LoginRequiredMixin, TemplateView):

    pixels_limit = 100
    template_name = 'explorer/pixelset_selection.html'

    def get(self, request, *args, **kwargs):

        selection = get_selected_pixel_sets_from_session(request.session)

        if not len(selection):
            return self.empty_selection(request)

        return super().get(request, *args, **kwargs)

    def empty_selection(self, request):

        messages.error(
            request,
            _("Cannot explore an empty selection.")
        )

        return HttpResponseRedirect(reverse('explorer:pixelset_list'))

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        selected_pixelset_ids = get_selected_pixel_sets_from_session(
            self.request.session
        )

        selected_pixelsets = PixelSet.objects.filter(
            id__in=selected_pixelset_ids
        )

        qs = Pixel.objects.filter(
            pixel_set_id__in=selected_pixelsets
        ).select_related(
            'omics_unit__reference'
        )

        pixels = qs[:self.pixels_limit]
        pixels_count = qs.count()

        total_count = Pixel.objects.filter(
            pixel_set_id__in=selected_pixelsets
        ).count()

        context.update({
            'pixels': pixels,
            'pixels_count': pixels_count,
            'pixels_limit': self.pixels_limit,
            'total_count': total_count,
            'selected_pixelsets': selected_pixelsets,
        })
        return context

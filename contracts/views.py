from django.shortcuts import render

from .reports import ALL_METRICS


def data_quality_report(request):
    return render(request, 'data_quality_report.html', {
        'ALL_METRICS': ALL_METRICS,
    })

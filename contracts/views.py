from django.db import models
from django.shortcuts import render
from django.http import Http404

from .models import Contract
from .reports import ALL_METRICS


MAX_EXAMPLES = 10

EXAMPLE_FIELDS = [
    field.name for field in Contract._meta.get_fields()
    if isinstance(field, (
        models.IntegerField,
        models.CharField,
        models.DecimalField,
        models.DateField,
        models.TextField,
    ))
]


def data_quality_report(request):
    return render(request, 'data_quality_report.html', {
        'ALL_METRICS': ALL_METRICS,
    })


def data_quality_report_detail(request, slug):
    metrics = [metric for metric in ALL_METRICS if metric.slug == slug]
    if not metrics:
        raise Http404('Unknown metric')
    metric = metrics[0]
    queryset = metric.get_queryset()

    examples = []
    for contract in queryset[:MAX_EXAMPLES]:
        examples.append([
            getattr(contract, field) for field in EXAMPLE_FIELDS
        ])

    return render(request, 'data_quality_report_detail.html', {
        'metric': metric,
        'examples': examples,
        'EXAMPLE_FIELDS': EXAMPLE_FIELDS,
    })

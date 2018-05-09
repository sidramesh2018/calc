import io

from django.shortcuts import render
from django.core.management import call_command
from django.utils.safestring import mark_safe
import markdown


def data_quality_report(request):
    stdout = io.StringIO()
    call_command('data_quality_report', stdout=stdout)
    html = mark_safe(markdown.markdown(stdout.getvalue()))  # nosec
    return render(request, 'data_quality_report.html', dict(html=html))

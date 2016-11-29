from django.shortcuts import render
from contracts.models import Contract
import json

from contracts.models import Contract
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required

import math

# Create your views here.
def percentage_compare(request):
    results = Contract.objects.filter(labor_category=request.labor_category)
    total_results = len(results)
    hourly_rate = float(request.hourly_rate)
    count_with_higher_price = len([result for result in results if result.hourly_rate_year1 > hourly_rate])
    percentage = math.floor(100 * (float(count_with_higher_price)/total_results))
    print("Percentage with higer hourly year 1 rates:", percentage)
    context = {
        "percentage":percentage,
        "hourly_rate":hourly_rate,
        "labor_category":labor_category
    }
    return render(request, "calc_kpi/percentage_compare",context)

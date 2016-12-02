from django.shortcuts import render
from contracts.models import Contract
import json

from calc_kpi.models import ProposedContractingData
from contracts.models import Contract
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required

from django.utils import timezone
import math
import statistics #Python 3 only

# Create your views here.
def percentage_compare(request):
    if request.method == 'POST':
        post_data_dict = request.POST.dict()
        results = Contract.objects.filter(labor_category=post_data_dict["labor_category"])
        try:
            hourly_rate = float(post_data_dict["hourly_rate"])
        except:
            #think of a way to handle this should type conversion fail
            pass
        proposed_data = ProposedContractingData(proposed_price=hourly_rate,timestamp=timezone.now())
        proposed_data.save()
        total_results = len(results)
        filtered_rates = [float(result.hourly_rate_year1) for result in results if result.hourly_rate_year1 > hourly_rate]
        average_savings = statistics.median(filtered_rates) - hourly_rate 
        count_with_higher_price = len(filtered_rates)
        percentage = math.floor(100 * (float(count_with_higher_price)/total_results))
        total_hours = float(post_data_dict["total_hours"])
        total_cost_for_this_contract = total_hours * hourly_rate
        average_total_cost_savings = average_savings * total_hours
        context = {
            "percentage":percentage,
            "hourly_rate":post_data_dict["hourly_rate"],
            "labor_category":post_data_dict["labor_category"],
            "average_savings":average_savings,
            "total_cost_for_this_contract":total_cost_for_this_contract,
            "average_total_cost_savings":average_total_cost_savings,
            "result":True
        }
        return render(request, "calc_kpi/percentage_compare.html",context)
    elif request.method == "GET":
        return render(request, "calc_kpi/percentage_compare.html",{"result":False})

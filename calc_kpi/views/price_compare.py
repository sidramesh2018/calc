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

def save_proposed_data(hourly_rate,number_of_hours,labor_category):
    proposed_data = ProposedContractingData(proposed_price=hourly_rate,proposed_hours=int(number_of_hours),timestamp=timezone.now())
    proposed_data.save()

def you_saved_with_calc_analysis(results,hourly_rate,total_hours):
    """
    This function does a series of calculations used for the analysis of proposed prices in calc
    parameters -
    * results of Contract.objects.filter(labor_category=labor_category) ( a list )
    * hourly_rate - a float
    * total_hours - an integer

    output -
    returns a dictionary that goes into the context variable 
    """
    total_results = len(results)
    filtered_rates = [float(result.hourly_rate_year1) for result in results if result.hourly_rate_year1 > hourly_rate]
    average_savings = statistics.median(filtered_rates) - hourly_rate 
    count_with_higher_price = len(filtered_rates)
    percentage = math.floor(100 * (float(count_with_higher_price)/total_results))
    total_cost_for_this_contract = total_hours * hourly_rate
    average_total_cost_savings = average_savings * total_hours
    return {
        "percentage":percentage,
        "hourly_rate":hourly_rate,
        "labor_category":labor_category,
        "average_savings":average_savings,
        "total_cost_for_this_contract":total_cost_for_this_contract,
        "average_total_cost_savings":average_total_cost_savings,
        "you_saved_with_calc":True,
        "result":True
    }

def you_could_save_x_with_calc(results,hourly_rate,total_hours,labor_category):
    """
    This function does a series of calculations used for the analysis of proposed prices in calc
    parameters -
    * results of Contract.objects.filter(labor_category=labor_category) ( a list )
    * hourly_rate - a float
    * total_hours - an integer

    output -
    returns a dictionary that goes into the context variable 
    """
    #I want to do something like this: http://stats.stackexchange.com/questions/23117/which-mean-to-use-and-when
    #inspecting the structure of the central tendency and making a decisions in code as to what the structure of the
    #mathematics is, I'm not sure I can infer this from the data
    #however, it will be interesting to try.
    #For the mean time, I'm merely going to check for the presence of an outlier,
    #should I find one, I'll make use of the median as the central tendency
    #should I not find one, I'll use the mean for the measure of central tendency
    #This should be considered as a replacement for mean in the main tool, and I hope to have a substantive discussion
    #around this issue with the group
    std_dev = statistics.stdev(results)
    mean = statistics.mean(results)
    median = statistics.median(results)
    #this code checks for outliers
    outlier_above = [result for result in results if (std_dev * 3) + mean > result]
    outlier_below = [result for result in results if (std_dev * 3) - mean < result]
    if len(outlier_above) > 0 or len(outlier_below) > 0:
        possible_savings = hourly_rate - median
    else:
        possible_savings = hourly_rate - mean
    total_results = len(results)
    count_with_lower_price = [float(result.hourly_rate_year1) for result in results if result.hourly_rate_year1 < hourly_rate]
    percentage = math.floor(100 * (float(count_with_lower_price)/total_results))

    return {
        "percentage":percentage,
        "hourly_rate":str(hourly_rate),
        "labor_category":str(labor_category),
        "average_savings":average_savings,
        "total_cost_for_this_contract":total_cost_for_this_contract,
        "average_total_cost_savings":average_total_cost_savings,
        "you_saved_with_calc":True,
        "result":True
    }
    
# Create your views here.
def percentage_compare(request):
    if request.method == 'POST':
        post_data_dict = request.POST.dict()
        results = Contract.objects.filter(labor_category=post_data_dict["labor_category"])
        try:
            hourly_rate = float(post_data_dict["hourly_rate"])
        except:
            #think of a way to handle this should type conversion fail
            #the type conversion shouldn't fail, looks like this is handled on the front end.  However still
            #probably a good idea to handle just in case and for testing purposes.
            #double checking also adds redundancy and better error checking
            pass
        total_hours = float(post_data_dict["total_hours"])
        save_proposed_data(hourly_rate,total_hours)
        
        return render(request, "calc_kpi/percentage_compare.html",context)
    elif request.method == "GET":
        return render(request, "calc_kpi/percentage_compare.html",{"result":False})

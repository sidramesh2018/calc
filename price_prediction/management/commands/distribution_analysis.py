from price_prediction.models import FittedValuesByCategory
from price_prediction.models import LaborCategoryLookUp
from price_prediction.models import PriceModels
from contracts.models import Contract
import pandas as pd
import math
import datetime
import code
from django.core.management import BaseCommand
from optparse import make_option
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from sklearn import cluster
import statistics
import random

def visualize(array):
    array = [result for result in array if result < 300]
    print("normality",stats.normaltest(array).pvalue)
    print("median",statistics.median(array))
    max = np.amax(array)
    min = np.amin(array)

    histo = np.histogram(array, bins=100, range=(min, max))
    freqs = histo[0]
    rangebins = (max - min)
    numberbins = (len(histo[1])-1)
    interval = (rangebins/numberbins)
    newbins = np.arange((min), (max), interval)
    histogram = plt.bar(newbins, freqs, width=0.2, color='gray')
    plt.show()
    
def check_na(value):
    try:
        float(value)
        return True
    except:
        return False
        
def checking_for_normality_via_price_information():
    """
    Results:
    1. Tests for normality across prices from year one fail.  This implies we cannot simply take a random sample of
    year one prices and assume it will be representative of the population of data.
    """

    results = Contract.objects.all()     
    year_one_prices = []
    year_two_prices = []
    year_three_prices = []
    year_four_prices = []
    year_five_prices = []
    for result in results:
        year_one_prices.append(result.hourly_rate_year1)
        year_two_prices.append(result.hourly_rate_year2)
        year_three_prices.append(result.hourly_rate_year3)
        year_four_prices.append(result.hourly_rate_year4)
        year_five_prices.append(result.hourly_rate_year5)
    year_one_prices = [float(result) for result in year_one_prices if check_na(result)]
    year_two_prices = [float(result) for result in year_two_prices if check_na(result)]
    year_three_prices = [float(result) for result in year_three_prices if check_na(result)]
    year_four_prices = [float(result) for result in year_four_prices if check_na(result)]
    year_five_prices = [float(result) for result in year_five_prices if check_na(result)]
    
    visualize(year_one_prices)
    visualize(year_two_prices)
    visualize(year_three_prices)
    visualize(year_four_prices)
    visualize(year_five_prices)


def normality_by_labor_category():
    """
    Result:
    338 of the 23854 labor categories passed the test of normality.  Meaning we could take random samples of those labor categories and still approximate something.
    This may feel like bad news, and to some degree it is, since these categories only account for 6,813 data points of the 55244 total data points in the set.  
    That amounts to test coverage of 12 percent via random sampling.
    """
    results = Contract.objects.all()
    labor_categories = set([result.labor_category for result in results])
    data = []
    results = []
    very_little_data_count = 0
    for labor_category in labor_categories:
        tmp = [float(result.hourly_rate_year1) for result in Contract.objects.filter(labor_category=labor_category) if check_na(result)]
        if len(tmp) > 10:
            data.append(tmp)
        else:
            very_little_data_count += 1
    for datum in data:
        results.append(stats.normaltest(datum).pvalue)
    significance_count = 0
    total_size = 0
    for ind,result in enumerate(results):
        if result > 0.05:
            significance_count += 1
            total_size += len(data[ind])
        else:
            continue
    return significance_count,total_size

def analysis_by_labor_category():
    results = Contract.objects.all()
    print(len(results))
    labor_categories = set([result.labor_category for result in results])
    print(len(labor_categories))
    _,total_size = normality_by_labor_category()
    print(total_size)

def homegrown_categories():
    """
    Results:
    The results using this categorization were even works than using the labor categories as the only look up.  total size of 605 and significance count of 17.
    Compared with the above test - which had 6813 data points that were normal, we are doing significantly worse.  More or less we went from an efficiency gain
    of 12% to something closer to 2%.  Clearly this strategy must be rejected.  
    """
    labor_categories = set([elem.labor_key for elem in LaborCategoryLookUp.objects.all()])
    data = []
    results = []
    very_little_data_count = 0
    for labor_category in labor_categories:
        tmp = [float(result.labor_value) for result in LaborCategoryLookUp.objects.filter(labor_key=labor_category)]
        if len(tmp) > 10:
            data.append(tmp)
        else:
            very_little_data_count += 1
    for datum in data:
        results.append(stats.normaltest(datum).pvalue)
    significance_count = 0
    total_size = 0
    for ind,result in enumerate(results):
        if result > 0.05:
            significance_count += 1
            total_size += len(data[ind])
        else:
            continue
    print("total size",total_size)
    print("significance count",significance_count)

def minimum_viable_sample(population):
    sample_sizes = [200,300,400,500,1000,1500,2000,2500,3000,3500,4000,4500,5000]
    best_pvalue = 10000
    best_sample_size = 0
    values_per_sample = {}
    for sample_size in sample_sizes:
        values_per_sample[sample_size] = []
        for _ in range(10):
            sample = random.sample(population,sample_size)
            p_value = stats.mannwhitneyu(population,sample).pvalue
            values_per_sample[sample_size].append(p_value)
            if p_value < best_pvalue:
                best_pvalue = p_value
                best_sample_size = sample_size
    return best_sample_size,values_per_sample

class Command(BaseCommand):

    def handle(self, *args, **options):
        results = Contract.objects.all()     
        year_one_prices = []
        year_two_prices = []
        year_three_prices = []
        year_four_prices = []
        year_five_prices = []
        for result in results:
            year_one_prices.append(result.hourly_rate_year1)
            year_two_prices.append(result.hourly_rate_year2)
            year_three_prices.append(result.hourly_rate_year3)
            year_four_prices.append(result.hourly_rate_year4)
            year_five_prices.append(result.hourly_rate_year5)
        year_one_prices = [float(result) for result in year_one_prices if check_na(result)]
        year_two_prices = [float(result) for result in year_two_prices if check_na(result)]
        year_three_prices = [float(result) for result in year_three_prices if check_na(result)]
        year_four_prices = [float(result) for result in year_four_prices if check_na(result)]
        year_five_prices = [float(result) for result in year_five_prices if check_na(result)]
        best_sample_size, results_dicter = minimum_viable_sample(year_one_prices)
        ploting_dicter = {}
        for key in results_dicter.keys():
            ploting_dicter[key] = statistics.mean(results_dicter[key])
        x_axis = list(ploting_dicter.keys())
        y_axis = [ploting_dicter[key] for key in x_axis]
        histogram = plt.bar(x_axis, y_axis, width=0.2, color='gray')
        plt.show()
        visualize(year_one_prices)
        visualize(random.sample(year_one_prices,500))

        
        #print(best_sample_size)

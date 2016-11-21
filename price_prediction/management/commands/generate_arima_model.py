from price_prediction.models import *
import pandas as pd
from glob import glob
import os
import math
import json
import datetime
import time
import numpy as np
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.graphics.api import qqplot
from scipy.optimize import brute
import statistics
from functools import partial
import os
import logging

import pandas as pd
import math
import datetime

from django.core.management import BaseCommand
from optparse import make_option
from django.core.management import call_command



def total_error(values,fitted_values):
    if (len(values) == len(fitted_values)) or (len(values) < len(fitted_values)):
        return sum([abs(values[ind] - fitted_values[ind]) for ind in range(len(values))]) 
    else:
        return sum([abs(values[ind] - fitted_values[ind]) for ind in range(len(fitted_values))])
        
def check_for_extreme_values(sequence,sequence_to_check=None):
    mean = statistics.mean(sequence)
    stdev = statistics.stdev(sequence)
    if sequence_to_check != None:
        for val in sequence_to_check:
            if val >= mean + (stdev*2):
                sequence_to_check.remove(val)
            elif val <= mean - (stdev*2):
                sequence_to_check.remove(val)
        return sequence_to_check
    else:
        for val in sequence:
            if val >= mean + (stdev*2):
                sequence.remove(val)
            elif val <= mean - (stdev*2):
                sequence.remove(val)
        return sequence
        
def setting_y_axis_intercept(data,model):
    data = list(data["Year 1/base"])
    fittedvalues = list(model.fittedvalues)
    avg = statistics.mean(data)
    median = statistics.median(data)
    possible_fitted_values = []

    possible_fitted_values.append([elem + avg for elem in fittedvalues])
    possible_fitted_values.append([elem + data[0] for elem in fittedvalues])
    possible_fitted_values.append([elem + median for elem in fittedvalues])
    possible_fitted_values.append(fittedvalues)
    min_error = 1000000
    best_fitted_values = 0
    for ind,f_values in enumerate(possible_fitted_values):
        cur_error = total_error(data,f_values)
        if cur_error < min_error:
            min_error = cur_error 
            best_fitted_values = ind
    print("minimum error:",min_error)
    return possible_fitted_values[best_fitted_values]

def objective_function(data,order):
    return sm.tsa.ARIMA(data,order).fit().aic

def model_search(data):
    obj_func = partial(objective_function,data)
    upper_bound_AR = 10
    upper_bound_I = 10
    upper_bound_MA = 10
    grid_not_found = True
    while grid_not_found:
        try:
            if upper_bound_AR < 0 or upper_bound_I < 0 or upper_bound_MA < 0:
                grid_not_found = False
            grid = (slice(1,upper_bound_AR,1),slice(1,upper_bound_I,1),slice(1,upper_bound_MA,1))
            return brute(obj_func, grid, finish=None)
        except Exception as e: #found here: http://stackoverflow.com/questions/4308182/getting-the-exception-value-in-python
            error_string = str(e)
            if "MA" in error_string:
                upper_bound_MA -= 1
            elif "AR" in error_string:
                upper_bound_AR -= 1
            else:
                upper_bound_I -= 1
                
    #assuming we don't ever hit a reasonable set of upper_bounds, it's pretty safe to assume this will work
    grid = (slice(1,2,1),slice(1,2,1),slice(1,2,1))
    return brute(obj_func, grid, finish=None)


class Command(BaseCommand):

    default_filename = 'contracts/docs/hourly_prices.csv'

    option_list = BaseCommand.option_list + (
        make_option(
            '-f', '--filename',
            default=default_filename,
            help='input filename (.csv, default {})'.format(default_filename)
        ),
    )

    def handle(self, *args, **options):
        labor_categories = [elem.labor_key for elem in LaborCategoryLookUp.objects.all()]

        for labor_category in labor_categories:
            labor_objects = LaborCategoryLookUp.objects.filter(labor_key=labor_category)
            df = pd.DataFrame()
            for labor_object in labor_objects:
                df = df.append({"Begin Date":labor_object.start_date,"Price":float(labor_object.labor_value)},ignore_index=True)
            df.index = df["Begin Date"]
            import code
            code.interact(local=locals())
            model_order = list(model_search(df))
            model_order = tuple([int(elem) for elem in model_order])
            model = sm.tsa.ARIMA(df,model_order).fit()
            for ind,value in enumerate(model.fittedvalues):
                fitted_values_by_category = FittedValuesByCategory(labor_key=labor_category,fittedvalue=value,start_date=df.ix[ind])
                fitted_values_by_category.save()
# results = sm.tsa.ARIMA(dta, (3,1,0)).fit()
# results.save
# sm.load()



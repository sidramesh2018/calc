from price_prediction.models import FittedValuesByCategory as Fitted
from price_prediction.models import LaborCategory
from price_prediction.models import TrendByCategory as Trend
from price_prediction.models import InterpolatedDataByCategory as InterpolatedData
import pandas as pd
import math
import datetime
import statsmodels.api as sm
import statistics
from functools import partial
import code
from scipy.optimize import brute
from django.core.management import BaseCommand
from optparse import make_option
import matplotlib.pyplot as plt
import numpy as np
import asyncio

MINIMUM_WAGE=10.20


def date_to_datetime(time_string):
    return datetime.datetime.strptime(time_string, '%m/%d/%Y')

    
# create a monthly continuous time series to pull from
# interpolate values from trend
# set prediction from new values from artificially generated time series.


def check_for_extreme_values(sequence, sequence_to_check=None):
    print("started check")
    data = [sequence.ix[i].Price for i in sequence.index]
    print("moved things to a list")
    final_data = []
    for elem in data:
        try:
            len(elem)
            for i in range(len(elem)):
                final_data.append(float(elem[i]))
        except:
            final_data.append(elem)
    print("finished for loop")
    print("finished post processing")
    sequence = final_data[:]
    mean = statistics.mean(sequence)
    stdev = statistics.stdev(sequence)
    if sequence_to_check is not None:
        for val in sequence_to_check:
            if val >= mean + (stdev*2):
                sequence_to_check.remove(val)
            elif val <= mean - (stdev*2):
                sequence_to_check.remove(val)
        return sequence_to_check
    else:
        for val in sequence:
            if val >= mean + (stdev*2):
                return True
            elif val <= mean - (stdev*2):
                return True
        return False

def remove_extreme_values(sequence, sequence_to_check=None):    
    data = [float(sequence.ix[i]) for i in sequence.index]
    print("moved things to a list")
    
    mean = statistics.mean(data)
    stdev = statistics.stdev(data)
    print("created mean, std")
    new_sequence = sequence.copy()
    for ind,val in enumerate(data):
        if val >= mean + (stdev*2):
            new_sequence = new_sequence.drop(sequence.index[ind])
        elif val <= mean - (stdev*2):
            new_sequence = new_sequence.drop(sequence.index[ind])
    print("removed bad values")
    return new_sequence


def date_range_generate(start,end):
    start_year = int(start.year)
    start_month = int(start.month)
    end_year = int(end.year)
    end_month = int(end.month)
    dates = [datetime.datetime(year=start_year, month=month, day=1) for month in range(start_month, 13)]
    for year in range(start_year+1, end_year+1):
        dates += [datetime.datetime(year=year, month=month, day=1) for month in range(1,13)]
    return dates


def interpolate(series):
    date_list = list(series.index)
    date_list.sort()
    dates = date_range_generate(date_list[0], date_list[-1])
    for date in dates:
        if date not in list(series.index):
            series = series.set_value(date, np.nan)
    series = series.interpolate(method="values")
    to_remove = [elem for elem in list(series.index) if elem.day != 1]
    series.drop(to_remove, inplace=True)
    return series


def check_for_singular(data):
    prices = set([data.ix[index]["Price"] for index in data.index])
    if len(prices) == 1:
        return True
    else:
        return False

#break out seasonal decomposition code
#test to make sure model_order is consistently returning same result for same data
#test flow of control like before
#test to make sure the same extreme values are consistently removed for the same data
#make sure clean data returns consistent result
#check_for_singular code to make sure it works as expected
#check generate_date_range
#check the return statements - mypy

def get_median_price(data: pd.DataFrame) -> pd.DataFrame:
    """
    If multiple prices appear for a given date, 
    we take the median of all prices
    
    Parameters
    ----------
    * data - dataframe of data
    """
    new_data = pd.DataFrame()
    for timestamp in set(data.index):
        if len(data.ix[timestamp]) > 1:
            tmp_df = data.ix[timestamp].copy()
            new_price = statistics.median([tmp_df.iloc[index]["Price"] for index in range(len(tmp_df))])
            series = tmp_df.iloc[0]
            series["Price"] = new_price
            new_data = new_data.append(series)
        else:
            new_data = new_data.append(data.ix[timestamp])
    return new_data

def get_trend_of_data(data: pd.DataFrame):
    if len(data) > 52:
        trend = sm.tsa.seasonal_decompose(data["Price"], freq=52).trend
    elif len(data) > 12:
        trend = sm.tsa.seasonal_decompose(data["Price"], freq=12).trend
    else:
        return None

# TODO: verify returns pd.Series
def fill_missing_trend(trend) -> pd.Series:
    if trend is None:
        return None
    else:
        trend = trend.fillna(0)
        trend = trend.iloc[trend.nonzero()[0]]
        return trend


def fill_missing_cleaned(cleaned_data) -> pd.DataFrame:
    s = cleaned_data.T.squeeze()
    s.sort_index(inplace=True)
    print("sorted index by date")
    # clearing out NaNs
    new_data = s.fillna(0)
    new_data = new_data.iloc[new_data.nonzero()[0]]
    return new_data


def trend_clean(data):
    print("inside of trend predict")
    cleaned_data = get_median_price(data)
    print("finished cleaning data")
    if check_for_singular(cleaned_data):
        return None
    print("checked for singularity")
    # seasonal decompose
    data = data.dropna()
    trend = get_trend_of_data(data)
    print("finished creating trend")
    trend = fill_missing_trend(trend)
    new_data = fill_missing_cleaned(cleaned_data)
    interpolated_data = interpolate(new_data.copy())
    print("interpolated data")
    interpolated_data = remove_extreme_values(interpolated_data)
    print("removed extreme data")
    return trend, interpolated_data
    
def is_nan(obj):
    if type(obj) == type(float()):
        return math.isnan(obj)
    else:
        return False

#make sure it's possible to connect to the database
#make sure each branch of my code is exercises.
#write a test for each every if, else statement
#stringio instance via monkey patching
#test to make sure minimum_wage is used throughout!!!

def gather_prices(labor_category: str) -> pd.DataFrame:
    labor_objects = LaborCategory.objects.filter(labor_category=labor_category)
    if len(labor_objects) < 12: #there isn't enough data for a prediction in this case
        return None
    print("completed lookup")
    df = pd.DataFrame()
    for labor_object in labor_objects:
        df = df.append({
            "Date": labor_object.date,
            "Price": float(labor_object.price)
        }, ignore_index=True)
    return df

def index_by_time(df: pd.DataFrame) -> pd.DataFrame:
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")
    df.sort_index(inplace=True)
    return df

def save_trend(trend: pd.Series, labor_category: str) -> None:
    if trend is not None:
        for ind in range(len(trend)):
            trend_elem = Trend(
                labor_key=labor_category,
                trend=trend[ind],
                start_date=trend.index[ind])
            trend_elem.save()
        print("Saved trend results")

def save_interpolated_data(interpolated_data: pd.Series, labor_category: str) -> None:
    if interpolated_data is not None:
        for ind in range(len(interpolated_data)):
            inter_data = InterpolatedData(
                labor_key=labor_category,
                interpolated_data=interpolated_data[ind],
                start_date=interpolated_data.index[ind])
            inter_data.save()
        print("Saved Interpolated Data results")
        
async def main(labor_category):
    df = gather_prices(labor_category)
    if df is None:
        return 
    # sanity checking this is a datetime
    print("created dataframe")
    df = index_by_time(df)
    print("completed dataframe sorting")
    result = trend_clean(df)
    print("finished prediction")
    if result is None:
        return
    trend, interpolated_data = result
    print("got result")
    save_trend(trend, labor_category)
    save_interpolated_data(interpolated_data, labor_category)
    
class Command(BaseCommand):

    def handle(self, *args, **options):
        InterpolatedData.objects.all().delete()
        Trend.objects.all().delete()
        labor_categories = [i for i in LaborCategory.objects.all() if i.labor_category]
        labor_categories = set([i.labor_category for i in labor_categories])
        loop = asyncio.get_event_loop()
        for index, labor_category in enumerate(labor_categories):
            loop.run_until_complete(main(labor_category))
        loop.close()

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

"""
A bit about this file - Python is a great language full of lots of useful data science libraries.  But it's not that fast.  For this reason we use a series of functions which send data to json files, which can be used by the language as Python Dictionaries.  Because of the size of the data, big but not *that* big, it made sense to chop up the tasks and not repeat computation unless necessary.  Otherwise debugging and iteration would be difficult, because just processing the data, takes a while.

Therefore we have the following methods:

making_categories - which maps individual labor categories into buckets across three fields - education level, years of experience and schedule.

I don't really undetstand what a schedule is, but it's kind of like a geographic region?  As well as a business line / set of skills.  So, if you are a schedule 70, it's likely you're in IT and it's even more likely you're a software developer.  It's worth stating that there is talk of moving over to SIN numbers which are used by the government to do something similar to the schedule, but at a more granular level.  Sometimes these SIN numbers have semantic data attached.  And sometimes, they do not.  So it's best to think of them as unique identifiers.  For this reason, it might be worth it to update this script down the road to work off of SIN numbers.  But for right now schedule seems like the right call.

"""

def is_nan(obj):
    if type(obj) == type(float()):
        return math.isnan(obj)
    else:
        return False
    
def money_to_float(string):
    """
    hourly wages have dollar signs and use commas, 
    this method removes those things, so we can treat stuff as floats
    """
    if type(string) == type(str()):
        string = string.replace("$","").replace(",","")
        return float(string)
    else:
        return string

def load_data():
    """
    this loads all the csv's into memory and then returns them.
    Note that only versioned csv's are returned, because the one without a version number
    is also the highest numbered CSV.  This avoids *some* double counting.
    """
    #loading the datasets into memory
    os.chdir("data")
    data_sets = ["hourly_prices_v1.csv","hourly_prices_v2.csv","hourly_prices_v3.csv","hourly_prices_v4.csv"]
    dfs = [pd.read_csv(data_set) for data_set in data_sets]
    os.chdir("..")
    return dfs

def date_to_datetime(time_string):
    return datetime.datetime.strptime(time_string, '%m/%d/%Y')

def making_categories():
    """
    This function assumes there is a folder called data, that contains csv's with data on schedule information 
    of different positions to contract for.
    this function creates a mapping from labor categories to education level + years of experience + schedule
    """
    
    dfs = load_data()
    #making use of the mapping of Labor Category to higher level categorization
    categories = {
        "None":{
            "0-5":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "6-10":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "11-15":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            }
        },
        "High School":{
            "0-5":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "6-10":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "11-15":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            }
        },
        "Associates":{
            "0-5":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "6-10":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "11-15":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            }
        },
        "Bachelors":{
            "0-5":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "6-10":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "11-15":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            }
        },
        "Masters":{
            "0-5":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "6-10":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "11-15":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            }
        },
        "Ph.D.":{
            "0-5":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "6-10":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "11-15":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            }
        }
    }
    seen_labor_categories = []
    years_exp = ""
    for df in dfs:
        for index in df.index:
            #this handles double counting, because about 1 out of every 100- every 1000 are double counted
            if df.ix[index]["Labor Category"] in seen_labor_categories: continue
            else:
                seen_labor_categories.append(df.ix[index]["Labor Category"])
            #This part of the code classifies the data into buckets based on some simple rules.
            if df.ix[index]["MinExpAct"] <6 or is_nan(df.ix[index]):
                years_exp = "0-5"
            elif df.ix[index]["MinExpAct"] >=6 and df.ix[index]["MinExpAct"] < 11:
                years_exp = "6-10"
            elif df.ix[index]["MinExpAct"] >= 11 and df.ix[index]["MinExpAct"] < 16:
                years_exp = "11-15"
            
            education_level = df.ix[index]["Education"] if not is_nan(df.ix[index]["Education"]) else "None" 
            categories[ education_level ][ years_exp ][ df.ix[index]["Schedule"] ]["freq"] += 1
            categories[ education_level ][ years_exp ][ df.ix[index]["Schedule"] ]["labor categories"].append(df.ix[index]["Labor Category"])
            
    json.dump(categories,open("categories.json","w"))

def making_labor_category_to_high_level():
    """
    This function assumes making_categories has been called.  
    It creates a mapping from individual labor categories to a higher level mapping which will be used in the time series analysis.
    Using this function we will create broad labor categories with enough data for a meaningful timeseries
    """
    list_of_categories = []
    categories = json.load(open("categories.json","r"))
    labor_category_to_high_level_category = {}
    for education_level in categories.keys():
        for years_of_experience in categories[education_level].keys():
            for schedule in categories[education_level][years_of_experience].keys():
                for labor_category in categories[education_level][years_of_experience][schedule]["labor categories"]:
                    labor_category_to_high_level_category[labor_category] = education_level +"_"+ years_of_experience +"_"+ schedule
                    if education_level +"_"+ years_of_experience +"_"+ schedule not in list_of_categories:
                        list_of_categories.append(education_level +"_"+ years_of_experience +"_"+ schedule)
    json.dump(labor_category_to_high_level_category,open("labor_category_to_high_level_category.json","w"))
    return list_of_categories

#this comes from here: http://stackoverflow.com/questions/22770352/auto-arima-equivalent-for-python
def objective_function(order,endogenous,exogenous=None):
    if exogenous:
        fit = sm.tsa.ARIMA(endogenous,order,exogenous).fit()
    else:
        fit = sm.tsa.ARIMA(endogenous,order).fit()
    return fit.aic()

def model_search(data,exogenous_data=None):
    grid = (slice(1,3,1),slice(1,3,1),slice(1,3,1))
    if exogenous_data:
        return brute(objective_function, args=(data,exogenous_data), finish=None)
    else:
        return brute(objective_function, args=(data), finish=None)

if not os.path.exists("categories.json"):
    making_categories()

if __name__ == '__main__':
    start = time.time()
    dfs = load_data()
    print("loaded_data, took:",time.time() - start)
    start = time.time()
    labor_category = json.load(open("labor_category_to_high_level_category.json","r"))
    list_of_categories = making_labor_category_to_high_level()
    set_of_time_series = {}.fromkeys(list_of_categories,pd.DataFrame())
    print("loaded json, ran making_labor_category_to_high_level, took:",time.time() - start)

    compressed_dfs = [pd.DataFrame() for _ in range(len(dfs))]
    start = time.time()
    for ind,df in enumerate(dfs):
        compressed_dfs[ind]["Year 1/base"] = df["Year 1/base"]
        compressed_dfs[ind]["Begin Date"] = df["Begin Date"]
        compressed_dfs[ind]["Labor Category"] = df["Labor Category"]
    print("compressed dataframes, took", time.time() - start)
    
    for df in compressed_dfs:
        for ind in df.index:
            labor_cat = labor_category[df.ix[ind]["Labor Category"]]
            set_of_time_series[labor_cat] = set_of_time_series[labor_cat].append(df.ix[ind])
    print("categorizing dataframes, took:", time.time() - start)

    start = time.time()
    for category in set_of_time_series.keys():
        set_of_time_series[category].index = [date_to_datetime(elem) for elem in set_of_time_series[category]["Begin Date"]]
        del set_of_time_series[category]["Begin Date"]
        del set_of_time_series[category]["Labor Category"]
    print("organizing categorized dataframes took:", time.time() - start)

    print("starting model search")
    start = time.time()
    keys = list(set_of_time_series.keys())
    keys.sort()
    
    set_of_time_series = {key:set_of_time_series[key].sort_index(axis=0) for key in keys}
    models = []
    for key in keys:
        dta = set_of_time_series[key]
        models.append({"category":key,"model":model_search(dta)})
    print("finished model search, in:",time.time() - start)
    # models = []
    
    # keys = list(set_of_time_series.keys())
    # keys.sort()
    # dta = set_of_time_series[keys[0]]
    # dta = dta.sort_index(axis=0)
    # dta["Year 1/base"] = dta["Year 1/base"].apply(lambda x:math.log(x))
    
    # model = sm.tsa.ARIMA(dta,(1,1,0)).fit()
    # model.fittedvalues = model.fittedvalues.apply(lambda x:x+4)
    # dicter = {"category":keys[0],"model":model}
    # models.append(dicter)

    # dta = set_of_time_series[keys[1]]
    # dta = dta.sort_index(axis=0)
    # model = sm.tsa.ARIMA(dta,(0,1,2)).fit()
    # model.fittedvalues = model.fittedvalues.apply(lambda x:x+62)
    # dicter = {"category":keys[1],"model":model}
    # models.append(dicter)

    # dta = set_of_time_series[keys[2]]
    # dta = dta.sort_index(axis=0)
    # model = sm.tsa.ARIMA(dta,(0,1,2)).fit()
    # model.fittedvalues = model.fittedvalues.apply(lambda x:x+50)
    # dicter = {"category":keys[1],"model":model}
    # models.append(dicter)
    
    # import IPython
    # IPython.embed()
    

import pandas as pd
from glob import glob
import os
import json

"""
A bit about this file - Python is a great language full of lots of useful data science libraries.  But it's not that fast.  For this reason we use a series of functions which send data to json files, which can be used by the language as Python Dictionaries.  Because of the size of the data, big but not *that* big, it made sense to chop up the tasks and not repeat computation unless necessary.  Otherwise debugging and iteration would be difficult, because just processing the data, takes a while.

Therefore we have the following methods:

making_categories - which maps individual labor categories into buckets across three fields - education level, years of experience and schedule.

I don't really undetstand what a schedule is, but it's kind of like a geographic region?  As well as a business line / set of skills.  So, if you are a schedule 70, it's likely you're in IT and it's even more likely you're a software developer.  It's worth stating that there is talk of moving over to SIN numbers which are used by the government to do something similar to the schedule, but at a more granular level.  Sometimes these SIN numbers have semantic data attached.  And sometimes, they do not.  So it's best to think of them as unique identifiers.  For this reason, it might be worth it to update this script down the road to work off of SIN numbers.  But for right now schedule seems like the right call.

"""

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
    data_sets = glob("*.csv")
    dfs = [pd.read_csv(data_set) for data_set in data_sets if "_v" in data_set]
    os.chdir("..")
    return dfs

def making_categories():
    """
    This function assumes there is a folder called data, that contains csv's with data on schedule information 
    of different positions to contract for.
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
                "AIMS":{"freq":0,"labor categories":[]}
            },
            "6-10":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]}
            },
            "11-15":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]}
            }
        },
        "High School":{
            "0-5":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]}
            },
            "6-10":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]}
            },
            "11-15":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]}
            }
        },
        "Associates":{
            "0-5":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]}
            },
            "6-10":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]}
            },
            "11-15":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]}
            }
        },
        "Bachelors":{
            "0-5":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]}
            },
            "6-10":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]}
            },
            "11-15":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]}
            }
        },
        "Masters":{
            "0-5":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]}
            },
            "6-10":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]}
            },
            "11-15":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]}
            }
        },
        "Ph.D.":{
            "0-5":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]}
            },
            "6-10":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]}
            },
            "11-15":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]}
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
            if df.ix[index]["MinExpAct"] <6:
                years_exp = "0-5"
            elif df.ix[index]["MinExpAct"] >=6 and df.ix[index]["MinExpAct"] < 11:
                years_exp = "6-10"
            elif df.ix[index]["MinExpAct"] >= 11 and df.ix[index]["MinExpAct"] < 16:
                years_exp = "11-15"
            try:
                categories[ df.ix[index]["Education"] ][ years_exp ][ df.ix[index]["Schedule"] ]["freq"] += 1
            except:
                continue
            categories[ df.ix[index]["Education"] ][ years_exp ][ df.ix[index]["Schedule"] ]["labor categories"].append(df.ix[index]["Labor Category"])
            
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

dfs = load_data()
if not os.path.exists("categories.json"):
    making_categories()
    
list_of_categories = making_labor_category_to_high_level()

labor_category = json.load(open("labor_category_to_high_level_category.json","r"))

set_of_time_series = {}.fromkeys(list_of_categories,pd.DataFrame())

counter = 0
counter_labor = 0
for df in dfs:
    try:
        df.ix[0]['Schedule']
    except:
        continue
    for ind in df.index:
        counter += 1
        if df.ix[ind]["Labor Category"] in list(labor_category.keys()):
            counter_labor += 1
        #labor_cat = labor_category[labor_category[df.ix[ind]["Labor Category"]]]

        #set_of_time_series[labor_cat].append(df.ix[ind])


import code
code.interact(local=locals())

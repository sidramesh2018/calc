#Price Prediction

##Intro

Description of the tool, what it does, why, and how

##Requirements

The following python packages are required to get things to work:

```
scipy==0.18.1
pandas==0.18.0
numpy==1.11.2
statsmodels==0.6.1
```

The following python packages are optional, but recommended, so that you can debug your models:

`matplotlib==1.5.1`

These optional dependencies can be found in requirements-dev.txt

##Justification of requirements

`statsmodels==0.6.1` - This is the heart of the application.  It has the time series model, which is used for price prediction.  

`scipy==0.18.1, pandas==0.18.0, numpy==1.11.2` - these three packages are dependencies for statsmodels.  

##How the requirements are used

In this section, we'll walk through specifically what parts of the packages that get used.  This way, if these dependencies become stale, either because compliance reasons or other issues, you'll know what you can update.  And what cannot be updated.

```
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy.optimize import brute
```

The above gives some insight into how the code is used.  Specifically, `scipy.optimize`'s `brute` method.  This method runs a brute force algorithm against a function passed in.  [Here are the docs for `brute`](https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.optimize.brute.html). 

Other than the brute method, which might be subject to change.  The rest of the code takes advantage of the basic utility of each of the above packages and is therefore unlikely to change.

##Making things async

Example async function: found in data_capture/jobs.py:

```
@job
def process_bulk_upload_and_send_email(upload_source_id):
    contracts_logger.info(
        "Starting bulk upload processing (pk=%d)." % upload_source_id
    )
    upload_source = BulkUploadContractSource.objects.get(
        pk=upload_source_id
    )

    try:
        num_contracts, num_bad_rows = _process_bulk_upload(upload_source)
        email.bulk_upload_succeeded(upload_source, num_contracts, num_bad_rows)
    except:
        contracts_logger.exception(
            'An exception occurred during bulk upload processing '
            '(pk=%d).' % upload_source_id
        )
        tb = traceback.format_exc()
        email.bulk_upload_failed(upload_source, tb)

    contracts_logger.info(
        "Ending bulk upload processing (pk=%d)." % upload_source_id
    )
```

Method is called here: data_capture/views/bulk_upload.py

`jobs.process_bulk_upload_and_send_email.delay(upload_source_id)`

##Setting up your model

Step 1) Create your lookup table based on the most recent data.

`python manage.py load_lookup_data.py`

Step 2) Train model

`python manage.py generate_arima_model`

##References

* [Rules of thumb for ARIMA models](https://people.duke.edu/~rnau/411arim.htm)

##Data dictionary

Here we will describe the model for the database.  This will include information about each column and each table.

Lookup table



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

    #todo: http://pandas.pydata.org/pandas-docs/stable/io.html#hdf5-pytables storing pandas df to disk
    start = time.time()
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
    
    #serialize model if possible

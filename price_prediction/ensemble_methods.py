from price_prediction.models import FittedValuesByCategory,LaborCategoryLookUp,PriceModels
import pandas as pd
import os
import math
import datetime
import statsmodels.api as sm
from scipy.optimize import brute
import statistics
from functools import partial
import os
import code
import statsmodels.api as sm
import IPython


def trend_predict(data):
    #seasonal decompose 
    if len(data) > 52:
        s = sm.tsa.seasonal_decompose(data["Price"],freq=52)
    elif len(data) > 12:
        s = sm.tsa.seasonal_decompose(data["Price"], freq=12)
    else:
        return None
    #clearing out NaNs
    new_data = data.fillna(0)
    new_data = new_data.iloc[new_data.nonzero()[0]]
    sm.tsa.x13_arima_select_order(new_data)
    IPython.embed()
    model = sm.tsa.ARIMA(new_data,model_order).fit()
    model.fittedvalues = setting_y_axis_intercept(new_data,model)
    return model,new_data,model_order

labor_categories = [elem.labor_key for elem in LaborCategoryLookUp.objects.all()]
order_terms = []
for labor_category in labor_categories:
    labor_objects = LaborCategoryLookUp.objects.filter(labor_key=labor_category)
    df = pd.DataFrame()
    for labor_object in labor_objects:
        df = df.append({"Date":labor_object.start_date,"Price":float(labor_object.labor_value)},ignore_index=True)
    #sanity checking this is a datetime
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")
    df.sort_index(inplace=True)
    model,new_data,order = trend_predict(df)


IPython.embed()

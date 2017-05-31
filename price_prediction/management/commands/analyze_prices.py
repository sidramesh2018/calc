#building off of calc/contracts/management/commands
import os
import logging
import asyncio
import pandas as pd
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.core.management import BaseCommand
from optparse import make_option
from django.core.management import call_command
import statistics as st
import numpy as np
from price_prediction.models import LaborCategory, CompressedData
import shutil
from scipy import stats
import json
import plotly
from plotly.graph_objs import Bar,Layout,Scatter, Box, Annotation,Marker,Font,XAxis,YAxis 

#write tests for this -

# make sure each of these functions performs appropriately
# - smoke test
# - (minimal) doc tests
# - edge cases
# - check to make sure data is saved to the database

def is_nan(obj):
    if type(obj) == type(float()):
        return math.isnan(obj)
    else:
        return False


def count_outliers(data):
    outliers_num = 0
    mean = st.mean(data)
    stdev = st.stdev(data)
    for elem in data:
        if (elem > mean + (2*stdev)) or (elem < mean - (2*stdev)):
            outliers_num += 1
    return outliers_num

def first_quartile(List):
    if len(List) >= 4:
        List.sort()
        if len(List) % 2 != 0:
            middle_number = st.median(List)
            return st.median(List[:List.index(middle_number)])
        else:
            middle_index = len(List)//2
            middle_number = List[middle_index]
            return st.median(List[:List.index(middle_number)])
    else:
        return None    

#Question 9
#Write a python function implementing a function that returns the first quantile of a set of numbers
def third_quartile(List):
    if len(List) >= 4:
        List.sort()
        if len(List) % 2 != 0:
            middle_number = st.median(List)
            return st.median(List[List.index(middle_number):])
        else:
            middle_index = len(List)//2
            middle_number = List[middle_index]
            return st.median(List[List.index(middle_number):])
    else:
        return None    

def quartile_analysis(data):
    if len(data) < 5:
        return None
    q1 = first_quartile(data)
    q3 = third_quartile(data)
    median = st.median(data)
    if abs(median - q1) > abs(median - q3):
        return abs(median - q1)
    else:
        return abs(median - q3)

def big_picture_analysis(labor_data):
    categories = set([elem.labor_category for elem in labor_data])
    central_tendency = []
    spread = []
    outliers = []
    iqrs = []
    for category in categories:
        data = LaborCategory.objects.filter(labor_category=category).all()
        prices = [round(float(elem.price),2) for elem in data]
        if len(prices) > 5 and stats.normaltest(prices).pvalue > 0.05:
            spread.append([category, st.stdev(prices)])
            central_tendency.append([category, st.mean(prices)])
        else:
            try:
                spread.append([category, quartile_analysis(prices)])
            except:
                spread.append([category, min_max(prices)])
            central_tendency.append([category, st.median(prices)])
        outliers.append([category, count_outliers(prices)])
    sorted(central_tendency, key=lambda x: x[1])
    sorted(spread, key=lambda x: x[1])
    sorted(outliers, key=lambda x: x[1])
    bar_plot(central_tendency,"center.html")
    bar_plot(spread,"spread.html")
    bar_plot(outliers,"outlier_count.html")
    print("central tendency",st.median([elem[1] for elem in  central_tendency]))
    print("spread",st.median([elem[1] for elem in spread]))
    print("outliers",st.median([elem[1] for elem in outliers]))

def bar_plot(data,filename):
    filename = "/Users/ericschles/Documents/projects/calc/price_prediction/"+filename
    x_vals = [elem[0] for elem in  data]
    y_vals = [elem[1] for elem in data]
        
    plotly.offline.plot({
        "data":[Bar(x=x_vals,y=y_vals)],
        "layout":Layout(
            title=filename.split(".")[0]
        )
    },auto_open=False)
    shutil.move("temp-plot.html",filename)

def min_max(data):
    data.sort()
    return abs(data[-1] - data[0])

def plot_bar_chart(data,name,title):
    x_vals = list(data.keys())
    x_vals.sort()
    y_vals = [data[key] for key in x_vals]
    #text = ["with count of "+str(len(data[key])) for key in x_vals] 
    x_vals = [str(elem) for elem in x_vals]
    plotly.offline.plot({
        "data":[Bar(x=x_vals,y=y_vals)],
        "layout":Layout(
            title=title
        )
    },auto_open=False)
    
    shutil.move("temp-plot.html","/Users/ericschles/Documents/projects/calc/price_prediction/viz/"+name+".html")     

def plot_bar_chart2(data,x_vals,name,title):
    y_vals = [data[key] for key in x_vals]
    text = ["with count of "+str(len(data[key])) for key in x_vals] 
    x_vals = [str(elem) for elem in x_vals]
    plotly.offline.plot({
        "data":[Bar(x=x_vals,y=y_vals,text=text)],
        "layout":Layout(
            title=title
        )
    },auto_open=False)
    
    shutil.move("temp-plot.html","/Users/ericschles/Documents/projects/calc/price_prediction/viz/"+name+".html")     

class Command(BaseCommand):
    #do year over year analysis
    def handle(self, *args, **options):
        #labor_data = LaborCategory.objects.all()
        #big_picture_analysis(labor_data)
        data = CompressedData.objects.all()
        overall_spread = []
        data_by_year = {}
        for datum in data:
            if not int(datum.year) in data_by_year.keys():
                data_by_year[int(datum.year)] = [float(datum.price)]
            else:
                data_by_year[int(datum.year)].append(float(datum.price))
        #import code
        #code.interact(local=locals())
        years = list(data_by_year.keys())
        years.sort()
        years = years[:-1]
        spread_year_over_year = {}
        center_year_over_year = {}
        outliers_per_year = {}
        mean_year_over_year = {}
        stdev_year_over_year = {}
        for year in years:
            if stats.normaltest(data_by_year[year]).pvalue > 0.05:
                spread_year_over_year[year] = st.stdev(data_by_year[year])
            else:
                spread_year_over_year[year] = quartile_analysis(data_by_year[year])
            stdev_year_over_year[year] = st.stdev(data_by_year[year])
        for year in years:
            if stats.normaltest(data_by_year[year]).pvalue > 0.05:
                center_year_over_year[year] = st.mean(data_by_year[year])
            else:
                center_year_over_year[year] = st.median(data_by_year[year])
            mean_year_over_year[year] = st.mean(data_by_year[year])
        for year in years:
            for val in data_by_year[year]:
                if val > center_year_over_year[year] + 2*spread_year_over_year[year]: #or val < center_year_over_year[year] - 2*spread_year_over_year[year]:
                    if not year in outliers_per_year.keys():
                        outliers_per_year[year] = 1
                    else:
                        outliers_per_year[year] += 1
        no_outlier_data_by_year = {}
        for year in years:
            for val in data_by_year[year]:
                if val > center_year_over_year[year] + 2*spread_year_over_year[year]: #or val < center_year_over_year[year] - 2*spread_year_over_year[year]:
                    continue
                else:
                    if not year in no_outlier_data_by_year.keys():
                        no_outlier_data_by_year[year] = [val]
                    else:
                        no_outlier_data_by_year[year].append(val)
        no_outlier_spread_year_over_year = {}
        no_outlier_center_year_over_year = {}
        for year in years:
            if stats.normaltest(no_outlier_data_by_year[year]).pvalue > 0.05:
                no_outlier_spread_year_over_year[year] = st.stdev(no_outlier_data_by_year[year])
            else:
                no_outlier_spread_year_over_year[year] = quartile_analysis(no_outlier_data_by_year[year])
        for year in years:
            if stats.normaltest(no_outlier_data_by_year[year]).pvalue > 0.05:
                no_outlier_center_year_over_year[year] = st.mean(no_outlier_data_by_year[year])
            else:
                no_outlier_center_year_over_year[year] = st.median(no_outlier_data_by_year[year])


        # print("center analysis")
        # for index in range(len(years)):
        #     print("In",years[index],"the center of the price was",no_outlier_center_year_over_year[years[index]],"with a count of",len(no_outlier_data_by_year[years[index]]))
        # for index in range(len(years)):
        #     try:
        #         print("From",years[index],"to",years[index+1],"the average price changed by",no_outlier_center_year_over_year[years[index+1]] - no_outlier_center_year_over_year[years[index]])
        #     except:
        #         break
            
        # print("spread analysis")
        
        # for index in range(len(years)):
        #     print("In",years[index],"the spread of the price was",no_outlier_spread_year_over_year[years[index]],"with a count of",len(no_outlier_data_by_year[years[index]]))
        # for index in range(len(years)):
        #     try:
        #         print("From",years[index],"to",years[index+1],"the spread in price changed by",no_outlier_spread_year_over_year[years[index+1]] - no_outlier_spread_year_over_year[years[index]])
        #     except:
        #         break
        

        from inflation_calc import CPI

        cpi = CPI()
        cpi_data = {}
        for index in range(len(years)):
            try:
                cpi_data[years[index+1]] = cpi.data["United States"][years[index+1]] - cpi.data["United States"][years[index]]
            except:
                break
            
        print("center analysis")
        #graph associated
        plot_bar_chart(center_year_over_year,"center_year_over_year","center year over year")
        for index in range(len(years)):
            print("In",years[index],"the center of the price was",center_year_over_year[years[index]],"with a count of",len(data_by_year[years[index]]))
        
        print("change year over year:")
        differences_in_average = {}
        x_vals = []
        for index in range(len(years)):
            try:
                print("From",years[index],"to",years[index+1],"the average price changed by",center_year_over_year[years[index+1]] - center_year_over_year[years[index]])
                differences_in_average[str(years[index])+" to "+str(years[index+1])] = center_year_over_year[years[index+1]] - center_year_over_year[years[index]]
                x_vals.append(str(years[index])+" to "+str(years[index+1]))
            except:
                break
        plot_bar_chart(differences_in_average,"differences_in_average","differences in average year over year")
        print("differencing against cpi:")
        diff_ave_against_cpi = {}
        differences_in_average_with_cpi = []
        for index in range(len(years)):
            try:
                print("From",years[index],"to",years[index+1],"the average price changed by",(center_year_over_year[years[index+1]] - center_year_over_year[years[index]]) - cpi_data[years[index+1]])
                differences_in_average_with_cpi.append((center_year_over_year[years[index+1]] - center_year_over_year[years[index]]) - cpi_data[years[index+1]])
                diff_ave_against_cpi[str(years[index])+" to "+str(years[index+1])] = (center_year_over_year[years[index+1]] - center_year_over_year[years[index]]) - cpi_data[years[index+1]]
            except:
                break
        plot_bar_chart(diff_ave_against_cpi,"difference_in_average_with_cpi","difference in average year over year, compared with CPI")
        print("differences in average",sum(differences_in_average_with_cpi[:-1])/float(len(differences_in_average_with_cpi[:-1])))

        print("mean versus median analysis")
        print("mean year over year")
        for index in range(len(years)):
            print("In",years[index],"the mean of the price was",mean_year_over_year[years[index]],"with a count of",len(data_by_year[years[index]]))
        print("difference between mean and median in absolute value")
        plot_bar_chart(mean_year_over_year,"mean_year_over_year","mean year over year")
        differences_in_median_mean_average = []

        differences_in_median_mean_ave = {}
        for index in range(len(years)):
            print("In",years[index],"the difference between the mean of the price and the median of the price was",round(abs(mean_year_over_year[years[index]] - center_year_over_year[years[index]]), 2))
            differences_in_median_mean_average.append(round(abs(mean_year_over_year[years[index]] - center_year_over_year[years[index]]), 2))
            differences_in_median_mean_ave[years[index]] = round(abs(mean_year_over_year[years[index]] - center_year_over_year[years[index]]), 2)
        print("differences in median v mean on average",sum(differences_in_median_mean_average[:-1])/float(len(differences_in_median_mean_average[:-1])))
        plot_bar_chart(differences_in_median_mean_ave,"differences_in_median_mean_average","differences in median mean average")
        
        print("median with outliers and without outliers")
        no_outlier_center_year_over_year_dict = {}
        for index in range(len(years)):
            print("In",years[index],"the center of the price without outliers was",no_outlier_center_year_over_year[years[index]],"with a count of",len(no_outlier_data_by_year[years[index]]))
            no_outlier_center_year_over_year_dict[years[index]] = no_outlier_center_year_over_year[years[index]]
        plot_bar_chart(no_outlier_center_year_over_year_dict,"no_outlier_center_year_over_year","no outlier center year over year")
        
        print("difference between center with outliers and without:")
        differences_with_outliers = []
        diff_with_outliers = {}
        for index in range(len(years)):
            print("In",years[index],"the difference between the center of the price with and without outliers was",round(abs(no_outlier_center_year_over_year[years[index]] - center_year_over_year[years[index]]), 2))
            differences_with_outliers.append(round(abs(no_outlier_center_year_over_year[years[index]] - center_year_over_year[years[index]]), 2))
            diff_with_outliers[years[index]] = round(abs(no_outlier_center_year_over_year[years[index]] - center_year_over_year[years[index]]), 2)
        print("the average difference with versus without outliers for the center of the data",st.mean(differences_with_outliers[:-1]))
        plot_bar_chart(diff_with_outliers,"difference_with_outliers","difference with outliers")
        print("spread analysis")

        spread_over_years = {}
        for index in range(len(years)):
            print("In",years[index],"the spread of the price was",spread_year_over_year[years[index]],"with a count of",len(data_by_year[years[index]]))
            spread_over_years[years[index]] = spread_year_over_year[years[index]]
        plot_bar_chart(spread_over_years,"spread_over_years","spread year over year")

        diff_spread = {}
        for index in range(len(years)):
            try:
                print("From",years[index],"to",years[index+1],"the spread in price changed by",spread_year_over_year[years[index+1]] - spread_year_over_year[years[index]])
                diff_spread[str(years[index])+" to "+str(years[index+1])] = spread_year_over_year[years[index+1]] - spread_year_over_year[years[index]]
            except:
                break
        plot_bar_chart(diff_spread,"difference_in_spread_year_over_year","difference in spread year over year")
        print("understanding outliers")

        percent_outliers_year_over_year = {}
        for index in range(len(years)):
            print(
                "In",years[index],"the number of outliers were",outliers_per_year[years[index]],"with a count of",len(data_by_year[years[index]]),
                "thats",round((float(outliers_per_year[years[index]])/len(data_by_year[years[index]]))*100,2),"percent of the data"
                )
            percent_outliers_year_over_year[years[index]] = round((float(outliers_per_year[years[index]])/len(data_by_year[years[index]]))*100,2)
        plot_bar_chart(percent_outliers_year_over_year,"percent_outliers_year_over_year","percent outliers year over year")

        no_outlier_spread = {}
        for index in range(len(years)):
            print("In",years[index],"the spread of the price was",no_outlier_spread_year_over_year[years[index]],"with a count of",len(no_outlier_data_by_year[years[index]]))
            no_outlier_spread[years[index]] = no_outlier_spread_year_over_year[years[index]]
        plot_bar_chart(no_outlier_spread,"no_outlier_spread","no outlier spread year over year")

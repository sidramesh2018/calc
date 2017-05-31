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

def is_nan(obj):
    if type(obj) == type(float()):
        return math.isnan(obj)
    else:
        return False

class Command(BaseCommand):
    #do year over year analysis
    def handle(self, *args, **options):
        labor_data = LaborCategory.objects.all()
        categories = set([labor_datum.labor_category for labor_datum in labor_data])
        mean_prices = 0
        median_prices = 0
        for category in categories:
            labor_objects = LaborCategory.objects.filter(labor_category=category)
            mean_prices += st.mean([float(labor_object.price) for labor_object in labor_objects if not is_nan(float(labor_object.price))])
            median_prices += st.median([float(labor_object.price) for labor_object in labor_objects if not is_nan(float(labor_object.price))])
        print("The total number of hours assuming the mean is the chosen price",mean_prices)
        print("The total number of hours assuming the median is the chosen price",median_prices)
        print("The difference between the two",mean_prices - median_prices)

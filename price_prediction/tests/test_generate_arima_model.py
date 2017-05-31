import datetime
from decimal import Decimal
from itertools import cycle

from django.test import TestCase
from contracts.mommy_recipes import get_contract_recipe

from price_prediction.models import FittedValuesByCategory as Fitted
from price_prediction.models import LaborCategory
from price_prediction.models import TrendByCategory as Trend
import pandas as pd
import math
import datetime
import statsmodels.api as sm
import statistics
from functools import partial
import code
from scipy.optimize import brute
import matplotlib.pyplot as plt
import numpy as np
import asyncio

class TestHelperFunctions(TestCase):
    def test_date_to_datetime():
        

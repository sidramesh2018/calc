from management.commands.load_timeseries_data import *
import numpy as np
import datetime as dt
import pandas as pd

def test_money_to_float():
    assert money_to_float("100") == 100.0
    assert money_to_float("$100") == 100.0
    assert money_to_float("$100,000") == 100000.0
    assert money_to_float(np.nan) == 0.0
    assert money_to_float(100) == 100.0
    assert money_to_float(100.00) == 100.00


def test_parse_begindate():
    assert parse_begindate("5/20/2014") == dt.datetime(year=2014, month=5, day=20)
    assert parse_begindate(dt.datetime(year=2014, month=5, day=20)) == dt.datetime(year=2014, month=5, day=20)
    # should raise an error
    try:
        parse_begindate(5)
        assert False
    except ValueError:
        assert True
    try:
        parse_begindate(10.0)
        assert False
    except ValueError:
        assert True
    try:
        parse_begindate("hello there")
        assert False
    except ValueError:
        assert True
    try:
        parse_begindate(True)
        assert False
    except ValueError:
        assert True

        
def test_convert_to_datetime():
    df = pd.DataFrame()
    df = df.append(
        {"a":
         dt.datetime(
             year=2014,
             month=5,
             day=10)
        }, ignore_index=True)
    assert convert_to_datetime(df.ix[0]["a"]) == dt.datetime(year=2014,month=5,day=10)
    assert convert_to_datetime(dt.datetime(year=2014,month=5,day=10)) == dt.datetime(year=2014,month=5,day=10)
    try:
        convert_to_datetime(0)
        assert False
    except ValueError:
        assert True
    try:
        convert_to_datetime("hello")
        assert False
    except:
        assert True
    try:
        convert_to_datetime(0.0)
        assert False
    except:
        assert True
        
def test_increment_year():
    date = dt.datetime(year=2014, month=5, day=20)
    year_plus_one = dt.datetime(
        year=date.year+1,
        month=date.month,
        day=date.day)
    assert increment_year(date) == year_plus_one
    try:
        increment_year(0)
        assert False
    except ValueError:
        assert True
    try:
        increment_year(0.0)
        assert False
    except ValueError:
        assert True
    try:
        increment_year("hello")
    except ValueError:
        assert True
    
# Expliciting missing saving_data_to_db
# Here's how to do it:
# https://docs.djangoproject.com/en/1.11/topics/testing/overview/#writing-tests

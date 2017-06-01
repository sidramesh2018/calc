import os
import logging
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.core.management import BaseCommand
from optparse import make_option
from price_prediction.models import LaborCategory

# write tests for this -

# make sure each of these functions performs appropriately
# - smoke test
# - (minimal) doc tests
# - edge cases
# - check to make sure data is saved to the database

# Q: What does this command do?
# A:
# This file command takes data from contracts/docs/hourly_prices.csv
# and loads it into the database.

# Q: Are there things to watch out for?
# A:
# Yup -
# 1) Mind the upload date
# Here I am specifically referencing find_current_option_startdate
# This function requires 'meta' knowledge, or knowledge about the export date
# This is because the data is loaded from an internal database from a GSA DBA
# The begin dates come from the spreadsheet, so they aren't a problem.
# The export date though, and I cannot highlight this enough, must be known
# Additionally, the option_years parameter is currently set at 5 years, but
# this is necessarily the convention that will always be employed.
# So please take care with this.

# 2) pandas is weird about uploading csv's sometimes
# Right now, I need to call the parse_begindate function
# this parses the begindate field from the csv - hourly_prices.csv
# but that could change in the future?
# In the past, I didn't need to parse out the dates, because they were
# automatically loaded in as datetimes from pd.read_csv.
# I don't know what changed that required this function, but it may be
# unnecessary in the future.


def money_to_float(string: str):
    """
    hourly wages have dollar signs and use commas,
    this method removes those things, so we can treat stuff as floats.

    Parameter
    -----------
    * string - the string version of a dollar amount
    """
    if isinstance(string, str):
        string = string.replace("$", "").replace(",", "")
        return float(string)
    else:
        if pd.isnull(string):
            return 0
        return string


def find_current_option_startdate(export_date, begin_date, option_years=5):
    """
    This function was written with James Seppi @seppi.

    What this function calculates:
    This function tells us what the current start date is,
    for the given period.
    I'm not sure why this is calculated in this way.
    It's related to the data dump
    we get from a GSA DBA.

    Definition: option - a increment period.
    Defintion: export_date - the date of last export, stored as a csv in
    contracts/docs/hourly_prices.csv
    Definition: begin_date - the begin date of the overall contract.

    How these parameters inter-relate semantically:
    The begin_date is the overall begin date of the contract.
    The option_year is the number of years in the current option.
    The contract is split by option_year into periods.
    The current convention (at the time of this writing)
    is that every five years contracts go into
    a new option period.  So if we want to calculate
    the current year of the contract. We need to know the export_date,
    the begin_date and how long the option period is.
    Then we can infer from the csv what period we are in,
    and what cycle of the current period we are in.
    From this information we can infer what the current
    date start date of the given contract is. The reason we need
    to know the current start date, is because the price changes over time.
    And sometimes the contract gets renegotiated at
    a higher (and sometimes lower) rate.

    Parameters
    -----------
    * export_date - a "meta parameter" that is known by the developer.
    This parameter is based on the last export date of
    contracts/docs/hourly_prices.csv
    * begin_date - the start date recorded from
    contracts/docs/hourly_prices.csv
    * option_years - the number of periods for the given option
    """
    years_of_contract = (export_date - begin_date).days/365.2425
    num_option_periods = years_of_contract // option_years
    years = int(num_option_periods*option_years)
    return begin_date + relativedelta(years=years)


def parse_begindate(begin_date) -> datetime:
    """
    Sometimes the begin_date is a string
    And sometimes it's a datetime object.

    Parameters
    ----------
    * begin_date - the begin_date read from the pandas object
    """
    if isinstance(begin_date, str):
        return datetime.strptime(begin_date, "%m/%d/%Y")
    elif isinstance(begin_date, datetime):
        return begin_date
    else:
        raise ValueError("No Begin Date found or could not parse Begin Date")


def convert_to_datetime(current_startdate) -> datetime:
    """
    This function ensures the current_startdate is a
    datetime object.

    Parameters
    ----------
    * current_startdate - the current start date of the contract
    """
    if not isinstance(current_startdate, datetime):
        try:
            return current_startdate.to_datetime()
        except:
            raise ValueError("""
            current_startdate is not a datetime object or convertable to one.
            """)
    return current_startdate


def saving_data_to_db(
        labor_category: str,
        date: datetime, price: float) -> None:
    """
    This function saves to the database.
    This function just serves as a refactor so we don't need to explicitly call
    obj.save() every time.

    Parameters
    ----------
    * labor_category - the labor category for the contract
    (type of worker requested)
    * date - the start date of the contract
    * price - the price of the contract for that start date
    """
    labor_category_obj = LaborCategory(
        labor_category=labor_category,
        date=date,
        price=price
    )
    labor_category_obj.save()


def increment_year(current_startdate: datetime) -> datetime:
    """
    This function increments the start year.
    Since prices are increment for the option period we simply need to
    increment the year to figure out how much the contractor costs, per hour.

    Parameters
    ----------
    * current_startdate - the current start date for the given year
    """
    return datetime(current_startdate.year+1,
                    current_startdate.month,
                    current_startdate.day)


class Command(BaseCommand):

    default_filename = 'contracts/docs/current_labor_categories.xlsx'

    option_list = BaseCommand.option_list + (
        make_option(
            '-f', '--filename',
            default=default_filename,
            help='input filename (.csv, default {})'.format(default_filename)
        ),
    )

    def handle(self, *args, **options):
        log = logging.getLogger(__name__)

        log.info("Begin load_data task")

        log.info("Deleting existing contract records")
        LaborCategory.objects.all().delete()

        filename = args[0]

        if not filename or not os.path.exists(filename):
            raise ValueError('invalid filename')

        filepath = os.path.abspath(filename)
        if filepath.endswith("csv"):
            df = pd.read_csv(filepath)
        elif filepath.endswith("xlsx"):
            df = pd.read_excel(filepath)
        log.info("Processing new datafile")
        for ind in df.index:
            begin_date = parse_begindate(df.ix[ind]["Begin Date"])
            current_startdate = find_current_option_startdate(
                datetime(year=2017,
                         month=1,
                         day=4),
                begin_date,
                option_years=5)

            current_startdate = convert_to_datetime(current_startdate)
            saving_data_to_db(
                df.ix[ind]["Labor Category"],
                current_startdate,
                round(money_to_float(df.ix[ind]["Year 1/base"]))
            )
            current_startdate = increment_year(current_startdate)

            saving_data_to_db(
                labor_category=df.ix[ind]["Labor Category"],
                date=current_startdate,
                price=round(money_to_float(df.ix[ind]["Year 2"]))
            )
            current_startdate = increment_year(current_startdate)

            saving_data_to_db(
                labor_category=df.ix[ind]["Labor Category"],
                date=current_startdate,
                price=round(money_to_float(df.ix[ind]["Year 3"]))
            )
            current_startdate = increment_year(current_startdate)

            saving_data_to_db(
                labor_category=df.ix[ind]["Labor Category"],
                date=current_startdate,
                price=round(money_to_float(df.ix[ind]["Year 4"]))
            )
            current_startdate = increment_year(current_startdate)

            saving_data_to_db(
                labor_category=df.ix[ind]["Labor Category"],
                date=current_startdate,
                price=round(money_to_float(df.ix[ind]["Year 5"]))
            )

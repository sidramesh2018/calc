import abc
import math
from collections import namedtuple
from urllib.parse import urlencode

from django.utils import timezone
from django.db import connection, transaction
from django.db.models import Avg, StdDev
from django.template.loader import render_to_string

from contracts.models import Contract, EDUCATION_CHOICES
from ..models import SubmittedPriceList

from .vocabulary import Vocabulary, broaden_query


# When comparing labor rates in units of standard deviations from
# the mean, we run into potential problems if our comparables have very
# little variance. (We also potentially run into division by zero errors.)
#
# To rectify this, we'll force standard deviations to have a minimum
# value.
MIN_STDDEV = 1

DEFAULT_MIN_COMPARABLES = 4

FoundContracts = namedtuple(
    'FoundContracts',
    ['phrase',
     'contracts',
     'count',
     'finder']
)


class ContractFinder(metaclass=abc.ABCMeta):
    '''
    Abstract base class representing a finder for contracts that match
    a certain criteria.
    '''

    @abc.abstractmethod
    def filter_queryset(self, qs):
        '''
        Return the given Django QuerySet with the matching criteria
        applied to it.
        '''

        raise NotImplementedError()

    @abc.abstractmethod
    def get_data_explorer_qs_params(self):
        '''
        Return a tuple of (name, value) pairs representing querystring
        arguments to pass to the Data Explorer, which will result in a
        Data Explorer URL that filters to this class' matching criteria.
        '''

        raise NotImplementedError()


class BaseEduAndExpFinder(ContractFinder):
    '''
    Abstract base class for finders that match based on minimum
    years of experience and education level.
    '''

    def __init__(self, min_years_experience, education_level):
        self.min_years_experience = min_years_experience
        self.education_level = education_level


class ExactEduAndExpFinder(BaseEduAndExpFinder):
    '''
    Finds contracts that are exactly equal to a given
    minimum experience and education level.
    '''

    def filter_queryset(self, qs):
        return qs.filter(
            min_years_experience=self.min_years_experience,
            education_level=self.education_level
        )

    def get_data_explorer_qs_params(self):
        return (
            ('min_experience', self.min_years_experience),
            ('max_experience', self.min_years_experience),
            ('education', self.education_level),
        )


class GteEduAndExpFinder(BaseEduAndExpFinder):
    '''
    Finds contracts that are greater than or equal to a given
    minimum experience and education level.
    '''

    def get_valid_education_levels(self):
        '''
        Returns a list of education levels that are equal to or
        greater than our own.
        '''

        # TODO: This code is largely copied from
        # api.views, we should consolidate it at some point.
        for index, pair in enumerate(EDUCATION_CHOICES):
            if self.education_level == pair[0]:
                return [
                    ed[0] for ed in EDUCATION_CHOICES[index:]
                ]

    def filter_queryset(self, qs):
        return qs.filter(
            min_years_experience__gte=self.min_years_experience,
            education_level__in=self.get_valid_education_levels()
        )

    def get_data_explorer_qs_params(self):
        return (
            ('min_experience', self.min_years_experience),
            ('education', ','.join(self.get_valid_education_levels())),
        )


def find_comparable_contracts(cursor, vocab, labor_category,
                              min_years_experience, education_level,
                              min_count=DEFAULT_MIN_COMPARABLES,
                              cache=None):
    '''
    Attempt to find contracts that are comparable to the given
    criteria. The search starts out as specific as possible but
    gradually broadens until a minimum number of comparables are found.

    If enough comparables are found, a FoundContracts instance is
    returned. Otherwise, None is returned.
    '''

    if cache is None:
        cache = {}

    finders = [
        ExactEduAndExpFinder(min_years_experience, education_level),
        GteEduAndExpFinder(min_years_experience, education_level),
    ]

    for phrase in broaden_query(cursor, vocab, labor_category, cache,
                                min_count):
        phrase_qs = Contract.objects.all().multi_phrase_search(phrase)
        for finder in finders:
            no_results_key = (
                '{}:no_results'.format(finder.__class__.__name__),
                phrase,
                min_count,
                finder.get_data_explorer_qs_params()
            )
            if no_results_key in cache:
                continue

            contracts = finder.filter_queryset(phrase_qs)
            count = contracts.count()
            if count >= min_count:
                return FoundContracts(
                    phrase=phrase,
                    contracts=contracts,
                    count=count,
                    finder=finder
                )
            else:
                cache[no_results_key] = True
    return None


def get_data_explorer_url(found_contracts):
    # TODO: Use url mapper to get URL for the data explorer.

    params = (
        ('q', found_contracts.phrase),
    ) + found_contracts.finder.get_data_explorer_qs_params()

    return '/?{}'.format(urlencode(params))


def describe(cursor, vocab, labor_category, min_years_experience,
             education_level, price, severe_stddevs=2,
             min_comparables=DEFAULT_MIN_COMPARABLES,
             cache=None):
    if cache is None:
        cache = {}

    result = {
        'severe': False,
        'description': ''
    }

    fc = find_comparable_contracts(
        cursor,
        vocab,
        labor_category,
        min_years_experience,
        education_level,
        min_count=min_comparables,
        cache=cache
    )

    if fc is not None:
        wage_field = 'current_price'
        stats = fc.contracts.aggregate(
            avg=Avg(wage_field),
            stddev=StdDev(wage_field)
        )
        avg = stats['avg']
        stddev = stats['stddev']

        price_delta = abs(price - avg)

        if price_delta > severe_stddevs * stddev:
            result['severe'] = True

        result['count'] = fc.count
        result['avg'] = avg

        if stddev < MIN_STDDEV:
            stddev = MIN_STDDEV

        result['stddev'] = stddev
        result['stddevs'] = math.ceil(price_delta / stddev)

        if result['severe']:
            result['preposition'] = \
                'w' + ('a' * result['stddevs']) + 'y ' + \
                ('below' if price < avg else 'above')

        result['labor_category'] = fc.phrase
        result['url'] = get_data_explorer_url(fc)
        result['description'] = render_to_string(
            'data_capture/analyze_contract.html',
            result
        )

    return result


def analyze_gleaned_data(gleaned_data):
    valid_rows = []

    if gleaned_data.valid_rows:
        cursor = connection.cursor()
        vocab = Vocabulary.from_db(cursor)
        with transaction.atomic():
            sid = transaction.savepoint()
            price_list = SubmittedPriceList(
                is_small_business=False,
                submitter_id=0,
                escalation_rate=0,
                status_changed_at=timezone.now(),
                status_changed_by_id=0,
            )
            price_list.save()
            gleaned_data.add_to_price_list(price_list)
            for row in price_list.rows.all():
                analysis = describe(
                    cursor,
                    vocab,
                    row.labor_category,
                    row.min_years_experience,
                    row.education_level,
                    float(row.base_year_rate),
                )
                valid_rows.append({
                    'analysis': analysis,
                    'sin': row.sin,
                    'labor_category': row.labor_category,
                    'education_level': row.education_level,
                    'min_years_experience': row.min_years_experience,
                    'price': float(row.base_year_rate),
                })
            transaction.savepoint_rollback(sid)

    return valid_rows

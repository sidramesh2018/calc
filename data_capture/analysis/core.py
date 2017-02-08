import math
from urllib.parse import urlencode

from django.utils import timezone
from django.db import connection, transaction
from django.db.models import Avg, StdDev
from django.template.loader import render_to_string

from contracts.models import Contract
from ..models import SubmittedPriceList

from .vocabulary import Vocabulary, broaden_query


def find_comparable_contracts(cursor, vocab, labor_category,
                              min_years_experience, education_level,
                              min_count=30, experience_radius=2,
                              cache=None):
    if cache is None:
        cache = {}

    for phrase in broaden_query(cursor, vocab, labor_category, cache,
                                min_count):
        no_results_key = ('find_comparable_contracts:no_results',
                          phrase, min_years_experience, education_level,
                          min_count, experience_radius)
        if no_results_key in cache:
            continue

        contracts = Contract.objects.all().multi_phrase_search(phrase)
        contracts = contracts.filter(
            min_years_experience__gte=min_years_experience - experience_radius,
            min_years_experience__lte=min_years_experience + experience_radius,
            education_level=education_level
        )

        count = contracts.count()
        if count >= min_count:
            return phrase, contracts, count
        else:
            cache[no_results_key] = True
    return None, None, None


def get_data_explorer_url(query, min_experience, max_experience, education):
    # TODO: Use url mapper to get URL for the data explorer.

    params = {
        'q': query,
        'min_experience': min_experience,
        'max_experience': max_experience,
        'education': education
    }

    return '/?{}'.format(urlencode(params))


def describe(cursor, vocab, labor_category, min_years_experience,
             education_level, price, severe_stddevs=2, experience_radius=2,
             cache=None):
    if cache is None:
        cache = {}

    result = {
        'severe': False,
        'description': ''
    }

    phrase, contracts, count = find_comparable_contracts(
        cursor,
        vocab,
        labor_category,
        min_years_experience,
        education_level,
        experience_radius=experience_radius,
        cache=cache
    )

    if contracts is not None:
        wage_field = 'current_price'
        stats = contracts.aggregate(
            avg=Avg(wage_field),
            stddev=StdDev(wage_field)
        )
        avg = stats['avg']
        stddev = stats['stddev']

        price_delta = abs(price - avg)

        if price_delta >= severe_stddevs * stddev:
            result['severe'] = True

        result['count'] = count
        result['avg'] = avg
        result['stddev'] = stddev
        result['stddevs'] = math.ceil(price_delta / stddev)
        result['preposition'] = \
            'w' + ('a' * result['stddevs']) + 'y ' + \
            ('below' if price < avg else 'above')
        result['labor_category'] = phrase
        result['url'] = get_data_explorer_url(
            phrase,
            min_years_experience - experience_radius,
            min_years_experience + experience_radius,
            education_level
        )
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

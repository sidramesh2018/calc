import csv
from collections import OrderedDict
import djclick as click
from django.db import connection

from contracts.models import Contract
from data_capture.templatetags.analyze_contract import describe, Vocabulary


def gsa_advantage_url(contract_id):
    # TODO: This is also in the front-end code for the data explorer;
    # might be nice to consolidate the template.

    contract_id = contract_id.replace('-', '')

    return ('https://www.gsaadvantage.gov/'
            'ref_text/%(id)s/%(id)s_online.htm' % {'id': contract_id})


def analyze(outfile, base_url='https://calc.gsa.gov'):
    contracts = Contract.objects.all()

    writer = None

    with connection.cursor() as cursor:
        vocab = Vocabulary.create(cursor)
        cache = {}

        total = contracts.count()

        for i, contract in enumerate(contracts):
            if int(i / 10) == float(i) / 10.0:
                print("Processed {} of {} contracts.".format(i, total))

            analysis = describe(
                cursor,
                vocab,
                contract.labor_category,
                contract.min_years_experience,
                contract.education_level,
                float(contract.current_price),
                severe_stddevs=3,
                cache=cache
            )

            if analysis['severe']:
                row = OrderedDict((
                    ('Labor category', contract.labor_category),
                    ('Minimum experience', contract.min_years_experience),
                    ('Education', contract.education_level),
                    ('Current year pricing', contract.current_price),
                    ('CALC query', analysis['labor_category']),
                    ('CALC sample size', analysis['count']),
                    ('CALC avg', analysis['avg']),
                    ('CALC stddev', analysis['stddev']),
                    ('CALC URL', base_url + analysis['url']),
                    ('GSA Advantage URL',
                     gsa_advantage_url(contract.idv_piid)),
                ))
                if writer is None:
                    writer = csv.DictWriter(outfile, fieldnames=row.keys())
                    writer.writeheader()
                writer.writerow(row)
                outfile.flush()


@click.command()
@click.argument('filename', default='contract_analysis.csv')
def command(filename):
    with open(filename, 'w') as f:
        print("Writing analysis to {}.".format(filename))
        analyze(f)
        print("Done.")

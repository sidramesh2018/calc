from django.db import connection

from contracts.models import Contract
from .base import BaseMetric


class Metric(BaseMetric):
    '''
    Measures the number of duplicate Contract entries in the database.

    By "duplicate" we mean that the entries have the same core fields
    but differ along other axes.

    This code is based on the following experimental PR:

        https://github.com/18F/calc/pull/1029
    '''

    CORE_FIELDS = [
        'vendor_name',
        'labor_category',
        'idv_piid',
        'current_price',
    ]

    CORE_FIELD_NAMES = [
        Contract._meta.get_field(field).verbose_name
        for field in CORE_FIELDS
    ]

    CONTRACTS_TABLE = Contract._meta.db_table

    CORE_FIELD_COLUMNS = [
        Contract._meta.get_field(field).column
        for field in CORE_FIELDS
    ]

    CORE_FIELDS_ARE_EQUAL = ' AND '.join([
        f"c1.{column} = c2.{column}"
        for column in CORE_FIELD_COLUMNS
    ])

    COUNT_SQL_QUERY = f'''
    SELECT COUNT(c1.id)
    FROM {CONTRACTS_TABLE} as c1, {CONTRACTS_TABLE} as c2
    WHERE c1.id < c2.id   /* Use < to avoid counting duplicates */
    AND {CORE_FIELDS_ARE_EQUAL}
    '''

    IDS_SQL_QUERY = f'''
    SELECT c1.id, c2.id
    FROM {CONTRACTS_TABLE} as c1, {CONTRACTS_TABLE} as c2
    WHERE c1.id < c2.id   /* Use < to avoid counting duplicates */
    AND {CORE_FIELDS_ARE_EQUAL}
    '''

    def get_examples_queryset(self):
        cursor = connection.cursor()
        cursor.execute(self.IDS_SQL_QUERY)
        ids = []
        for c1_id, c2_id in cursor.fetchmany(self.MAX_EXAMPLES / 2):
            ids.append(c1_id)
            ids.append(c2_id)
        return Contract.objects.filter(id__in=ids).order_by(*self.CORE_FIELDS)

    def count(self) -> int:
        cursor = connection.cursor()
        cursor.execute(self.COUNT_SQL_QUERY)
        return cursor.fetchone()[0]

    desc = f'''
    labor rates appear to be duplicates.
    '''

    footnote = f'''
    By "duplicates" we mean that they share the same values
    for {', '.join(CORE_FIELD_NAMES[:-1])} and {CORE_FIELD_NAMES[-1]}.
    They may (and likely do) vary across other fields.
    '''

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

    CONTRACTS_TABLE = Contract._meta.db_table

    CORE_FIELD_COLUMNS = [
        Contract._meta.get_field(field).column
        for field in CORE_FIELDS
    ]

    CORE_FIELDS_ARE_EQUAL = ' AND '.join([
        f"c1.{column} = c2.{column}"
        for column in CORE_FIELD_COLUMNS
    ])

    SQL_QUERY = f'''
    SELECT COUNT(c1.id)
    FROM {CONTRACTS_TABLE} as c1, {CONTRACTS_TABLE} as c2
    WHERE c1.id < c2.id   /* Use < to avoid counting duplicates */
    AND {CORE_FIELDS_ARE_EQUAL}
    '''

    def count(self) -> int:
        cursor = connection.cursor()
        cursor.execute(self.SQL_QUERY)
        return cursor.fetchone()[0]

    def describe(self, count) -> str:
        return f'''
            {count} labor rates
            share the same core fields
            ({', '.join(self.CORE_FIELDS)}) but
            differ along other axes.
        '''

from django.db import connection

from contracts.models import Contract


# If two distinct labor category rows share these fields in common
# but differ along other axes, they are considered duplicates.
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
SELECT COUNT(c1.id) / 2  /* Divide by two to avoid double-counting */
FROM {CONTRACTS_TABLE} as c1, {CONTRACTS_TABLE} as c2
WHERE c1.id != c2.id
AND {CORE_FIELDS_ARE_EQUAL}
'''


def count_duplicates() -> int:
    '''
    Count the number of duplicate Contract records in
    the database, that have the same CORE_FIELDS but
    differ along other axes.
    '''

    cursor = connection.cursor()
    cursor.execute(SQL_QUERY)
    return cursor.fetchone()[0]

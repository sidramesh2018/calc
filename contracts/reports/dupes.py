from django.db.models import Count, Sum, Q

from contracts.models import Contract
from .base import BaseMetric


# Sometimes we want to dynamically build a Q object by starting
# with a "null query" that has nothing in it, and then adding
# more Q objects via the OR operator (i.e., "|").
#
# This particular null query has the advantage that no database query
# is executed if nothing is OR'd with it. It was taken from
# https://stackoverflow.com/a/46225056.
NULL_QUERY = Q(pk__in=[])


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

    def _get_dupe_info(self):
        return Contract.objects.values(*self.CORE_FIELDS)\
            .annotate(count=Count(self.CORE_FIELDS[0]))\
            .filter(count__gt=1)\
            .distinct()

    def get_examples_queryset(self):
        total = 0
        q = NULL_QUERY

        for row in self._get_dupe_info():
            total += row['count']
            criteria = {field: row[field] for field in self.CORE_FIELDS}
            next_q = Q(**criteria)
            q = q | next_q
            if total > self.MAX_EXAMPLES:
                break

        return Contract.objects.filter(q)\
            .order_by(*self.CORE_FIELDS)[:self.MAX_EXAMPLES]

    def count(self) -> int:
        return self._get_dupe_info()\
            .aggregate(Sum('count'))['count__sum'] or 0

    desc = f'''
    labor rates appear to be duplicates.
    '''

    footnote = f'''
    By "duplicates" we mean that they share the same values
    for {', '.join(CORE_FIELD_NAMES[:-1])} and {CORE_FIELD_NAMES[-1]}.
    They may (and likely do) vary across other fields.
    '''

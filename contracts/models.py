import re

from datetime import datetime
from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from djorm_pgfulltext.models import SearchManager, SearchQuerySet
from djorm_pgfulltext.fields import VectorField

EDUCATION_CHOICES = (
    ('HS', 'High School'),
    ('AA', 'Associates'),
    ('BA', 'Bachelors'),
    ('MA', 'Masters'),
    ('PHD', 'Ph.D.'),
)

MIN_ESCALATION_RATE = 0
MAX_ESCALATION_RATE = 99
NUM_CONTRACT_YEARS = 5


def convert_to_tsquery(query):
    """
    Converts multi-word phrases into AND boolean queries for postgresql.

    Examples:

        >>> convert_to_tsquery('interpretation')
        'interpretation:*'

        >>> convert_to_tsquery('interpretation services')
        'interpretation:* & services:*'
    """

    # remove all non-alphanumeric or whitespace chars
    pattern = re.compile('[^a-zA-Z\s]')
    query = pattern.sub('', query)
    query_parts = query.split()
    # remove empty strings and add :* to use prefix matching on each chunk
    query_parts = ["%s:*" % s for s in query_parts if s]
    tsquery = ' & '.join(query_parts)

    return tsquery


def convert_to_tsquery_union(queries):
    '''
    Converts a list of multi-word phrases into OR boolean queries for
    postgresql.

    Examples:

        >>> convert_to_tsquery_union(['foo', 'bar'])
        'foo:* | bar:*'

        >>> convert_to_tsquery_union(['foo', 'bar baz'])
        'foo:* | bar:* & baz:*'

    Also, unrecognizable/garbage phrases will be removed:

        >>> convert_to_tsquery_union(['foo', '$@#%#@!', 'bar'])
        'foo:* | bar:*'
    '''

    queries = [convert_to_tsquery(query) for query in queries]
    # remove empty strings
    queries = filter(None, queries)
    return " | ".join(queries)


class CurrentContractManager(SearchManager):
    # need to subclass the SearchManager we were using for postgres full text
    # search instead of default

    def multi_phrase_search(self, *args, **kwargs):
        return self.get_queryset().multi_phrase_search(*args, **kwargs)

    def get_queryset(self):
        return ContractsQuerySet(self.model, using=self._db)\
            .filter(current_price__gt=0)\
            .exclude(current_price__isnull=True)


class ContractsQuerySet(SearchQuerySet):

    def multi_phrase_search(self, queries):
        if isinstance(queries, str):
            queries = [queries]
        return self.search(convert_to_tsquery_union(queries), raw=True)

    def order_by(self, *args, **kwargs):
        edu_sort_sql = """
            case
                when education_level = 'HS' then 1
                when education_level = 'AA' then 2
                when education_level = 'BA' then 3
                when education_level = 'MA' then 4
                when education_level = 'PHD' then 5
                else -1
            end
        """

        edu_index = None

        sort_params = list(args)

        if 'education_level' in sort_params:
            edu_index = sort_params.index('education_level')
        elif '-education_level' in sort_params:
            edu_index = sort_params.index('-education_level')

        if edu_index is not None:
            sort_params[edu_index] = 'edu_sort' if not args[
                edu_index].startswith('-') else '-edu_sort'
            queryset = super(ContractsQuerySet, self)\
                .extra(select={'edu_sort': edu_sort_sql}, order_by=sort_params)
        else:
            queryset = super(ContractsQuerySet, self)\
                .order_by(*args, **kwargs)

        return queryset


class BulkUploadContractSource(models.Model):
    '''
    Model to store provenance of bulk-uploaded contract data
    '''
    REGION_10 = 'R10'

    PROCUREMENT_CENTER_CHOICES = (
        (REGION_10, 'Region 10'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitter = models.ForeignKey(User, null=True, blank=True)
    has_been_loaded = models.BooleanField(default=False)
    original_file = models.BinaryField()
    file_mime_type = models.TextField()
    procurement_center = models.CharField(
        db_index=True, max_length=5, choices=PROCUREMENT_CENTER_CHOICES)


class Contract(models.Model):

    idv_piid = models.CharField(max_length=128)  # index this field
    piid = models.CharField(max_length=128)  # index this field
    contract_start = models.DateField(null=True, blank=True)
    contract_end = models.DateField(null=True, blank=True)
    contract_year = models.IntegerField(null=True, blank=True)
    vendor_name = models.CharField(max_length=128)
    labor_category = models.TextField(db_index=True)
    education_level = models.CharField(
        db_index=True, choices=EDUCATION_CHOICES, max_length=5, null=True,
        blank=True)
    min_years_experience = models.IntegerField(db_index=True)
    hourly_rate_year1 = models.DecimalField(max_digits=10, decimal_places=2)
    hourly_rate_year2 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    hourly_rate_year3 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    hourly_rate_year4 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    hourly_rate_year5 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    current_price = models.DecimalField(
        db_index=True, max_digits=10, decimal_places=2, null=True, blank=True)
    next_year_price = models.DecimalField(
        db_index=True, max_digits=10, decimal_places=2, null=True, blank=True)
    second_year_price = models.DecimalField(
        db_index=True, max_digits=10, decimal_places=2, null=True, blank=True)
    contractor_site = models.CharField(
        db_index=True, max_length=128, null=True, blank=True)
    schedule = models.CharField(
        db_index=True, max_length=128, null=True, blank=True)
    business_size = models.CharField(
        db_index=True, max_length=128, null=True, blank=True)
    sin = models.TextField(null=True, blank=True)

    search_index = VectorField()

    upload_source = models.ForeignKey(
        BulkUploadContractSource,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    # use a manager that filters by current contracts with a valid
    # current_price
    objects = CurrentContractManager(
        fields=('labor_category',),
        config='pg_catalog.english',
        search_field='search_index',
        auto_update_search_field=True
    )

    def get_readable_business_size(self):
        if 's' in self.business_size.lower():
            return 'small business'
        else:
            return 'other than small business'

    @staticmethod
    def get_education_code(text):
        for pair in EDUCATION_CHOICES:
            if text.strip() in pair[1]:
                return pair[0]

        return None

    @staticmethod
    def normalize_rate(rate):
        return float(rate.replace(',', '').replace('$', ''))

    def update_price_fields(self):
        '''
        Set current, next, and second year price fields based on this
        contract's contract_year.
        '''
        if self.contract_year is None:
            raise ValueError('self.contract_year must be set')

        curr_contract_year = self.contract_year

        contract_end_year = self.calculate_end_year()

        if 0 < curr_contract_year <= contract_end_year:
            self.current_price = self.get_hourly_rate(curr_contract_year)
        else:
            self.current_price = None

        if -1 < curr_contract_year < contract_end_year:
            self.next_year_price = self.get_hourly_rate(curr_contract_year + 1)
        else:
            self.next_year_price = None

        if -2 < curr_contract_year < contract_end_year - 1:
            self.second_year_price = self.get_hourly_rate(
                curr_contract_year + 2)
        else:
            self.second_year_price = None

    def escalate_hourly_rate_fields(self, base_year_rate, escalation_rate):
        if (escalation_rate < MIN_ESCALATION_RATE or
                escalation_rate > MAX_ESCALATION_RATE):
                raise ValueError(
                    'escalation_rate must be between {} and {}'.format(
                        MIN_ESCALATION_RATE, MAX_ESCALATION_RATE))

        self.hourly_rate_year1 = base_year_rate

        for i in range(2, NUM_CONTRACT_YEARS + 1):
            # use base rate by default
            next_rate = base_year_rate

            # if there is an escalation rate, increase the
            # previous year's value by the escalation rate
            if escalation_rate > 0:
                escalation_factor = Decimal(1 + escalation_rate/100)
                prev_rate = self.get_hourly_rate(i-1)
                next_rate = escalation_factor * prev_rate

            self.set_hourly_rate(i, next_rate)

    def adjust_contract_year(self, current_date=None):
        if current_date is None:
            current_date = datetime.today().date()

        if not self.contract_start:
            # TODO: What should happen in this case? Could also early return
            raise ValueError('contract_start must be defined')

        # Calculate the difference in years between the current_date and
        # the contract start date
        # (365.25 is used to account for leap years)
        curr_contract_year = int(
            (current_date - self.contract_start).days / 365.25) + 1

        self.contract_year = curr_contract_year

    def calculate_end_year(self):
        if not self.contract_start or not self.contract_end:
            raise ValueError('contract_start and contract_end must be defined')

        if self.contract_start > self.contract_end:
            raise ValueError('contract_start cannot be after contract_end')

        # Calculate the end year of the contract, with a ceiling of 5 (since
        # the hourly_rate_yearX fields only go up to 5)
        # (365.25 is used to account for leap years)
        contract_end_year = min(5, int(
            (self.contract_end - self.contract_start).days / 365.25) + 1)

        return contract_end_year

    def get_hourly_rate(self, year):
        if year < 1 or year > NUM_CONTRACT_YEARS:
            raise ValueError(
                'year must be in range 1 to {}'.format(NUM_CONTRACT_YEARS))
        return getattr(self, 'hourly_rate_year{}'.format(year))

    def set_hourly_rate(self, year, val):
        if year < 1 or year > NUM_CONTRACT_YEARS:
            raise ValueError(
                'year must be in range 1 to {}'.format(NUM_CONTRACT_YEARS))
        setattr(self, 'hourly_rate_year{}'.format(year), val)

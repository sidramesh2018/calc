import abc
from typing import Tuple, List
from django.db.models import QuerySet

from contracts.models import EDUCATION_CHOICES


QueryStringTuple = Tuple[Tuple[str, str], ...]


class ContractFinder(metaclass=abc.ABCMeta):
    '''
    Abstract base class representing a finder for contracts that match
    a certain criteria.
    '''

    @abc.abstractmethod
    def filter_queryset(self, qs: QuerySet) -> QuerySet:
        '''
        Return the given Django QuerySet with the matching criteria
        applied to it.
        '''

        raise NotImplementedError()

    @abc.abstractmethod
    def get_data_explorer_qs_params(self) -> QueryStringTuple:
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

    def __init__(self, min_years_experience: int,
                 education_level: str) -> None:
        self.min_years_experience = min_years_experience
        self.education_level = education_level


class ExactEduAndExpFinder(BaseEduAndExpFinder):
    '''
    Finds contracts that are exactly equal to a given
    education level, and around a given experience level.
    '''

    MAX_YEARS_DELTA = 4

    def filter_queryset(self, qs: QuerySet) -> QuerySet:
        return qs.filter(
            min_years_experience__gte=self.min_years_experience,
            min_years_experience__lte=(self.min_years_experience +
                                       self.MAX_YEARS_DELTA),
            education_level=self.education_level
        )

    def get_data_explorer_qs_params(self) -> QueryStringTuple:
        return (
            ('min_experience', str(self.min_years_experience)),
            ('max_experience', str(self.min_years_experience +
                                   self.MAX_YEARS_DELTA)),
            ('education', self.education_level),
        )


class GteEduAndExpFinder(BaseEduAndExpFinder):
    '''
    Finds contracts that are greater than or equal to a given
    minimum experience and education level.
    '''

    def get_valid_education_levels(self) -> List[str]:
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

    def filter_queryset(self, qs: QuerySet) -> QuerySet:
        return qs.filter(
            min_years_experience__gte=self.min_years_experience,
            education_level__in=self.get_valid_education_levels()
        )

    def get_data_explorer_qs_params(self) -> QueryStringTuple:
        return (
            ('min_experience', str(self.min_years_experience)),
            ('education', ','.join(self.get_valid_education_levels())),
        )

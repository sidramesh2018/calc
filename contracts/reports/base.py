from typing import Union
import abc

number = Union[int, float]


class BaseMetric(metaclass=abc.ABCMeta):
    '''
    An abstract base class that describes a metric that can be
    shown in a report.
    '''

    @abc.abstractmethod
    def count(self) -> number:
        '''
        Count the metric.
        '''

        raise NotImplementedError()

    @abc.abstractmethod
    def describe(self, count: number) -> str:
        '''
        Given a count, return a sentence that describes what
        it means.
        '''

        raise NotImplementedError()

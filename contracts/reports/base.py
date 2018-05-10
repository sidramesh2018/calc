from typing import Union
from textwrap import dedent, fill
import abc
from django.utils.safestring import SafeString
import markdown

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

    @abc.abstractproperty
    def desc(self) -> str:
        '''
        Return a markdown sentence that describes what the
        count means, assuming the count begins the sentence.

        For example, a value of "labor rates are weird" works
        because "53 labor rates are weird" makes sense, assuming
        that the count is 53.

        Note that this value may be converted to HTML and marked
        as safe, which means that it shouldn't contain any
        untrusted user data.
        '''

        raise NotImplementedError()

    @property
    def desc_text(self) -> str:
        return fill(dedent(self.desc)).strip()

    @property
    def desc_html(self) -> SafeString:
        html = markdown.markdown(self.desc_text)

        # Unwrap the <p></p> that markdown wraps it in.
        html = html[len('<p>'):-len('</p>')]

        return SafeString(html)

from django.template.loader import render_to_string
from django.core.validators import MinValueValidator

from contracts.loaders.region_10 import FEDERAL_MIN_CONTRACT_RATE

min_price_validator = MinValueValidator(
    FEDERAL_MIN_CONTRACT_RATE,
    message='Price must be at least the federal contractor minimum wage '
            '(${0:.2f})'.format(FEDERAL_MIN_CONTRACT_RATE))


class BasePriceList:
    '''
    Abstract base class for price lists being imported into CALC.
    '''

    # Human-readable name of the schedule to which the price list
    # belongs. Subclasses should override this.
    title = 'Unknown Schedule'

    # Path to the template used for presenting an example of
    # what to upload.
    upload_example_template = None

    # Extra instructions text to use for the upload widget.
    upload_widget_extra_instructions = None

    def __init__(self):
        # This is a list of Django Form objects representing
        # valid rows in the price list.
        self.valid_rows = []

        # This is a list of Django Form objects representing
        # invalid rows in the price list.
        self.invalid_rows = []

    def is_empty(self):
        '''
        Returns whether the price list contains no data.
        '''

        return not (self.valid_rows or self.invalid_rows)

    def add_to_price_list(self, price_list):
        '''
        Adds the price list's valid rows to the given
        data_capture.models.SubmittedPriceList model.
        '''

        raise NotImplementedError()

    def serialize(self):
        '''
        Returns a JSON-serializable representation of the
        price list.
        '''

        raise NotImplementedError()

    def to_table(self):
        '''
        Returns a string of the HTML table representation of the valid rows
        of the price list
        '''

        raise NotImplementedError()

    def to_error_table(self):
        '''
        Returns a string of the HTML table representation of the invalid
        rows of the price list
        '''

        return NotImplementedError()

    @classmethod
    def get_upload_example_context(cls):
        '''
        Returns a dictionary to use as the context for the upload example
        template.
        '''

        return None

    @classmethod
    def render_upload_example(cls, request=None):
        '''
        Returns the HTML containing an example of what the schedule
        expects the user to upload, along with any other pertinent
        information.

        If the schedule has no example, returns an empty string.
        '''

        if cls.upload_example_template is not None:
            return render_to_string(cls.upload_example_template,
                                    cls.get_upload_example_context(),
                                    request=request)
        return ''

    @classmethod
    def deserialize(cls, obj):
        '''
        Given an object previously returned by serialize(),
        Return a BasePriceList subclass.
        '''

        raise NotImplementedError()

    @classmethod
    def load_from_upload(cls, f):
        '''
        Given an UploadedFile, return a BasePriceList
        subclass that represents the price list. If the file could not
        be read, raise a ValidationError.

        For more details on UploadedFile, see:

            https://docs.djangoproject.com/en/1.9/ref/files/uploads/
        '''

        raise NotImplementedError()

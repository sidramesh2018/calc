class BasePriceList:
    '''
    Abstract base class for price lists being imported into CALC.
    '''

    # Human-readable name of the schedule to which the price list
    # belongs. Subclasses should override this.
    title = 'Unknown Schedule'

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

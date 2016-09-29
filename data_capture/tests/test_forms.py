from django.test import TestCase, override_settings

from .common import FAKE_SCHEDULE, uploaded_csv_file, r10_file
from ..schedules.fake_schedule import FakeSchedulePriceList
from ..schedules import registry
from ..forms import Step2Form, Step3Form, Region10BulkUploadForm


class Step2FormTests(TestCase):
    def test_clean_escalation_rate_works(self):
        form = Step2Form({'escalation_rate': None})
        form.is_valid()
        self.assertEqual(form.cleaned_data['escalation_rate'], 0)

        form = Step2Form({'escalation_rate': 2.5})
        form.is_valid()
        self.assertEqual(form.cleaned_data['escalation_rate'], 2.5)


@override_settings(DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE])
class Step3FormTests(TestCase):
    def setUp(self):
        registry._init()

    def test_invalid_when_file_is_missing(self):
        form = Step3Form({}, schedule=FAKE_SCHEDULE)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['file'][0], 'This field is required.')

    def test_invalid_when_file_cannot_be_gleaned(self):
        form = Step3Form({}, {
            'file': uploaded_csv_file(b'i cannot be gleaned')
        }, schedule=FAKE_SCHEDULE)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            '__all__': [
                "The file you uploaded doesn't have any data we can "
                "glean from it."
            ]
        })

    def test_clean_sets_gleaned_data(self):
        form = Step3Form({}, {
            'file': uploaded_csv_file()
        }, schedule=FAKE_SCHEDULE)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['gleaned_data'].title,
                         FakeSchedulePriceList.title)


class Region10BulkUploadFormTests(TestCase):
    def test_invalid_when_file_is_missing(self):
        form = Region10BulkUploadForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['file'][0], 'This field is required.')

    def test_invalid_when_file_is_invalid(self):
        form = Region10BulkUploadForm({}, {'file': r10_file(b'whatever')})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            '__all__': [
                "That file does not appear to be a "
                "valid Region 10 export. Try another?"
            ]
        })

    def test_valid_when_file_is_valid(self):
        form = Region10BulkUploadForm({}, {'file': r10_file()})
        self.assertTrue(form.is_valid())

from django.test import SimpleTestCase
from rest_framework.serializers import ValidationError

from api.serializers import EducationLevelField


class EducationLevelFieldTests(SimpleTestCase):
    def test_returns_edu_code(self):
        self.assertEqual(
            EducationLevelField().to_internal_value('Bachelors'),
            'BA'
        )

    def test_raises_validation_error(self):
        f = EducationLevelField()
        msg = 'Invalid education level: lol'
        with self.assertRaisesRegex(ValidationError, msg):
            f.to_internal_value('lol')

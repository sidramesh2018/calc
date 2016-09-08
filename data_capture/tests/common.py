import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.contrib.auth.models import User, Group

from contracts.models import BulkUploadContractSource


def path(*paths):
    root_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(root_dir, *paths)


FAKE_SCHEDULE = 'data_capture.schedules.fake_schedule.FakeSchedulePriceList'

FAKE_SCHEDULE_EXAMPLE_PATH = path(
    'static', 'data_capture', 'fake_schedule_example.csv'
)

R10_XLSX_PATH = path('static', 'data_capture', 'r10_export_sample.xlsx')

XLSX_CONTENT_TYPE = ('application/vnd.openxmlformats-'
                     'officedocument.spreadsheetml.sheet')


def create_bulk_upload_contract_source(user):
    if isinstance(user, str):
        user = User.objects.create_user('testuser', email=user)
    with open(R10_XLSX_PATH, 'rb') as f:
        src = BulkUploadContractSource.objects.create(
            submitter=user,
            has_been_loaded=False,
            original_file=f.read(),
            file_mime_type=XLSX_CONTENT_TYPE,
            procurement_center=BulkUploadContractSource.REGION_10,
        )
    return src


def uploaded_csv_file(content=None):
    if content is None:
        with open(FAKE_SCHEDULE_EXAMPLE_PATH, 'rb') as f:
            content = f.read()

    return SimpleUploadedFile(
        'foo.csv',
        content,
        content_type='text/csv'
    )


def r10_file(content=None, name='r10.xlsx'):
    if content is None:
        with open(R10_XLSX_PATH, 'rb') as f:
            content = f.read()

    if type(content) is str:
        content = bytes(content, 'UTF-8')

    return SimpleUploadedFile(name, content,
                              content_type=XLSX_CONTENT_TYPE)


@override_settings(
    # This will make tests run faster.
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
    # Ignore our custom auth backend so we can log the user in via
    # Django 1.8's login helpers.
    AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'],
)
class BaseTestCase(TestCase):
    def create_user(self, username, password=None, is_staff=False,
                    is_superuser=False, email=None, groups=()):
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        for groupname in groups:
            g = Group.objects.get(name=groupname)
            g.user_set.add(user)
            g.save()
        if is_staff:
            user.is_staff = True
            user.save()
        if is_superuser:
            user.is_staff = True
            user.is_superuser = True
            user.save()
        return user

    def login(self, username='foo', is_staff=False, is_superuser=False,
              groups=()):
        user = self.create_user(username=username, password='bar',
                                is_staff=is_staff,
                                is_superuser=is_superuser,
                                groups=groups)
        assert self.client.login(username=username, password='bar')
        return user


@override_settings(
    DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE],
)
class StepTestCase(BaseTestCase):
    def assertRedirectsToLogin(self, url):
        res = self.client.get(url)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(
            res['Location'],
            'http://testserver/auth/login?next=%s' % url
        )

    def assertHasMessage(self, res, tag, content):
        msgs = list(res.context['messages'])
        self.assertEqual(len(msgs), 1)
        m = msgs[0]
        self.assertEqual(m.tags, tag)
        self.assertEqual(str(m), content)

import os
from django.core.files.uploadedfile import SimpleUploadedFile


def path(*paths):
    root_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(root_dir, *paths)


FAKE_SCHEDULE = 'data_capture.schedules.fake_schedule.FakeSchedulePriceList'


FAKE_SCHEDULE_EXAMPLE_PATH = path(
    'static', 'data_capture', 'fake_schedule_example.csv'
)


def uploaded_csv_file(content=None):
    if content is None:
        with open(FAKE_SCHEDULE_EXAMPLE_PATH, 'rb') as f:
            content = f.read()

    return SimpleUploadedFile(
        'foo.csv',
        content,
        content_type='text/csv'
    )

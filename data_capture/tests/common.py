import os


def path(*paths):
    root_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(root_dir, *paths)


FAKE_SCHEDULE = 'data_capture.schedules.fake_schedule.FakeSchedulePriceList'


FAKE_SCHEDULE_EXAMPLE_PATH = path(
    'static', 'data_capture', 'fake_schedule_example.csv'
)

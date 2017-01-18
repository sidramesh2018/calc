from debug_toolbar.panels import Panel

from .apps import DataCaptureSchedulerApp


class DocsPanel(Panel):
    '''
    A Django Debug Toolbar panel that links to various
    documentation artifacts for developers.
    '''

    title = 'Documentation'

    template = 'data_capture/panels/docs.html'

    nav_subtitle = 'Read me first!'


class ScheduledJobsPanel(Panel):
    '''
    A Django Debug Toolbar panel that displays information about
    scheduled jobs.
    '''

    title = 'Scheduled Jobs'

    template = 'data_capture/panels/jobs.html'

    def generate_stats(self, request, response):
        scheduler = DataCaptureSchedulerApp.get_scheduler()

        self.record_stats({
            'scheduled_jobs': scheduler.get_jobs(with_times=True)
        })

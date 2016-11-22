import abc


class AbstractBrowserForm(abc.ABC):
    @staticmethod
    def get_id_for_radio(name, number):
        return 'id_{}_{}'.format(name, number)

    def set_date(self, name, month, day, year):
        self.set_text('%s_0' % name, str(year))
        self.set_text('%s_1' % name, str(month))
        self.set_text('%s_2' % name, str(day))

    @abc.abstractmethod
    def set_text(self, name, value):
        raise NotImplementedError()

    @abc.abstractmethod
    def set_radio(self, name, number):
        raise NotImplementedError()

    @abc.abstractmethod
    def set_file(self, name, path):
        raise NotImplementedError()

    @abc.abstractmethod
    def submit(self):
        raise NotImplementedError()


class AbstractBrowser(abc.ABC):
    @abc.abstractmethod
    def load(self, url):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_title(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_form(self, selector):
        raise NotImplementedError()

class AbstractBrowserForm:
    @staticmethod
    def get_id_for_radio(name, number):
        return 'id_{}_{}'.format(name, number)

    def set_date(self, name, month, day, year):
        self.set_text('%s_0' % name, str(year))
        self.set_text('%s_1' % name, str(month))
        self.set_text('%s_2' % name, str(day))

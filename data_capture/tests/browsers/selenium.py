from frontend.tests.test_selenium import SeleniumTestCase as _SeleniumTestCase

from . import base


class SeleniumForm(base.AbstractBrowserForm):
    def __init__(self, driver, selector):
        self.driver = driver
        self.form = driver.find_element_by_css_selector(selector)

    def set_text(self, name, value):
        self.form.find_element_by_name(name).send_keys(value)

    def set_radio(self, name, number):
        self.form.find_element_by_css_selector(
            '[for="{}"]'.format(self.get_id_for_radio(name, number))
        ).click()

    def set_file(self, name, path):
        self.form.find_element_by_name(name).send_keys(path)

    def submit(self):
        self.form.submit()


class SeleniumTestCase(_SeleniumTestCase, base.AbstractBrowser):
    def load(self, url):
        return super().load(url)

    def get_title(self):
        return self.driver.title

    def get_form(self, selector):
        return SeleniumForm(self.driver, selector)

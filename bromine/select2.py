class Select2Mixin:
    def select2(self, elem):
        return Select2(self, elem)


class Select2:
    """A wrapper for an element containing a select2 object.
    """

    def __init__(self, browser, elem):
        self.browser = browser
        self.elem = elem

    @property
    def text(self):
        return self.elem(".select2-selection").text

    @property
    def rendered(self):
        return self.elem(".select2-selection__rendered")

    def click(self):
        self.elem(".select2-selection").click()
        self.browser(".select2-results .loading-results").wait("not present")
        return self

    def send_keys(self, keys):
        self.browser("input.select2-search__field").send_keys(keys)
        return self

    def select(self, text):
        self.browser(
            xpath="//li[text()=%s]" % self.browser._quote_xpath(text)
        ).click()
        return self

    @property
    def options(self):
        return Select2Options(self)

    def wait_option(self, text, condition="present"):
        self.browser(
            xpath="//li[text()=]" % self.browser._quote_xpath(text)
        ).wait(condition)
        return self


class Select2Options:
    def __init__(self, s2):
        self.s2 = s2

    def __len__(self):
        return len(self.s2.browser.find(".select2-results__option"))

    def __iter__(self):
        return iter(self.s2.browser.find(".select2-results__option"))

    def __call__(self, text):
        return self.s2.browser(
            xpath="//li[text()=%s]" % self.s2.browser._quote_xpath(text)
        )

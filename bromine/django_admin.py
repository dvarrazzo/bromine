class DjangoAdminMixin:
    """A mixin to add django-admin utilities to a browser.
    """

    def click_save(self):
        return self(xpath="//input[@name='_save']").click()

    def click_save_cont(self):
        return self(xpath="//input[@name='_continue']").click()

    def click_save_add(self):
        return self(xpath="//input[@name='_addanother']").click()

    def click_input(self, value):
        return self(
            xpath="//input[@value=%s]" % self._quote_xpath(value)
        ).click()

    @property
    def success_msgs(self):
        self(id="content").wait()
        return self.find("ul.messagelist li.success")

    @property
    def warning_msgs(self):
        self(id="content").wait()
        return self.find("ul.messagelist li.warning")

    @property
    def fields(self):
        return DjangoAdminFields(self)

    @property
    def widgets(self):
        return DjangoAdminWidgets(self)

    def get_object_path(self, obj):
        return "/%s/%s/%s" % (
            obj._meta.app_label,
            obj._meta.model_name,
            obj.pk,
        )


class DjangoAdminFields:
    def __init__(self, browser):
        self.browser = browser

    def __getitem__(self, name):
        try:
            elem = self.browser("div.field-%s" % name).wait("present")
        except self.browser.exceptions.NoSuchElementException:
            raise KeyError("field not found: %s" % name)

        return FieldWrapper(elem)


class DjangoAdminWidgets:
    def __init__(self, browser):
        self.browser = browser

    def __getitem__(self, name):
        try:
            return self.browser(id="id_" + name).wait("present")
        except self.browser.exceptions.NoSuchElementException:
            raise KeyError("widget not found: %s" % name)


class FieldWrapper:
    def __init__(self, elem):
        self.elem = elem

    def __getattr__(self, attr):
        return getattr(self.elem, attr)

    def __call__(self, *args, **kwargs):
        return self.elem(*args, **kwargs)

    @property
    def errors(self):
        return self.elem.find("ul.errorlist li")

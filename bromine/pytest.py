"""A fixture to use selenium with py.test

Note: not using the pytest-selenium package because it doesn't play nice
with virtual displays.
"""

import re
import os
import shlex
from typing import List, Optional, Sequence
from importlib import import_module
from contextlib import contextmanager

import pytest
from selenium import webdriver
from selenium.webdriver.remote.remote_connection import RemoteConnection

# set a global timeout for selenium request: sometimes we get random errors
# creating a new session, with a java traceback, and it takes several minutes
RemoteConnection.set_timeout(20)


def pytest_addoption(parser):
    group = parser.getgroup("bromine", "Bromine integration with Selenium")

    group.addoption(
        "--selenium-hub",
        help="run web tests using this hub, e.g. 'http://localhost:4444/wd/hub';"
        " if omitted, run tests locally",
    )

    group.addoption(
        "--screenshots-dir",
        help="if specified save screenshots of failing tests there",
    )

    group.addoption(
        "--selenium-driver",
        default="Chrome",
        help="what selenium driver to use? [default: %(default)s]",
    )

    group.addoption(
        "--selenium-driver-args",
        help="arguments to pass to the selenium driver",
        default="--window-size=1280,1024",
    )


@pytest.fixture(scope="session")
def browser_factory(request):
    selenium_hub = request.config.getoption("--selenium-hub")
    return BrowserFactory(selenium_hub=selenium_hub, request=request)


@pytest.fixture(scope="function")
def browser(browser_factory, request, options):
    """Return a selenium driver to browse for testing"""
    with browser_factory.browser(options) as browser:
        yield browser


class BrowserFactory:
    def __init__(self, selenium_hub: Optional[str] = None, request=None):
        self.selenium_hub = selenium_hub
        self._request = request

    @contextmanager
    def browser(self, options):
        from . import browser

        if self.selenium_hub:
            gen = self._yield_remote_browser(options)
        else:
            gen = self._yield_local_browser(options)

        self._setup_screenshot_dir()

        for b in gen:
            browser.on_pytest += 1
            if self._request:
                self._request.node._browser = b

            yield b

            browser.on_pytest -= 1

    def _yield_local_browser(self, options):
        from . import browser

        cls = browser_class_from_options(options)
        drv = cls(options=options)
        b = browser.Browser(drv)
        try:
            yield b
        finally:
            b.quit()

    def _yield_remote_browser(self, options):
        from . import browser

        assert self.selenium_hub

        # Sometimes we get an error with this request: try a few times
        r = None
        exc = None
        for i in range(3):
            try:
                r = webdriver.Remote(
                    RemoteConnection(self.selenium_hub),
                    options=options,
                )
                break
            except Exception as e:
                exc = e

        if r is None:
            pytest.fail("error opening remote browser: %s" % exc)

        b = browser.Browser(r)
        try:
            yield b
        finally:
            b.quit()

    def _setup_screenshot_dir(self):
        if not self._request:
            return

        ssdir = self._request.config.getoption("--screenshots-dir")
        if ssdir:
            self._request.node._screenshots_dir = ssdir


@pytest.fixture(scope="session")
def options_factory(request):
    driver = request.config.getoption("--selenium-driver")
    args_in = request.config.getoption("--selenium-driver-args")
    args = shlex.split(args_in) if args_in else []
    return OptionFactory(driver=driver, args=args)


@pytest.fixture(scope="session")
def options(options_factory):
    return options_factory.options()


class OptionFactory:
    def __init__(self, driver: str, args: Sequence[str] = ()):
        self.driver = driver
        self.args = list(args)

    def options(self, driver: Optional[str] = None, args: Optional[List[str]] = None):
        if not driver:
            driver = self.driver
        driver = driver.lower()
        if not args:
            args = self.args

        optmodule = "selenium.webdriver.%s.options" % driver.lower()
        try:
            optmodule = import_module(optmodule)
        except ImportError:
            raise pytest.fail("unknown selenium driver: %s" % driver)

        opt = optmodule.Options()
        for arg in args:
            opt.add_argument(arg)

        return opt


def browser_class_from_options(options):
    module = type(options).__module__
    package = module.rsplit(".", 1)[0]
    assert package.startswith("selenium.webdriver.")

    drvmodule = f"{package}.webdriver"
    try:
        drvmodule = import_module(drvmodule)
    except ImportError:
        raise pytest.fail(f"unknown selenium driver package: {package!r}")

    return drvmodule.WebDriver


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    out = yield

    ssdir = getattr(item, "_screenshots_dir", None)
    b = getattr(item, "_browser", None)

    if ssdir is None or b is None:
        return

    from selenium.common.exceptions import WebDriverException

    try:
        out.get_result()
    except (AssertionError, WebDriverException):
        if not os.path.exists(ssdir):
            os.makedirs(ssdir)
        fn = os.path.join(ssdir, "%s.screenshot.png" % sanitize(item._nodeid))
        item._screenshot = (fn, b.save_screenshot(fn))
        raise


def sanitize(s):
    """Clear tricky chars for a file from a string"""
    return re.sub(r"[^-.a-zA-Z0-9:]", "_", s)


# Should be used for reporting, but currently not working
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    if hasattr(item, "_screenshot"):
        report = outcome.get_result()
        report._screenshot = item._screenshot


# TODO: not working (creates multiple lines...)
# def pytest_report_teststatus(report):
#   if hasattr(report, '_screenshot'):
#       return report.outcome, "f", report._screenshot[0]

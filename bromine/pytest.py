"""A fixture to use selenium with py.test

Note: not using the pytest-selenium package because it doesn't play nice
with virtual displays.
"""

import re
import os
import pytest
from importlib import import_module

# set a global timeout for selenium request: sometimes we get random errors
# creating a new session, with a java traceback, and it takes several minutes
from selenium.webdriver.remote.remote_connection import RemoteConnection

RemoteConnection.set_timeout(20)


def pytest_addoption(parser):
    parser.addoption(
        "--selenium-hub",
        help="run web tests using this hub, e.g. 'http://localhost:4444/wd/hub'",
    )

    parser.addoption(
        "--screenshots-dir",
        help="if specified save screenshots of failing tests there",
    )

    parser.addoption(
        "--selenium-driver",
        default="Chrome",
        help="what selenium driver to use? [default: %(default)s]",
    )


@pytest.fixture(scope="function")
def browser(request):
    """Return a selenium driver to browse for testing
    """
    try:
        from selenium import webdriver
    except ImportError:
        pytest.skip("selenium not available")

    from . import browser

    remote_url = request.config.getoption("--selenium-hub")
    if not remote_url:
        raise pytest.skip(
            "no hub specified to run the tests (use --selenium-hub)"
        )

    ssdir = request.config.getoption("--screenshots-dir")
    if ssdir:
        request.node._screenshots_dir = ssdir

    driver_name = request.config.getoption("--selenium-driver")
    optmodule = "selenium.webdriver.%s.options" % driver_name.lower()
    try:
        optmodule = import_module(optmodule)
    except ImportError:
        raise pytest.fail("unknown selenium driver: %s" % driver_name)

    opt = optmodule.Options()
    # TODO: only tested with Chrome
    opt.add_argument("--window-size=1280,1024")

    # Sometimes we get an error with this request: try a few times
    r = None
    exc = None
    for i in range(3):
        try:
            r = webdriver.Remote(
                RemoteConnection(remote_url, resolve_ip=False), options=opt
            )
            break
        except Exception as e:
            exc = e

    if r is None:
        pytest.fail("error opening remote browser: %s" % exc)

    browser.on_pytest += 1
    b = browser.Browser(r)
    request.node._browser = b

    yield b

    browser.on_pytest -= 1
    b.quit()


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

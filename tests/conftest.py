import os
from importlib import import_module

import pytest
import selenium.webdriver
from selenium.webdriver.remote.remote_connection import RemoteConnection

import bromine


def pytest_addoption(parser):
    parser.addoption(
        "--driver",
        help="The browser to run tests with. default: %(default)s",
        default="Chrome",
    )
    parser.addoption(
        "--hub", help="Remote hub url to connect to. [default: local browser]"
    )


@pytest.fixture
def driver(request):
    driver = make_driver(request)
    yield driver
    driver.quit()


@pytest.fixture(scope="session")
def session_driver(request):
    driver = make_driver(request)
    yield driver
    driver.quit()


def make_driver(request):
    """Return a selenium driver according to the test configuration"""
    driver_name = request.config.getoption("--driver")
    opt_module = "selenium.webdriver.%s.options" % driver_name.lower()
    try:
        opt_module = import_module(opt_module)
    except ImportError as e:
        pytest.fail("couldn't import options: %s" % e)

    options = opt_module.Options()

    hub = request.config.getoption("--hub")
    if hub:
        from selenium.webdriver.remote.webdriver import WebDriver

        driver = WebDriver(
            RemoteConnection(hub, resolve_ip=False), options=options
        )
    else:
        wd_module = "selenium.webdriver.%s.webdriver" % driver_name.lower()
        wd_module = import_module(wd_module)
        driver = wd_module.WebDriver(options=options)

    return driver


@pytest.fixture(scope='session')
def pages(session_driver):
    """Return the url of a page from the test files"""

    def pages_(*path):
        if type(session_driver) is selenium.webdriver.Remote:
            path = os.path.join("/pages", *path)
        else:
            path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "pages", *path)
            )
        return "file://" + path

    return pages_


@pytest.fixture
def jsexec(driver, pages):
    """Execute some javascript in a browser page"""

    def jsexec_(jscode):
        b = bromine.Browser(driver)

        url = pages("jsexec.html")
        if b.current_url != url:
            b.get(url)

        b("textarea").clear().send_keys(jscode)
        b("#execute").click()

    return jsexec_

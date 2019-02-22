import pytest
import bromine


def test_elem_css_selector(driver, pages):
    b = bromine.Browser(driver)
    b.get(pages("sample-page.html"))
    assert b.elem(css="p.greet").text == "Goodbye!"
    assert b.elem("p.greet").text == "Goodbye!"
    assert b(css="p.greet").text == "Goodbye!"
    assert b("p.greet").text == "Goodbye!"
    with pytest.raises(b.exceptions.WebDriverException):
        b("p.nosuchclass").text


def test_elem_id_selector(driver, pages):
    b = bromine.Browser(driver)
    b.get(pages("sample-page.html"))
    assert b.elem(id="the_page").text == "page"
    assert b(id="the_page").text == "page"
    with pytest.raises(b.exceptions.WebDriverException):
        b(id="nosuchelement").text


def test_elem_xpath_selector(driver, pages):
    b = bromine.Browser(driver)
    b.get(pages("sample-page.html"))
    assert b.elem(xpath="//h1").text == "Hello page!"
    assert b(xpath="//h1").text == "Hello page!"
    with pytest.raises(b.exceptions.WebDriverException):
        b(id="//h7").text


def test_find_css(driver, pages):
    b = bromine.Browser(driver)
    b.get(pages("sample-page.html"))
    ps = b.find("p")
    assert len(ps) >= 2
    assert ps[0].text.startswith("This is a test page")
    assert ps[-1].text == "Goodbye!"


def test_wait(driver, jsexec):
    b = bromine.Browser(driver)
    jsexec(
        """
        setTimeout(function() {
          $('body').append("<div class='late'>Sorry I'm late</div>")
        }, 1000);
        """
    )
    b(".late").wait().text == "Sorry I'm late"


def test_wait_too_much(driver, jsexec):
    b = bromine.Browser(driver)
    jsexec(
        """
        setTimeout(function() {
          $('body').append("<div class='late'>Sorry I'm late</div>")
        }, 3000);
        """
    )
    with pytest.raises(b.exceptions.TimeoutException):
        b(".late").wait().text


def test_click_implicit_wait(driver, jsexec):
    b = bromine.Browser(driver)
    assert b.title != "Hello page!"
    jsexec(
        """
        $('body').append(
            "<a id='clickme' href='sample-page.html' style='display:none'>"
            + "Click me</a>");
        """
    )

    with pytest.raises(b.exceptions.TimeoutException):
        b("#clickme").click()

    jsexec(
        """
        setTimeout(function() {
          $('#clickme').show()
        }, 1000);
        """
    )
    b("#clickme").click()
    assert b.title == "Hello page!"

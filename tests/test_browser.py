import pytest
import bromine


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
            "<a id='clickme' href='elem.html' style='display:none'>"
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

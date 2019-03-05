import pytest
import bromine


def test_wait(driver, pages):
    b = bromine.Browser(driver)
    b.get(pages("jsexec.html"))
    b.execute_script(
        """
        setTimeout(function() {
            document.getElementById('content').innerHTML =
                "<div class='late'>Sorry I'm late</div>";
        }, 1000);
        """
    )
    b(".late").wait().text == "Sorry I'm late"


def test_wait_too_much(driver, pages):
    b = bromine.Browser(driver)
    b.get(pages("jsexec.html"))
    b.execute_script(
        """
        setTimeout(function() {
            document.getElementById('content').innerHTML =
                "<div class='late'>Sorry I'm late</div>";
        }, 3000);
        """
    )
    with pytest.raises(b.exceptions.TimeoutException):
        b(".late").wait().text


def test_click_implicit_wait(driver, pages):
    b = bromine.Browser(driver)
    b.get(pages("jsexec.html"))
    assert b.title != "Hello page!"
    b.execute_script(
        """
        document.getElementById('content').innerHTML =
            "<a id='clickme' href='elem.html' style='display:none'>"
            + "Click me</a>";
        """
    )

    with pytest.raises(b.exceptions.TimeoutException):
        b("#clickme").click()

    b.execute_script(
        """
        setTimeout(function() {
            document.getElementById('clickme').style.display = ''
        }, 1000);
        """
    )
    b("#clickme").click()
    assert b.title == "Hello page!"

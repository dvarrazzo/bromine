import pytest
import bromine


@pytest.fixture(scope='function')
def page(session_driver, pages):
    b = bromine.Browser(session_driver)
    url = pages("elem.html")
    if b.current_url != url:
        b.get(url)

    return b


def test_elem_css_selector(page):
    assert page.elem(css="p.greet").text == "Goodbye!"
    assert page.elem("p.greet").text == "Goodbye!"
    assert page(css="p.greet").text == "Goodbye!"
    assert page("p.greet").text == "Goodbye!"
    with pytest.raises(page.exceptions.WebDriverException):
        page("p.nosuchclass").text


def test_elem_id_selector(page):
    assert page.elem(id="the_page").text == "page"
    assert page(id="the_page").text == "page"
    with pytest.raises(page.exceptions.WebDriverException):
        page(id="nosuchelement").text


def test_elem_xpath_selector(page):
    assert page.elem(xpath="//h1").text == "Hello page!"
    assert page(xpath="//h1").text == "Hello page!"
    with pytest.raises(page.exceptions.WebDriverException):
        page(id="//h7").text


def test_find_css(page):
    ps = page.find("p")
    assert len(ps) >= 2
    assert ps[0].text.startswith("This is a test page")
    assert ps[-1].text == "Goodbye!"


@pytest.mark.parametrize(
    "idx, string",
    enumerate(
        """
Single'quote
'Single quote start
Single quote end'
Double"quote
"Double quote start
Double quote end"
'A"bit'of""\"a'mix"
"A'bit"of''\'a"mix'
""".strip().splitlines()
    ),
)
def test_elem_text_selector(idx, string, page):
    elem = page(text=string)
    assert elem.get_attribute("data-idx") == str(idx)

    elem = page.elem(text=string)
    assert elem.get_attribute("data-idx") == str(idx)

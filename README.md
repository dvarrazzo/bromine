# Bromine: pythonic web testing

Bromine is a wrapper around [selenium] to allow writing testing in a terse and
*pythonic* rather that *java-esque* way.

[selenium]: https://www.seleniumhq.org/

Selenium is cool: you register browser to a hub, you ask browsers from a hub,
you use the browser, and you put it back. It works like magic.

Except if you want to use https. But who needs https these days?

Anyway, enough dissing well intentioned web testing systems. Let's talk bad
about bad testing system. You know what you have to do to wait for a page to
load after a get, and then check if an element is visible? The selenium docs
[will tell you](https://selenium-python.readthedocs.io/waits.html#explicit-waits):

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ...
driver.get("http://example.com")
element = WebDriverWait(driver, 10).until(
	EC.presence_of_element_located((By.ID, "myDynamicElement"))
)
```

I've been kind and I've stripped some boilerplate. If you are happy about
importing three objects from 4 levels of namespaces and create a wait object
and pass a 2-element tuple to the "convenience method"
`selenium.webdriver.support.expected_conditions.visibility_of_element_located`
for a thing you have to do pretty much every time you click on a link, please
stop reading here: type `pip install selenium` and off you go. The following
paragraph is only for people who think the above is unsatisfactory in Python.

Still reading? Sure?

Well, I'll be honest: what I prefer to do is:

```python
import bromine
browser = bromine.Browser(driver)
element = browser.get("http://example.com/").wait(id='myDynamicElement')
```

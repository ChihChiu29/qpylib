"""Easier and improved WebDriver APIs.

ONLY opens one WebDriverManager at a time; using multiple instances will have
cause interference.
"""

import subprocess
import time

import retrying
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from qpylib import t

_KILLING_NUM_RETRIES = 5
_GET_URL_NUM_RETRIES = 3
_SLEEP_BETWEEN_RETRIES = 0.5
_ALLOW_KILL_CHROME = True
_DEFAULT_WAIT_SEC = 30


def _RetryOnException(exception: Exception) -> bool:
  return isinstance(exception, WebDriverException)


class WebDriverManager(object):
  """Manage Chrome WebDriver so actions can be retried."""

  def __init__(self, headless: bool = False):
    self._driver = None
    self._headless = headless

  @retrying.retry(
    retry_on_exception=_RetryOnException,
    stop_max_attempt_number=_GET_URL_NUM_RETRIES,
    wait_fixed=_SLEEP_BETWEEN_RETRIES,
  )
  def Do(
      self,
      action_fn: t.Callable[[WebDriver], t.T],
      close_upon_completion: bool = False,
  ) -> t.T:
    """Performs actions using provided WebDriver.

    Wrap actions you want to perform into action_fn, and make sure these actions
    start with one that sets the state (e.g. load an url). When there is a crash
    which makes any of the actions to fail, a new chromedriver will be created
    and action_fn will be retried. Do *NOT* assume any state from previous
    calls of this function, always assume you might start with
    a new browser.

    If chromedriver does not crash, the save driver is reused cross multiple
    calls of this function. If you do want to start with a new chromedriver
    (which starts a new chrome window with new session), use the Quit function
    to close the existing chromedriver.
    """
    driver = self._GetOrCreateDriver()
    try:
      result = action_fn(driver)
      if close_upon_completion:
        self.Quit()
      return result
    except Exception as e:
      _KillBrowsersAndDrivers()
      self._driver = None
      raise e

  def Quit(self):
    """Quits the created WebDriver."""
    try:
      self._driver.quit()
    except Exception:
      pass
    self._driver = None

  def _GetOrCreateDriver(self):
    if not self._driver:
      self._driver = CreateWebDriver(headless=self._headless)
    return self._driver


def _KillBrowsersAndDrivers():
  if not _ALLOW_KILL_CHROME:
    return
  # It's best effort killing, since defunct chromedriver attached to the current
  # process won't die until the program quits.
  for _ in range(_KILLING_NUM_RETRIES + 1):
    existing_process = subprocess.check_output(
      'echo $(ps -e | grep chrome)', shell=True)
    if existing_process == '\n':
      return
    subprocess.call(['killall', '-KILL', '-r', 'chrome'])
    time.sleep(_SLEEP_BETWEEN_RETRIES)


def CreateWebDriver(
    headless: bool = True,
    use_firefox: bool = True) -> WebDriver:
  if use_firefox:
    options = webdriver.FirefoxOptions()
    if headless:
      options.add_argument('-headless')
    return webdriver.Firefox(firefox_options=options)
  else:
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.binary_location = '/usr/bin/chromium-browser'
    if headless:
      options.add_argument('--headless')
    return webdriver.Chrome(chrome_options=options)


def FindElementsWithCssWithWait(
    driver: WebDriver,
    css: t.Text,
    wait_sec: int = _DEFAULT_WAIT_SEC,
) -> t.List[WebElement]:
  """Returns all elements matching the given css, wait if not present."""
  WebDriverWait(driver, wait_sec).until(
    expected_conditions.presence_of_element_located(
      (By.CSS_SELECTOR, css))
  )
  return driver.find_elements_by_css_selector(css)

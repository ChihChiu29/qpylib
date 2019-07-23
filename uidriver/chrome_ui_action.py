"""UI Actions for chrome_driver.py."""
import json

from PIL import Image

from qpylib import t, image
from qpylib.date_n_time import timing
from qpylib.uidriver import chrome_driver


def UiWait():
  """Creates a Wait object suitable for UI Actions."""
  return timing.Wait(
    num_of_retries=5,
    wait_between_retries_sec=4)


def GoToUrl(
    comm: chrome_driver.ChromeCommunicator,
    url: t.Text,
) -> None:
  """Goes to a URL.

  The page content before and after the change are compared to make sure
  the change indeed happens.
  """
  get_body_text_js = 'document.body.innerText;'
  before_text = comm.RunJs_GetValue(get_body_text_js)
  comm.RunJs_GetValue('window.location="%s"' % url)

  UiWait().UntilValue(
    lambda x: x != before_text, comm.RunJs_GetValue, get_body_text_js)


def GetWindowScrollValues(
    comm: chrome_driver.ChromeCommunicator,
) -> t.JSON:
  """Gets window scroll values."""
  result = json.loads(comm.RunJs_GetValue(
    'JSON.stringify({"x": window.scrollX, "y": window.scrollY});'))
  return {
    'x': float(result['x']),
    'y': float(result['y']),
  }


def GetElementText(
    comm: chrome_driver.ChromeCommunicator,
    css_selector: t.Text,
) -> t.Text:
  """Gets innerText of an element of the given css selector.

  Waits for the element to be visible first.
  """
  return UiWait().UntilNoException(
    chrome_driver.ChromeCommunicatorCommandJsError,
    comm.RunJs_GetValue,
    'document.querySelector("%s").innerText;' % css_selector)


def GetElementRect(
    comm: chrome_driver.ChromeCommunicator,
    css_selector: t.Text,
) -> t.JSON:
  """Gets bounding rect for an element."""
  result = json.loads(comm.RunJs_GetValue(
    'JSON.stringify(document.querySelector("%s").getBoundingClientRect());' %
    css_selector))
  return {
    'x': float(result['x']),
    'y': float(result['y']),
    'width': float(result['width']),
    'height': float(result['height']),
  }


def TakeScreenshot(
    comm: chrome_driver.ChromeCommunicator,
    css_selector: t.Optional[t.Text],
) -> Image:
  """Takes a screenshot for an element or the whole viewport."""
  cmd = {
    'method': 'Page.captureScreenshot',
    'params': {
      'format': 'png',
    }
  }
  if css_selector:
    rect = GetElementRect(comm, css_selector)
    scroll = GetWindowScrollValues(comm)
    cmd.get('params')['clip'] = {
      'x': rect['x'] + scroll['x'],
      'y': rect['y'] + scroll['y'],
      'width': rect['width'],
      'height': rect['height'],
      'scale': 1.0,
    }
  result = comm.RunCommand(cmd)
  return image.EncodedPNGToImage(result['result']['data'])

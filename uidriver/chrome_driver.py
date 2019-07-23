"""Drives a Chrome window/tab using remote debugging protocol.

Note that only one remote debug port can be used at a time. Using multiple
remote debug port to control multiple chromes is not possible. As such, we
forcibly close all existing chrome windows before creating new ones.
"""

import json
import subprocess
import urllib

import websocket

from qpylib import t
from qpylib.date_n_time import timing
from qpylib.web import nbshttp

_CHROME_REMOTE_DEBUGGING_ID = 77


class ChromeDriverException(Exception):
  pass


class ChromeNotRunning(ChromeDriverException):
  pass


class ChromeCommunicatorCommandError(ChromeDriverException):
  pass


class ChromeCommunicatorCommandJsError(ChromeCommunicatorCommandError):
  pass


class ChromeCommunicatorCommandUnknownError(ChromeCommunicatorCommandError):
  pass


class ChromeCommunicator:
  """Helps to communicate with debug websocket."""

  def __init__(self, websocket_address: t.Text):
    self._address = websocket_address
    self._ws = websocket.create_connection(websocket_address)

  def IsAlive(self):
    return self._ws.connected

  def Kill(self):
    return self._ws.close()

  def RunCommand(self, cmd: t.JSON) -> t.JSON:
    """Runs a remote debugging command.

    Args:
      cmd: the JSON command to execute. See:
        https://chromedevtools.github.io/devtools-protocol/
        Example:
        {
          'id': 1,
          'method': 'Runtime.evaluate',
          'params': {
            'expression': 'document.body.innerText',
          },
        }

    Returns:
      The JSON response from Chrome.
    """
    request = cmd
    request['id'] = _CHROME_REMOTE_DEBUGGING_ID
    self._ws.send(json.dumps(request))

    while True:
      response = json.loads(self._ws.recv())
      if response['id'] == _CHROME_REMOTE_DEBUGGING_ID:
        return response

  def RunJs(self, js: t.Text) -> t.JSON:
    """Runs a JS string and returns the result JSON."""
    return self.RunCommand({
      'method': 'Runtime.evaluate',
      'params': {
        'expression': js,
      }
    })['result']['result']

  def RunJs_GetValue(self, js: t.Text) -> t.Any:
    """Runs a JS string and returns a value.

    This function does the following:
    1. JS returns a value. Returns this value in this case (type is
       already converted).
    2. JS returns a DOM element. Returns the Chrome "node ID" in this case.
    3. JS resulted in an error. Raise ChromeCommunicatorCommandJsError with
       error description.
    4. Other case. Raise ChromeCommunicatorCommandUnknownError with the result
       JSON string.
    """
    result = self.RunJs(js)
    if 'value' in result:
      return result['value']

    if 'subtype' in result:
      if result['subtype'] == 'node':
        return result['objectId']
      elif result['subtype'] == 'error':
        raise ChromeCommunicatorCommandJsError(result['description'])

    raise ChromeCommunicatorCommandUnknownError(
      'Unknown error: ' + json.dumps(result))


class ChromeDriver:
  """Represents a running Chrome with remote debugging enabled."""

  def __init__(
      self,
      process: subprocess.Popen,
      remote_debugging_port: int = 9222,
  ):
    """Constructor.

    Args:
      process: the process that runs Chrome. Note that shell=True cannot be
        used to open the process otherwise it cannot be killed easily, see:
        https://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true/4791612#4791612
      remote_debugging_port: the remote debugging port.
    """
    self._proc = process
    self._remote_debugging_port = remote_debugging_port

  def IsAlive(self):
    return self._proc.poll() is None

  def CheckIsAlive(self):
    if not self.IsAlive():
      raise ChromeNotRunning('¯\_(ツ)_/¯')

  def Kill(self):
    self._proc.kill()

  def GetDebugWebSocketAddresses(self) -> t.List[t.Text]:
    """Gets all debug websocket addresses."""
    pages = nbshttp.JsonGet(
      'http://localhost:%d/json' % self._remote_debugging_port)
    return [p['webSocketDebuggerUrl'] for p in pages]

  def GetCommunicator(self, index: int = 0) -> ChromeCommunicator:
    """Gets a communicator for a debug websocket for the given index."""
    return ChromeCommunicator(self.GetDebugWebSocketAddresses()[index])


def CreateChromeDriver(
    remote_debugging_port: int = 9222,
    kill_existing_instances: bool = True,
    headless: bool = False,
    wait: bool = True,
) -> ChromeDriver:
  if kill_existing_instances:
    subprocess.run('killall -KILL -r chromium', shell=True)

  cmd = ['/usr/bin/chromium-browser', '--no-sandbox',
         '--remote-debugging-port=%d' % remote_debugging_port]
  if headless:
    cmd.append('--headless')
  p = subprocess.Popen(cmd)
  driver = ChromeDriver(p, remote_debugging_port=remote_debugging_port)
  if wait:
    timing.Wait(
      num_of_retries=10, wait_between_retries_sec=1).UntilNoException(
      urllib.error.URLError,
      driver.GetDebugWebSocketAddresses)
    timing.Wait(
      num_of_retries=10, wait_between_retries_sec=1).UntilNoException(
      ChromeCommunicatorCommandJsError,
      driver.GetCommunicator(0).RunJs_GetValue,
      'document.body.innerText;')
  return driver


class ChromeDriverManager(object):
  """Manages a Chrome instance with a fixed remote debugging port."""

  def __init__(
      self,
      remote_debugging_port: int = 9222,
      headless: bool = False,
  ):
    self._remote_debugging_port = remote_debugging_port
    self._headless = headless

    self._driver = None  # type: t.Optional[ChromeDriver]

  def Do(
      self,
      action_fn: t.Callable[[ChromeDriver], t.T],
      close_upon_completion: bool = False,
  ) -> t.T:
    """Performs actions using provided ChromeDriver.

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
    result = action_fn(driver)
    if close_upon_completion:
      self.Quit()
    return result

  def Quit(self):
    """Quits the created WebDriver."""
    if self._driver is not None:
      if self._driver.IsAlive():
        self._driver.Kill()
      self._driver = None
    return self._driver

  def _CreateDriver(self):
    self._driver = CreateChromeDriver(
      remote_debugging_port=self._remote_debugging_port,
      headless=self._headless)
    return self._driver

  def _GetOrCreateDriver(self):
    if self._driver is not None and self._driver.IsAlive():
      return self._driver

    self.Quit()
    return self._CreateDriver()

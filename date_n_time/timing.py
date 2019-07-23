"""Timing related helpers."""

import time

from qpylib import t, logging

_DEFAULT_NUM_OF_RETRIES = 3
_DEFAULT_WAIT_BETWEEN_RETRIES_SEC = 0.5


class WaitOutOfRetriesException(Exception):
  """Wait.Until* runs out of number of retries."""
  pass


class _ShouldRetrySignal(Exception):
  pass


class Wait:
  """Helps to perform wait actions.

  The action wait until action is done via one of the Until* functions, which
  is given the action function and its arguments.

  Examples:
    Wait(num_of_retries=5, wait_between_retries_sec=1).UntilTrue(
      ActionFunction, arg1, arg2)
  """

  def __init__(
      self,
      num_of_retries: int = _DEFAULT_NUM_OF_RETRIES,
      wait_between_retries_sec: float = _DEFAULT_WAIT_BETWEEN_RETRIES_SEC,
  ):
    """Constructor.

    Args:
      num_of_retries: how many retries to perform by the Until* functions.
      wait_between_retries_sec: the time to wait between retries, by the
        Until* functions.
    """
    self._num_of_retries = num_of_retries
    self._wait_between_retries_sec = wait_between_retries_sec

  def Until(
      self,
      success_predicate_func,
      action_function,
      *args,
      **kwargs,
  ) -> t.Any:
    """Waits until the given predicate returns True.

    Args:
      success_predicate_func: a function that takes the action function and its
        arguments, then decide whether the action succeeded. A retry will be
        issued if it raises _ShouldRetrySignal, otherwise it is assumed to be
        successful and its return value is returned.
      action_function: the actual action.
      args: args to the action function.
      kwargs: named args to the action function.
    """
    for _ in range(self._num_of_retries):
      try:
        return success_predicate_func(action_function, *args, **kwargs)
      except _ShouldRetrySignal as e:
        logging.info('Will retry if allowed; current error: %s', e)
        time.sleep(self._wait_between_retries_sec)
    raise WaitOutOfRetriesException(
      'Action did not succeed after %d retries.' % self._num_of_retries)

  def UntilValue(self, predicate_func, action_function, *args,
                 **kwargs) -> t.Any:
    """Waits until action_function's return value passes predicate_func."""

    def CheckValuePredicate(action_function, *args, **kwargs) -> t.Any:
      result = action_function(*args, **kwargs)
      if predicate_func(result):
        return result
      raise _ShouldRetrySignal(
        'Return value (capped at 200 characters): %s' % str(result)[:200])

    self.Until(CheckValuePredicate, action_function, *args, **kwargs)

  def UntilTrue(self, action_function, *args, **kwargs) -> t.Any:
    """Waits until action_function returns a non-False value."""
    self.UntilValue(lambda x: bool(x), action_function, *args, **kwargs)

  def UntilNoException(self, exception_type, action_function, *args, **kwargs):
    """Waits until action_function no longer throw exception of given type."""

    def CheckExceptionPredicate(action_function, *args, **kwargs) -> t.Any:
      try:
        return action_function(*args, **kwargs)
      except Exception as e:
        if isinstance(e, exception_type):
          raise _ShouldRetrySignal(e)
        raise e

    return self.Until(CheckExceptionPredicate, action_function, *args, **kwargs)


class SingleThreadThrottler(object):
  def __init__(self, limit_rate: float):
    """Constructor.

    Args:
      limit_rate (float): desired number of actions per second.
    """
    self._last_action_time_sec = time.time()
    self._delta_time_sec = 1.0 / limit_rate

  def WaitUntilNextAllowedTime(self):
    to_sleep_sec = self._delta_time_sec - (time.time() -
                                           self._last_action_time_sec)
    time.sleep(to_sleep_sec if to_sleep_sec > 0 else 0)
    self._last_action_time_sec = time.time()

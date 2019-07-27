"""Easier to use logging module."""

import datetime
import inspect
from logging import *

from qpylib import t

# Turns on INFO log by default.
getLogger().setLevel(INFO)


class ENV:
  # Debug verbosity, 0 means no debug logging.
  debug_verbosity = 2  # type: int


def vlog(
    verbosity: int,
    msg: t.Text,
    *args,
) -> None:
  """Logs a message only when debug_verbosity is large enough.
  
  Args:
    verbosity: the verbosity of the logging action. Only when 
      ENV.debug_verbosity is greater or equal to this value will the log 
      action happen.
    msg: the message format string.
    args: the args used in the message.
  """
  if ENV.debug_verbosity < verbosity:
    return

  caller = inspect.getframeinfo(inspect.stack()[1][0])
  prefix = '[%s] %s:%s ' % (
    datetime.datetime.now().strftime('%H:%M:%S'),
    caller.filename.split('/')[-1],
    caller.lineno)
  print(prefix + (msg % args))


def printf(msg: t.Text, *args):
  vlog(0, msg, *args)

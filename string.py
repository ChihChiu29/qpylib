"""Helps string manipulations."""

from qpylib import t


def GetClassName(ref) -> t.Text:
  """Gets a subclass's name.

  Args:
    ref: the reference to an object, usually "self".
  """
  return str(ref.__class__).rstrip('\'>').split('.')[-1]

"""Helpers for working with numpy."""

import numpy

from qpylib import t


def GetRow(a: numpy.ndarray, index: int) -> numpy.ndarray:
  """Gets the row with the given index while keeping the dimension."""
  return a[index, numpy.newaxis]


def IterRows(a: numpy.ndarray) -> t.Iterable[numpy.ndarray]:
  """Returns iterable for an array while keeping each row the same dim."""
  for row in a:
    return row[:, numpy.newaxis]


def SelectReduce(
    source_values: numpy.ndarray,
    mask: numpy.ndarray,
) -> numpy.ndarray:
  """Selects values from source_values according to the mask.

  Args:
    source_values: any numpy array.
    mask: a numpy array that has the same shape as values_array, and it only
      contains value 0 or 1.

  Returns:
    A new array consists of values from source_values where mask's corresponding
    values are 1. The result's dimension is mask.shape[:-1].
  """
  return numpy.sum(source_values * mask, axis=mask.ndim - 1)


def Replace(
    source_values: numpy.ndarray,
    mask: numpy.ndarray,
    new_values: numpy.ndarray,
) -> numpy.ndarray:
  """Replaces values in source_values by new_values at masked positions.

  Args:
    source_values: any numpy array.
    mask: a numpy array that has the same shape as values_array, and it only
      contains value 0 or 1.
    new_values: new values to set at positions indicated by mask. Its shape
      is mask.shape[:-1].

  Returns:
    A new array copied from source_values, but with values at locations
    indicated by mask (the 1's) replaced by new_values.
  """
  unchanged_values = source_values * (1 - mask)
  changed_values = mask * numpy.expand_dims(new_values, axis=new_values.ndim)
  return unchanged_values + changed_values


class TestUtil:
  
  @staticmethod
  def AssertArrayEqual(array1: numpy.ndarray, array2: numpy.ndarray):

    if numpy.array_equal(array1, array2):
      pass
    else:
      raise AssertionError('%s does not equal to %s' % (array1, array2))

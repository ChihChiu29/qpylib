"""Helpers for working with numpy."""
import keras
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
      try:
        diff = array1 - array2
        raise AssertionError(
          '\n%s\ndoes not equal to:\n%s\ndiff:\n%s' % (array1, array2, diff))
      except ValueError:
        raise AssertionError(
          '\n%s\ndoes not equal to:\n%s\nshape does not match either' % (
            array1, array2))

  @staticmethod
  def AssertModelWeightsEqual(model1: keras.Model, model2: keras.Model):
    weights1 = model1.get_weights()
    weights2 = model2.get_weights()
    if len(weights1) != len(weights2):
      raise AssertionError('model 1 has %d layers but model 2 has %d layers' % (
        len(weights1), len(weights2)))
    for idx in range(len(weights1)):
      try:
        TestUtil.AssertArrayEqual(weights1[idx], weights2[idx])
      except AssertionError as e:
        raise AssertionError('model weights mismatch for layer %d: %s' % (
          idx, e))

"""Unit tests for numpy_util.py."""

import unittest

import numpy

from qpylib import numpy_util


# Deprecated; use numpy_util.TestUtil instead.
class NumpyTestCase(unittest.TestCase):

  def assertArrayEq(self, array1: numpy.ndarray, array2: numpy.ndarray):
    if numpy.array_equal(array1, array2):
      pass
    else:
      self.fail('%s does not equal to %s' % (array1, array2))


class NumpyUtilTests(unittest.TestCase):

  def test_selectReduce_2d(self):
    numpy_util.TestUtil.AssertArrayEqual(
      numpy.array([2, 4]),
      numpy_util.SelectReduce(
        numpy.array([
          [1, 2, 3],
          [4, 5, 6],
        ]),
        numpy.array([
          [0, 1, 0],
          [1, 0, 0],
        ])))

  def test_selectReduce_1d(self):
    numpy_util.TestUtil.AssertArrayEqual(
      numpy.array([-0.9]),
      numpy_util.SelectReduce(
        numpy.array([[-0.9, 0, 0]]),
        numpy.array([[1, 0, 0]])))

  def test_replace(self):
    numpy_util.TestUtil.AssertArrayEqual(
      numpy.array([
        [1, 7, 3],
        [8, 5, 6],
      ]),
      numpy_util.Replace(
        numpy.array([
          [1, 2, 3],
          [4, 5, 6],
        ]),
        numpy.array([
          [0, 1, 0],
          [1, 0, 0],
        ]),
        numpy.array([7, 8]),
      ))

  def test_replace_highDimension(self):
    numpy_util.TestUtil.AssertArrayEqual(
      numpy.array([
        [
          [1, 10, 1],
          [3, 4, 3],
        ],
        [
          [12, 6, 5],
          [7, 13, 7],
        ]
      ]),
      numpy_util.Replace(
        numpy.array([
          [
            [1, 2, 1],
            [3, 4, 3],
          ],
          [
            [5, 6, 5],
            [7, 8, 7],
          ]
        ]),
        numpy.array([
          [
            [0, 1, 0],
            [0, 0, 0],
          ],
          [
            [1, 0, 0],
            [0, 1, 0],
          ]
        ]),
        numpy.array([
          [10, 11],
          [12, 13],
        ]),
      ))

  def test_EncodePositionsToOneHotArray(self):
    numpy_util.TestUtil.AssertArrayEqual(
      numpy.array([[0, 1, 0], [0, 0, 1]]),
      numpy_util.EncodePositionsToOneHotArray(numpy.array([1, 2]), 3))

"""Helpers for plotting."""

import datetime

import numpy as np
from matplotlib import pyplot as plt


def AddTimeTicker(
    start: float,
    end: float,
    number_of_tickers: int = 10,
    datetime_format: str = '%Y-%m-%d',
    rotation: float = 45):
  """Add time tickers for the given timestamp range.

  Args:
    start: the starting timestamp.
    end: the ending timestamp.
    number_of_tickers: how many tickers to have.
    datetime_format: used to format date_n_time.
    rotation: how ticker texts are rotated.
  """
  ticker_xs = np.linspace(start, end, number_of_tickers)
  labels = [
    datetime.datetime.fromtimestamp(ticker_x).strftime(datetime_format) for
    ticker_x in ticker_xs]
  plt.xticks(ticker_xs, labels, rotation=rotation)

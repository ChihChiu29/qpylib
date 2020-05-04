"""Easy-to-use timeseries."""
import datetime

import numpy
import numpy as np
import pandas
from matplotlib import pyplot
from scipy import integrate
from scipy import interpolate

from qpylib import plot_util
from qpylib import t
from qpylib.date_n_time import date

DEFAULT_FIGURE_DIMENSION = (18, 10)


class TimeSeries:
  """Helps to manage a time series.

  The time ticks do not need to be evenly spaced.
  """

  def __init__(
      self,
      time_series: t.List[float],  # timestamp
      value_series: t.List[float]):
    series = zip(time_series, value_series)
    series = list(sorted(series, key=lambda pair: pair[0]))

    self._t = np.array([pair[0] for pair in series])
    self._y = np.array([pair[1] for pair in series])
    self._interp = interpolate.interp1d(self._t, self._y)

  def GetTimeArray(self) -> np.ndarray:
    return self._t.copy()

  def GetValueArray(self) -> np.ndarray:
    return self._y.copy()

  def RestrictToRangeByTimestamp(
      self,
      start_timestamp: float,
      end_timestamp: float):
    new_t = []
    new_y = []
    for index, t in enumerate(self._t):
      if start_timestamp <= t <= end_timestamp:
        new_t.append(t)
        new_y.append(self._y[index])
    return TimeSeries(new_t, new_y)

  def RestrictToRangeByDatetime(
      self,
      start_datetime: datetime.datetime,
      end_datetime: datetime.datetime,
  ) -> 'TimeSeries':
    return self.RestrictToRangeByTimestamp(
      start_datetime.timestamp(), end_datetime.timestamp())

  def GetValueByTimestamp(self, timestamp: float) -> float:
    return self._interp([timestamp])[0]

  def GetValuesByTimestamp(self, timestamps: t.List[float]) -> t.List[float]:
    return self._interp(timestamps)

  def GetValueByDatetime(self, dt: datetime.datetime) -> float:
    return self.GetValueByTimestamp(dt.timestamp())

  def GetValuesByDatetime(
      self,
      dts: t.List[datetime.datetime],
  ) -> t.List[float]:
    return self.GetValuesByTimestamp([dt.timestamp() for dt in dts])

  def GetAverage(
      self,
      left_bound: float,
      right_bound: float,
  ) -> float:
    """Return average over a range."""
    return (
        integrate.quad(self.GetValueByTimestamp, left_bound, right_bound)[0] / (
        right_bound - left_bound))

  def GetMinTimestamp(self) -> float:
    return self._t[0]

  def GetMaxTimestamp(self) -> float:
    return self._t[-1]

  def GetMinDatetime(self) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(self.GetMinTimestamp())

  def GetMaxDatetime(self) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(self.GetMaxTimestamp())

  def ToDataFrame(self, rolling: int = None) -> pandas.DataFrame:
    df = pandas.DataFrame([self._t, self._y]).transpose()
    if rolling:
      df = df.rolling(rolling, center=True).mean()
    return df

  def ShiftTime(self, num_of_seconds: int):
    """Returns a copy with shifted time."""
    return TimeSeries(
      [t + num_of_seconds for t in self.GetTimeArray()],
      self.GetValueArray())

  def Rolling(self, rolling: int) -> 'TimeSeries':
    """Returns a rolling timeseries."""
    return FromDataFrame(self.ToDataFrame(rolling=rolling).dropna())

  def Plot(
    self,
    rolling: int = None,
    new_figure: bool = False,
    show: bool = True,
    **kwargs):
    """Plots the timeseries in the current figure.

    Args:
      rolling: plot with rolling average.
      show: whether to show the figure (otherwise more plots can be done to the
        same figure).
    """
    if new_figure:
      pyplot.figure(figsize=DEFAULT_FIGURE_DIMENSION)

    df = self.ToDataFrame(rolling=rolling)
    pyplot.plot(df[0], df[1], **kwargs)

    if show:
      plot_util.AddTimeTicker(self._t[0], self._t[-1])
      pyplot.legend()
      pyplot.show()


def FromDataFrame(df: pandas.DataFrame) -> TimeSeries:
  """Construct a timeseries from 1st and 2nd columns of a DataFrame."""
  return TimeSeries(df.iloc[:, 0], df.iloc[:, 1])


def CalculateCorrelation(ts1: TimeSeries, ts2: TimeSeries) -> float:
  """Calculates correlation between two timeseries.

  Only the overlapped time range is used, and only daily values are used.
  """
  left_t = max(ts1.GetMinDatetime(), ts2.GetMinDatetime())
  right_t = min(ts1.GetMaxDatetime(), ts2.GetMaxDatetime())
  days = [d for d in date.DaysBetween(left_t, right_t)]
  return numpy.corrcoef(
    ts1.GetValuesByDatetime(days),
    ts2.GetValuesByDatetime(days),
  )[0, 1]

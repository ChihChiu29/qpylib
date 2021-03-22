"""Helps manage dates."""

import datetime

from dateutil import relativedelta
from dateutil import rrule

from qpylib import t


class YearMonth:
  def __init__(self, year: int, month: int):
    self.year = year
    self.month = month

  def FirstDay(self) -> datetime.datetime:
    return datetime.datetime(self.year, self.month, 1)

  def LastDay(self) -> datetime.datetime:
    # See: https://stackoverflow.com/a/14994380
    return self.FirstDay() + relativedelta.relativedelta(day=31)

  def YYYYMM(self) -> str:
    return '%04d%02d' % (self.year, self.month)


def YearMonthFromDatetime(dt: datetime) -> YearMonth:
  return YearMonth(dt.year, dt.month)


def NextMonth(year_month: YearMonth) -> YearMonth:
  return YearMonthFromDatetime(
    year_month.FirstDay() + relativedelta.relativedelta(days=31))


def PreviousMonth(year_month: YearMonth) -> YearMonth:
  return YearMonthFromDatetime(
    year_month.FirstDay() - relativedelta.relativedelta(days=31))


def MonthsAfter(year_month: YearMonth, num_months: int):
  return YearMonthFromDatetime(
    year_month.FirstDay() + relativedelta.relativedelta(months=num_months))


def MonthsBefore(year_month: YearMonth, num_months: int):
  return YearMonthFromDatetime(
    year_month.FirstDay() - relativedelta.relativedelta(months=num_months))


def CurrentMonth() -> YearMonth:
  return YearMonthFromDatetime(datetime.datetime.today())


def MonthsBetween(
    start: YearMonth,
    end: YearMonth = None) -> t.Iterable[YearMonth]:
  """List months between two YearMonths, including "end"."""
  for dt in rrule.rrule(
      rrule.MONTHLY,
      dtstart=start.FirstDay(),
      until=end.FirstDay()):
    yield YearMonthFromDatetime(dt)


def DaysAfter(day: datetime.datetime, n: int) -> datetime.datetime:
  """Returns the day n days after the given day."""
  return day + relativedelta.relativedelta(days=n)


def NextDay(day: datetime.datetime) -> datetime.datetime:
  return DaysAfter(day, 1)


def DaysBefore(day: datetime.datetime, n: int) -> datetime.datetime:
  """Returns the day n days before the given day."""
  return day - relativedelta.relativedelta(days=n)


def PreviousDay(day: datetime.datetime) -> datetime.datetime:
  return DaysBefore(day, 1)


def DaysBetween(
    start: datetime.datetime,
    end: datetime.datetime) -> t.Iterable[datetime.datetime]:
  """List days between two datetimes, including "end" but not "start"."""
  # Get next day: start.date() + relativedelta.relativedelta(days=1),
  return rrule.rrule(rrule.DAILY, dtstart=start.date(), until=end.date())

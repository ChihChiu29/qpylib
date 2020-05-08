"""Helpers for getting Google Trends data."""
from typing import Iterable, Text

import pandas

from pytrends.request import TrendReq

from qpylib import storage

STORAGE = storage.DataFrameStorage('qpylib/trends')

_PYTREND = TrendReq()


def GetTrends(keywords: Iterable[Text], category: int=None) -> pandas.DataFrame:
  """Gets Google Trends history data.
  
  Args:
    keywords: a list of keywords to search.
    category: the index of a category. Use the Google Trends UI to see which
      index corresponds to which category. Index 0 should be "ALL" and index 7
      should be "Finance". Defaults to "ALL".

  Returns:
    The trends history.
  """
  if category is None:
    category = 0

  _PYTREND.build_payload(kw_list=list(keywords), cat=category)
  raw_date_df = _PYTREND.interest_over_time().reset_index()
  df = pandas.DataFrame()
  df['ts'] = raw_date_df['date'].apply(lambda x: x.timestamp())
  df['value'] = raw_date_df.iloc[:, 1]
  return df


def GetTrendsCached(
    keywords: Iterable[Text],
    category: int=None,
    force_download: bool=False,
) -> pandas.DataFrame:
  """Gets Google Trends history data.
  
  Args:
    keywords: a list of keywords to search.
    category: the index of a category. Use the Google Trends UI to see which
      index corresponds to which category. Index 0 should be "ALL" and index 7
      should be "Finance". Defaults to "ALL".
    force_download: if False, will reuse cached ones if exists.

  Returns:
    The trends history.
  """
  keywords = list(keywords)
  filename = '%s_google_trends.json' % '_'.join(keywords)
  if STORAGE.Exists(filename) and not force_download:
    return STORAGE.Load(filename)

  trends_df = GetTrends(keywords, category=category)
  STORAGE.Save(trends_df, filename)
  return trends_df

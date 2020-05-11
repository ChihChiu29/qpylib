"""Provides basic Google search functionality.

The `googlesearch` module is installed via `pip install google`; reference:
https://python-googlesearch.readthedocs.io/en/latest/index.html#module-googlesearch
"""
import datetime
from typing import Iterable, Text

import googlesearch


def QuickSearchUrls(
    query: Text,
    from_date: datetime.date,
    to_date: datetime.date = None,
    lang: Text = 'en',
    country: Text = 'usa',
    number_of_results: int = 100,
) -> Iterable[Text]:
  """Performs a Google news search using a query.

  Args:
    query: search query.
    from_date: search news from this date.
    to_date: search news until this date, default to today.
    lang: search news in this language.
    country: search news in this country.
    number_of_results: number of results to return.

  Returns:
    A list of searched result URLs.
  """
  if not to_date:
    to_date = datetime.date.today()
  tbs = googlesearch.get_tbs(from_date, to_date)
  return googlesearch.search(
    query, lang=lang, tbs=tbs, country=country, tpe="nws",
    stop=number_of_results)

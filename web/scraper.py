"""Generic article fetcher.

Related references:
* https://github.com/juanluisrto/stock-prediction-nlp/blob/master/google-news-scraping.ipynb
"""
from typing import Text

from newsplease import NewsPlease


def GetArticle(url: Text) -> dict:
  """Gets an article from an URL.

  Args:
    url: the url to fetch from.

  Returns:
    A dict for the article. Most important keys include: "title", "maintext".
  """
  return NewsPlease.from_url(url).to_dict()

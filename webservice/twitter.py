"""Provides helpers interacting with Twitter."""
import datetime
from typing import List, Text

import GetOldTweets3

DATE_FORMAT = '%Y-%m-%d'


def Search(
    query: Text,
    from_date: datetime.datetime = None,
    to_date: datetime.datetime = None,
    number_of_results: int = 10,
) -> List[GetOldTweets3.models.Tweet]:
  """Search tweets.

  Reference:
  * https://libraries.io/pypi/GetOldTweets3
  * https://github.com/Jefferson-Henrique/GetOldTweets-python

  Args:
    query: the search query.
    from_date: a date string like "2019-01-01". Leaving as None to not set it.
    to_date: a date string like "2019-01-01". Leaving as None to not set it.
    number_of_results: number of results to return.

  Returns:
    A list of tweets. Each tweet has attributes:
      'author_id',
      'date',
      'favorites',
      'formatted_date',
      'geo',
      'hashtags',
      'id',
      'mentions',
      'permalink',
      'replies',
      'retweets',
      'text',
      'to',
      'urls',
      'username'
  """
  tweetCriteria = GetOldTweets3.manager.TweetCriteria().setQuerySearch(query)
  if from_date:
    tweetCriteria.setSince(from_date.strftime(DATE_FORMAT))
  if to_date:
    tweetCriteria.setUntil(to_date.strftime(DATE_FORMAT))
  tweetCriteria.setMaxTweets(number_of_results)
  return GetOldTweets3.manager.TweetManager.getTweets(tweetCriteria)

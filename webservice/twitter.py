"""Provides helpers interacting with Twitter."""
import datetime
import os
import pandas
from typing import Dict, Iterable, List, Text

import nest_asyncio
import twint

from qpylib import storage


def Search(
    query: Text,
    from_date: datetime.datetime = None,
    to_date: datetime.datetime = None,
    number_of_results: int = 100,
) -> pandas.DataFrame:
  """Search tweets.

  Args:
    query: the search query.
    from_date: search from this datetime.
    to_date: search till this datetime.
    number_of_results: number of results to return.

  Returns:
    A dataframe of tweets. For columns, reference:
      {
        'id': 1371248526085226496,
        'conversation_id': '1371248036563795969',
        'created_at': '2021-03-14 23:54:59 UTC',
        'date': '2021-03-14',
        'time': '23:54:59',
        'timezone': '+0000',
        'user_id': 1233956153656332291,
        'username': 'je4ia',
        'name': 'funy guy sbungbob',
        'place': '',
        'tweet': '@Zer0Priv And stock up on Bitcoin and GameStop stocks',
        'language': 'en',
        'mentions': [],
        'urls': [],
        'photos': [],
        'replies_count': 0,
        'retweets_count': 0,
        'likes_count': 2,
        'hashtags': [],
        'cashtags': [],
        'link': 'https://twitter.com/je4ia/status/1371248526085226496',
        'retweet': False,
        'quote_url': '',
        'video': 0,
        'thumbnail': '',
        'near': '',
        'geo': '',
        'source': '',
        'user_rt_id': '',
        'user_rt': '',
        'retweet_id': '',
        'reply_to': [{'screen_name': 'Zer0Priv',
          'name': 'Zer0',
          'id': '1256485417744031747'}],
        'retweet_date': '',
        'translate': '',
        'trans_src': '',
        'trans_dest': '',
      },
  """
  nest_asyncio.apply()

  c = twint.Config()
  c.Search = query
  if from_date:
    c.Since = from_date.strftime('%Y-%m-%d %H:%M:%S')
  if to_date:
    c.Until = to_date.strftime('%Y-%m-%d %H:%M:%S')
  c.Limit = number_of_results
  c.Pandas = True
  c.Hide_output = True
  twint.run.Search(c)
  
  return twint.storage.panda.Tweets_df

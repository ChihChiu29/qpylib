import http
import json
import urllib

import bs4
from PIL import Image
from joblib import Memory

from qpylib import logging
from qpylib import storage
from qpylib import t

DISK_CACHE = Memory(
  cachedir=storage.GetCacheDirPath('tool/nbshttp'),
  verbose=0)

_DEFAULT_TIMEOUT_SEC = 30


def Get(
    url: t.Text,
    use_header: bool = True,
    timeout_sec: int = None,
) -> http.client.HTTPResponse:
  """Gets static content from a URL."""
  logging.info('Fetching from URL: %s', url)
  timeout_sec = timeout_sec if timeout_sec else _DEFAULT_TIMEOUT_SEC
  if use_header:
    return urllib.request.urlopen(urllib.request.Request(
      url,
      headers={
        'User-Agent': (
          'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
          '(KHTML, like Gecko) Ubuntu Chromium/75.0.3770.90 '
          'Chrome/75.0.3770.90 Safari/537.36')
      },
    ), timeout=timeout_sec)
  else:
    return urllib.request.urlopen(url, timeout=timeout_sec)


def JsonGet(
    url: t.Text,
    timeout_sec: int = None,
) -> t.JSON:
  """Gets a JSON over http GET."""
  return json.loads(Get(url, timeout_sec=timeout_sec).read())


@DISK_CACHE.cache
def JsonGetCached(
    url: t.Text,
    timeout_sec: int = None,
) -> t.JSON:
  """Gets a JSON over http GET, cached to disk."""
  return JsonGet(url, timeout_sec=timeout_sec)


def HtmlGet(
    url: t.Text,
    timeout_sec: int = None,
) -> bs4.BeautifulSoup:
  """Gets a static html page."""
  return bs4.BeautifulSoup(Get(url, timeout_sec=timeout_sec), 'html.parser')


def ImageGet(
    url: t.Text,
    use_header: bool = True,
    timeout_sec: int = None,
) -> Image:
  """Gets an image."""
  return Image.open(Get(url, use_header=use_header, timeout_sec=timeout_sec))

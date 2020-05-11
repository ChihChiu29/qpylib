"""Helper functions for sentiment analysis."""

from typing import Text

import numpy
import transformers

from qpylib import logging
from qpylib import storage


class BertBaseMultilingualUncasedSentiment:
  """A BERT based sentiment classifier.

  Reference:
  * https://github.com/juanluisrto/stock-prediction-nlp/blob/master/bert-sentiment.ipynb
  * https://github.com/juanluisrto/stock-prediction-nlp/tree/master
  """

  BASE_NAME = 'BertBaseMultilingualUncasedSentiment'

  def __init__(self):
    self._storage = storage.PickleStorage('qpylib/nlp/sentiment')

    self._tokenizer = None
    self._model = None
    self._Load()

  def _Load(self):
    logging.warning('Will take ~2 min for the initial download (2 GB)')
    self._tokenizer = transformers.AutoTokenizer.from_pretrained(
      'nlptown/bert-base-multilingual-uncased-sentiment')
    self._model = (
      transformers.TFAutoModelForSequenceClassification.from_pretrained(
        'nlptown/bert-base-multilingual-uncased-sentiment', from_pt=True))

  def Classify(self, content: Text) -> int:
    """Classifies some content as a 0-4 value (4 means best)."""
    self._tokenizer.encode(content)
    return int(
      numpy.argmax(self._model.predict([self._tokenizer.encode(content)])))

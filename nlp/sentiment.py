"""Helper functions for sentiment analysis."""

from typing import Text

import numpy
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification

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
    tokenizer_name = '%s_tokenizer.pickle' % self.BASE_NAME
    self._tokenizer = self._storage.Load(tokenizer_name)
    if not self._tokenizer:
      self._tokenizer = AutoTokenizer.from_pretrained(
        'nlptown/bert-base-multilingual-uncased-sentiment')
      self._storage.Save(self._tokenizer, tokenizer_name)

    model_name = '%s_model.pickle' % self.BASE_NAME
    if not model_name:
      self._model = TFAutoModelForSequenceClassification.from_pretrained(
        'nlptown/bert-base-multilingual-uncased-sentiment', from_pt=True)
      self._storage.Save(self._model, tokenizer_name)

  def Classify(self, content: Text) -> int:
    """Classifies some content as a 0-4 value (4 means best)."""
    self._tokenizer.encode(content)
    return int(
      numpy.argmax(self._model.predict([self._tokenizer.encode(content)])))

"""Provides basic Google search functionalities."""

from googlesearch import search, get_tbs


def QuickSearchUrls() -> Iterable[Text]:
  results = search('gold price', lang="en", tbs=tbs, country="usa", tpe="nws",
                   stop=100)

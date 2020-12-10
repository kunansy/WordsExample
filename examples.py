#!/usr/bin/env python3
import argparse
from typing import Union

import rnc

CORPORA = Union[rnc.MainCorpus, rnc.ParallelCorpus]


def get(word: str,
        count: int,
        corpus,
        **params) -> CORPORA:
    pages = count // 10 or 1
    corp = corpus(word, pages, marker=str.upper,
                  dpp=5, sort='random', **params)
    corp.request_examples()
    return corp


def get_russian(word: str,
                count: int) -> rnc.MainCorpus:
    return get(word, count, rnc.MainCorpus)


def get_parallel(word: str,
                 count: int,
                 language: str = 'en') -> rnc.ParallelCorpus:
    return get(word, count, rnc.ParallelCorpus,
               subcorpus=rnc.subcorpus[language])


def get_examples(word: str,
                 func,
                 count: int) -> None:
    try:
        corp = func(word, count)
    except ValueError:
        corp = func(word, 1)
    try:
        corp.sort_data(key=lambda example: len(example.txt))
    except AttributeError:
        corp.sort_data(key=lambda example: len(example.ru))

    for ex in corp[:count]:
        if isinstance(ex.txt, dict):
            for lang, text in ex.txt.items():
                print(f"{lang}: {text}")
            print()
        else:
            print(ex.txt)
            print()


def main() -> None:
    pass


if __name__ == "__main__":
    main()


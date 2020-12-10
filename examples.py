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
    parser = argparse.ArgumentParser(
        description="Get examples of the word usage. "
                    "It might be word in English or in Russian."
    )
    parser.add_argument(
        'word', metavar="Word", type=str,
    )
    parser.add_argument(
        '-c', '--corpus',
        metavar='Corpus',
        type=str,
        choices=['parallel', 'main'],
        default='main'
    )
    parser.add_argument(
        '-l', '--language',
        metavar='Language',
        type=str,
        default='en',
        choices=['en', 'fr', 'ger'],
        dest='lang'
    )
    parser.add_argument(
        '--count',
        metavar='Count',
        type=int,
        default=10
    )
    parser.add_argument(
        '-level', '--log-level',
        metavar="Logging level",
        type=str,
        default='warning',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        dest="level"
    )

    args = parser.parse_args()

    rnc.set_file_handler_level('CRITICAL')
    rnc.set_stream_handler_level(args.level.upper())

    lang = args.lang

    if args.corpus == 'main':
        func = get_russian
    else:
        func = get_parallel
        func.__defaults__ = (lang, )

    word = args.word
    count = args.count

    get_examples(word, func, count)


if __name__ == "__main__":
    main()


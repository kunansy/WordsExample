#!/usr/bin/env python3
import argparse
from typing import Union

import rnc

CORPORA = Union[rnc.MainCorpus, rnc.ParallelCorpus]


def get(word: str,
        count: int,
        corpus,
        **kwargs) -> CORPORA:
    pages = count // 10 or 1
    corp = corpus(word, pages, dpp=5, sort='random', **kwargs)
    corp.request_examples()
    return corp


def get_russian(word: str,
                count: int,
                **kwargs) -> rnc.MainCorpus:
    return get(word, count, rnc.MainCorpus, **kwargs)


def get_parallel(word: str,
                 count: int,
                 language: str = 'en',
                 **kwargs) -> rnc.ParallelCorpus:
    return get(word, count, rnc.ParallelCorpus,
               subcorpus=rnc.subcorpus[language], **kwargs)


def get_examples(word: str,
                 func,
                 count: int,
                 **kwargs) -> None:
    try:
        corp = func(word, count, **kwargs)
    except ValueError:
        corp = func(word, 1, **kwargs)

    if isinstance(corp, rnc.MainCorpus):
        corp.sort_data(key=lambda example: len(example.txt))
    elif isinstance(corp, rnc.ParallelCorpus):
        corp.sort_data(key=lambda example: len(example.ru))

    for ex in corp[:count]:
        if isinstance(ex, rnc.ParallelExample):
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
        choices=('parallel', 'main'),
        default='main'
    )
    parser.add_argument(
        '-l', '--language',
        metavar='Choose the lang of the examples; all langs from RNC possible',
        type=str,
        default='en',
        choices=('en', 'arm', 'bas', 'bel', 'bul', 'bur', 'sp', 'it', 'ch',
                 'lat', 'lit', 'ger', 'pol', 'ukr', 'fr', 'fin', 'cz', 'sw',
                 'es'),
        dest='lang'
    )
    parser.add_argument(
        '--count',
        metavar='Count of examples',
        type=int,
        default=10
    )
    parser.add_argument(
        '-level', '--log-level',
        metavar="Logging level",
        type=str,
        default='warning',
        choices=('debug', 'info', 'warning', 'error', 'critical'),
        dest="level"
    )
    parser.add_argument(
        '--marker',
        metavar='Choose how to mark found wordforms; upper of hide',
        type=str,
        default='upper',
        choices=('upper', 'hide'),
        dest='marker',
        required=False
    )

    args = parser.parse_args()

    rnc.set_file_handler_level('CRITICAL')
    rnc.set_stream_handler_level(args.level.upper())

    if args.corpus == 'main':
        func = get_russian
    else:
        func = get_parallel

    if args.marker == 'upper':
        marker = str.upper
    else:
        marker = lambda word: '***'

    get_examples(
        args.word, func, args.count, marker=marker, language=args.lang)


if __name__ == "__main__":
    main()

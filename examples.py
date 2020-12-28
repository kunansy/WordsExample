#!/usr/bin/env python3
import argparse
from typing import Union

import rnc

CORPORA = Union[rnc.MainCorpus, rnc.ParallelCorpus]


def get(word: str,
        count: int,
        corpus,
        **kwargs) -> CORPORA:
    """
    Get examples from the Corpus.

    Request count // 10 pages with dpp = 5 and
     random sort.

    There are >= count of examples than requested.

    :param word: str, word to find its usage.
    :param count: int, count of examples.
    :param corpus: obj, Corpus class from where get examples.
    :param kwargs: any kwargs for Corpus class.
    :return: Corpus object with got examples.
    :exception: all the same as Corpus.
    """
    pages = count // 10 or 1
    corp = corpus(word, pages, dpp=5, sort='random', **kwargs)
    corp.request_examples()
    return corp


def get_russian(word: str,
                count: int,
                **kwargs) -> rnc.MainCorpus:
    """
    Get examples from the MainCorpus.

    :param word: str, Russian word to find its usage.
    :param count: int, count of examples.
    :param kwargs: any kwargs for Corpus class.
    :return: MainCorpus object with got examples.
    :exception: all the same as Corpus.
    """
    return get(word, count, rnc.MainCorpus, **kwargs)


def get_parallel(word: str,
                 count: int,
                 language: str = 'en',
                 **kwargs) -> rnc.ParallelCorpus:
    """
    Get examples from the ParallelCorpus.

    :param word: str, word to find its usage.
    :param count: int, count of examples.
    :param language: str, lang of Corpus.
    :param kwargs: any kwargs for Corpus class.
    :return: ParalellCorpus object with got examples.
    :exception: all the same as Corpus.
    """
    return get(word, count, rnc.ParallelCorpus,
               mycorp=rnc.mycorp[language], **kwargs)


def get_examples(word: str,
                 func,
                 count: int,
                 **kwargs) -> None:
    """
    Get examples from the Corpus, sort them by length of
    Russian text and print very count of examples.

    :param word: str, word to find its usage.
    :param func: func which gets examples from the Corpus.
    :param count: int, count of examples.
    :param kwargs: any kwargs for Corpus class.
    :return: None.
    """
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
        else:
            print(ex.txt)
        print()


FUNC = {
    'main': get_russian,
    'parallel': get_parallel
}
MARKER = {
    'upper': str.upper,
    'hide': lambda word: '***'
}


def main() -> None:
    """
    Parse command args, turn off file handler of RNC logger,
    get and print examples according to command line args.

    :return: None.
    """
    parser = argparse.ArgumentParser(
        description="Get examples of the word usage. "
                    "It might be word in Russian or original language."
    )
    parser.add_argument(
        'word',
        metavar="Word(s) to find sentences with it (them).",
        type=str,
        nargs="+"
    )
    parser.add_argument(
        '-c', '--corpus',
        metavar="Corpus where search word's examples; "
                "parallel and main possible. Main by default.",
        type=str,
        choices=('parallel', 'main'),
        default='main'
    )
    parser.add_argument(
        '-l', '--language',
        metavar="Choose the language of the examples; "
                "all languages from RNC possible. English by default.",
        type=str,
        default='en',
        choices=('en', 'arm', 'bas', 'bel', 'bul', 'bur', 'sp', 'it', 'ch',
                 'lat', 'lit', 'ger', 'pol', 'ukr', 'fr', 'fin', 'cz', 'sw',
                 'es'),
        dest='lang'
    )
    parser.add_argument(
        '--count',
        metavar='Count of examples ot get. 10 by default.',
        type=int,
        default=10
    )
    parser.add_argument(
        '-level', '--log-level',
        metavar="Level of stream handler of RNC logger. Warning by default.",
        type=str,
        default='warning',
        choices=('notset', 'debug', 'info', 'warning', 'error', 'critical'),
        dest="level"
    )
    parser.add_argument(
        '--marker',
        metavar="Choose how to mark found wordforms; "
                "upper or hide, upper by default.",
        type=str,
        default='upper',
        choices=('upper', 'hide'),
        dest='marker',
        required=False
    )

    args = parser.parse_args()

    rnc.set_file_handler_level('CRITICAL')
    rnc.set_stream_handler_level(args.level.upper())

    func = FUNC[args.corpus]
    marker = MARKER[args.marker]

    get_examples(
        ' '.join(args.word), func, args.count,
        marker=marker, language=args.lang)


if __name__ == "__main__":
    main()

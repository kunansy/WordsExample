#!/usr/bin/env python3
import argparse
from typing import Union

import rnc

CORPORA = Union[rnc.MainCorpus, rnc.ParallelCorpus]

LEFT_RUS_BORDER, RIGHT_RUS_BORDER = ord('а'), ord('я')
LEFT_ENG_BORDER, RIGHT_ENG_BORDER = ord('a'), ord('z')


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
            print(f"txt: {ex.txt}")
        print(f"src: {ex.src}", end='\n\n')


def min_letter_index(string: str) -> int:
    """
    :param string: str to work with.
    :return: min index of letter symbol in the string;
     -1 if the string is empty, 2000 if there's no letter symbol.
    """
    if not string:
        return -1

    return min(
        ord(symbol.lower()) if symbol.isalpha() else 2_000
        for symbol in string
    )


def max_letter_index(string: str) -> int:
    """
    :param string: str to work with.
    :return: max index of letter symbol in the string;
     -1 if the string is empty or there's no letter symbol.
    """
    if not string:
        return -1

    return max(
        ord(symbol.lower()) if symbol.isalpha() else -1
        for symbol in string
    )


def is_russian(string: str) -> bool:
    """
    :return: bool, whether the string is Russian.
    """
    return min_letter_index(string) >= LEFT_RUS_BORDER and \
            max_letter_index(string) <= RIGHT_RUS_BORDER


def is_english(string: str) -> bool:
    """
    :return: bool, whether the string is English.
    """
    return min_letter_index(string) >= LEFT_ENG_BORDER and \
            max_letter_index(string) <= RIGHT_ENG_BORDER


FUNC = {
    'main': get_russian,
    'parallel': get_parallel
}
MARKER = {
    'upper': str.upper,
    'hide': lambda word: '***',
    'bold': lambda word: f"<b>{word}</b>",
    'ubold': lambda word: f"<b>{word.upper()}</b>",
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
        help="Word(s) to find sentences with it (them).",
        type=str,
        nargs="+"
    )
    parser.add_argument(
        '-c', '--corpus',
        help="Corpus where search word's examples; If the word is "
             "Russian use main, if it's English – use parallel.",
        type=str,
        choices=('parallel', 'main'),
        default=None,
        dest='corpus'
    )
    parser.add_argument(
        '-l', '--language',
        help="Choose the language of the examples; English by default.",
        type=str,
        default='en',
        choices=('en', 'arm', 'bas', 'bel', 'bul', 'bur', 'sp', 'it', 'ch',
                 'lat', 'lit', 'ger', 'pol', 'ukr', 'fr', 'fin', 'cz', 'sw',
                 'es'),
        dest='lang'
    )
    parser.add_argument(
        '--count',
        help='Count of examples ot get. 10 by default.',
        type=int,
        default=10,
        dest='count'
    )
    parser.add_argument(
        '-level', '--log-level',
        help="Level of stream handler of RNC logger. Warning by default.",
        type=str,
        default='warning',
        choices=('notset', 'debug', 'info', 'warning', 'error', 'critical'),
        dest="level"
    )
    parser.add_argument(
        '--marker',
        help="Choose how to mark found wordforms; Upper by default.",
        type=str,
        default='upper',
        choices=('upper', 'hide', 'bold', 'ubold'),
        dest='marker',
        required=False
    )

    args = parser.parse_args()

    rnc.set_file_handler_level('CRITICAL')
    rnc.set_stream_handler_level(args.level.upper())

    func = FUNC.get(args.corpus, None)
    marker = MARKER[args.marker]
    word = ' '.join(args.word)

    if is_english(word):
        func = FUNC['parallel']
    func = func or FUNC['main']

    get_examples(
        ' '.join(args.word), func, args.count,
        marker=marker, language=args.lang)


if __name__ == "__main__":
    main()


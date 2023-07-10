import pathlib
import re
from argparse import ArgumentParser
from dataclasses import dataclass
from typing import Optional


class ArgumentParserError(Exception):
    pass


def _get_argument_parser() -> ArgumentParser:
    parser = ArgumentParser()

    parser.add_argument(
        '-c', '--config-file',
        type=pathlib.Path,
        required=True,
        help='config file path'
    )

    parser.add_argument(
        '-t', '--service-tags',
        nargs='+',
        help='service tags to process'
    )

    parser.add_argument(
        '-i', '--input-file',
        type=pathlib.Path,
        help='file containing separated service tags to process'
    )

    parser.add_argument(
        '-s', '--separator',
        type=str,
        help='separator used in input file to separate service tags (default is whitespace)'
    )

    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='do not use previously cached results'
    )

    parser.add_argument(
        '-o', '--output-file',
        type=pathlib.Path,
        help='path to output file'
    )

    parser.add_argument(
        '--output-file-type',
        type=str,
        choices=['csv', 'tsv', 'ssv'],
        default='csv',
        help='type of the output file (csv - comma, tsv - tab, ssv - semicolon)'
    )

    parser.add_argument(
        '--output-file-include-header',
        action='store_true',
        help='include header in output CSV file'
    )

    return parser


@dataclass(init=False, eq=False)
class AppArgumentParser:
    config_file: pathlib.Path
    input_service_tags: Optional[list[str]]
    input_file: Optional[pathlib.Path]
    separator: Optional[str]
    no_cache: bool
    output_file: Optional[pathlib.Path]
    output_file_type: str
    output_file_include_header: bool

    def __init__(self) -> None:
        parser = _get_argument_parser()
        args = parser.parse_args()

        self.config_file = args.config_file
        self.input_service_tags = args.service_tags
        self.input_file = args.input_file
        self.separator = args.separator
        self.no_cache = args.no_cache
        self.output_file = args.output_file
        self.output_file_type = args.output_file_type
        self.output_file_include_header = args.output_file_include_header

        self._validate()

    def _validate(self):
        if not self.config_file.is_file():
            raise ArgumentParserError(f'invalid config file: {self.config_file!r}')

        if self.input_file is not None and not self.input_file.is_file():
            raise ArgumentParserError(f'invalid input file: {self.input_file!r}')

        if not self.input_service_tags and not self.input_file:
            raise ArgumentParserError('no service tags provided')

    def collect_service_tags(self) -> list[str]:
        collected = []

        if self.input_service_tags:
            collected.extend(self.input_service_tags)

        if self.input_file is not None and self.input_file.is_file():
            with open(self.input_file, 'r') as f:
                for st in f.read().split(self.separator):
                    collected.append(st.strip())

        parsed = []
        service_tag_pattern = re.compile('[0-9a-zA-Z]{7}')

        for st in set(collected):
            if service_tag_pattern.fullmatch(st):
                parsed.append(st.upper())

        return parsed

    @property
    def output_file_separator(self) -> str:
        mappings = {
            'csv': ',',
            'tsv': '\t',
            'ssv': ';'
        }

        return mappings[self.output_file_type]

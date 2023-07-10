import csv
import sys

from dell_st_lookup.app.parser import AppArgumentParser, ArgumentParserError
from dell_st_lookup.config import Config
from dell_st_lookup.database import SQLiteDeviceCache, DummyDeviceCache, DellDeviceCache
from dell_st_lookup.device import DellDevice
from dell_st_lookup.lookuper import DellServiceTagLookuper


def save_results_as_csv(parser: AppArgumentParser, results: list[DellDevice]) -> None:
    with open(parser.output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=parser.output_file_separator)

        if parser.output_file_include_header:
            writer.writerow([
                'Type', 'Name', 'Service tag', 'Warranty type', 'Warranty expiration date'
            ])

        for d in results:
            writer.writerow([
                d.device_type, d.name, d.service_tag,
                d.warranty_type or '', d.warranty_expiration_date or ''
            ])


def run_from_command_line():
    try:
        parser = AppArgumentParser()
    except ArgumentParserError as e:
        print(f'Invalid arguments: {e}', file=sys.stderr)
        exit(-1)

    config = Config.from_file(parser.config_file)
    service_tags = parser.collect_service_tags()

    if parser.no_cache:
        cache: DellDeviceCache = DummyDeviceCache()
    else:
        cache: DellDeviceCache = SQLiteDeviceCache(config)

    results = []
    cache_misses = []
    lookuper = None

    try:
        cache.open()

        for st in service_tags:
            if existing_device := cache.get_device(st):
                print(f'[CACHE] For service tag {st} got: {existing_device}')
                results.append(existing_device)
            else:
                cache_misses.append(st)

        if cache_misses:
            lookuper = DellServiceTagLookuper(config)
            lookuper.start()

            for st in cache_misses:
                if device := lookuper.get_product(st):
                    print(f'For service tag {st} got: {device}')
                    cache.insert_device(device)
                    results.append(device)
                else:
                    print(f'No such device: {st}')
    except Exception as e:
        print(f'Got exception: {e}')
        raise e
    finally:
        if lookuper:
            lookuper.quit()
        cache.close()

    if parser.output_file:
        save_results_as_csv(parser, results)

#! /usr/bin/env python

import argparse
import json
import logging
import sys


def parse_cli():
    parser = argparse.ArgumentParser(
        description='Parse pgbench output to json')

    parser.add_argument('-d', '--debug',
                        help='Print lots of debugging statements',
                        action='store_const', dest='loglevel', const=logging.DEBUG,
                        default=logging.WARNING)
    parser.add_argument('-v', '--verbose',
                        help='Be verbose',
                        action='store_const', dest='loglevel', const=logging.INFO)

    parser.add_argument('infile', nargs='?',
                        help='pgbench result file to parse, default is stdin',
                        type=argparse.FileType('r'),
                        default=sys.stdin)

    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    return args


def digit(s):
    """
    convert 's' to float or int

    :param s: string to convert to digit
    :returns: digital value of s
    :raises ValueError: if 's' can't be converted to either int or float
    """
    s = s.strip()
    for cast in [int, float]:
        try:
            s = cast(s)
            logging.debug('successfully cast %s to %s', s, cast)
            return s
        except ValueError:
            logging.debug("can't cast %s to %s", s, cast)
            continue
    raise ValueError


def with_unit(s):
    """
    convert 's' to digit while trying to parse the unit associated with the value

    :param s: string to convert to digit with unit
    :returns: digital value of s and its unit
    :raises ValueError: if 's' can't be converted to either int or float
    """
    s = s.strip()
    # Don't try to parse something that don't start with a number
    if not s[0].isdigit():
        logging.debug("s is doesn't start by a digit")
        raise ValueError
    numeric = '0123456789-. '
    for i, c in enumerate(s):
        if c not in numeric:
            break
    number = digit(s[:i])
    unit = s[i:].lstrip()
    value = {'value': number, 'unit': unit}
    logging.debug('converted %s to %s', s, value)
    return value


def main():
    """
    The main
    """
    args = parse_cli()
    raw_benchresult = [line.strip() for line in args.infile]

    bench_result = {}
    for line in raw_benchresult:

        # don't take care of script statistics for pgbench 9.6+
        if 'script statistics' in line or 'statement latencies in milliseconds' in line:
            break
        # ignore blank lines
        if not line:
            continue

        line = [e.strip() for e in line.replace('=', ':').split(':') if e.strip()]
        if len(line) != 2:
            continue

        # Parse --> number of transactions actually processed: 1000/1000
        if 'number of transactions actually processed' in line:
            label = 'percentage of transactions actually processed'
            value = eval(line[1]) * 100  # percentage of executed queries

        elif 'tps' in line:
            # Parse --> tps = 840.772771 (including connections establishing)
            if 'including' in line[1]:
                label = 'tps (including connections establishing)'
                # Parse --> tps = 842.418891 (excluding connections establishing)
            elif 'excluding' in line[1]:
                label = 'tps (excluding connections establishing)'
            value = float(line[1].split()[0])

        # Each types of number, int, float and with unit
        else:
            label = line[0]
            value = ':'.join(line[1:])
            for cast in [digit, with_unit]:
                try:
                    value = cast(value)
                    break
                except ValueError:
                    pass
            # Try to add some more information and find out number and unit
        bench_result[label] = value

    print(json.dumps(bench_result))


if __name__ == '__main__':
    main()

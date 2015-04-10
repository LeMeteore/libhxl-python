"""
Console scripts
David Megginson
April 2015

This is a big, ugly module to support the libhxl
console scripts, including (mainly) argument parsing.

License: Public Domain
Documentation: https://github.com/HXLStandard/libhxl-python/wiki
"""

import sys
import re
import argparse

from hxl import hxl, TagPattern, HXLException
from hxl.io import write_hxl

from hxl.filters.add import AddFilter
from hxl.filters.clean import CleanFilter
from hxl.filters.count import CountFilter
from hxl.filters.cut import ColumnFilter
from hxl.filters.merge import MergeFilter


#
# Console script entry points
#

def hxladd():
    """Console script for hxladd."""
    run_script(hxladd_main)

def hxlclean():
    """Console script for hxlclean."""
    run_script(hxlclean_main)

def hxlcount():
    """Console script for hxlcount."""
    run_script(hxlcount_main)

def hxlcut():
    """Console script for hxlcut."""
    run_script(hxlcut_main)

def hxlmerge():
    """Console script for hxlmerge."""
    run_script(hxlmerge_main)

#
# Main scripts for command-line tools.
#

#
# Command-line support
#

def hxladd_main(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    """
    Run hxladd with command-line arguments.
    @param args A list of arguments, excluding the script name
    @param stdin Standard input for the script
    @param stdout Standard output for the script
    @param stderr Standard error for the script
    """

    parser = argparse.ArgumentParser(description = 'Add new columns with constant values to a HXL dataset.')
    parser.add_argument(
        'infile',
        help='HXL file to read (if omitted, use standard input).',
        nargs='?'
        )
    parser.add_argument(
        'outfile',
        help='HXL file to write (if omitted, use standard output).',
        nargs='?'
        )
    parser.add_argument(
        '-v',
        '--value',
        help='Constant value to add to each row',
        metavar='[[Text header]#]<tag>=<value>',
        action='append',
        required=True
        )
    parser.add_argument(
        '-b',
        '--before',
        help='Add new columns before existing ones rather than after them.',
        action='store_const',
        const=True,
        default=False
    )
        
    args = parser.parse_args(args)

    with hxl(args.infile or stdin) as source, make_output(args.outfile, stdout) as output:
        filter = AddFilter(source, values=args.value, before=args.before)
        write_hxl(output.output, filter)


def hxlclean_main(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    """
    Run hxlclean with command-line arguments.
    @param args A list of arguments, excluding the script name
    @param stdin Standard input for the script
    @param stdout Standard output for the script
    @param stderr Standard error for the script
    """

    # Command-line arguments
    parser = argparse.ArgumentParser(description = 'Clean data in a HXL file.')
    parser.add_argument(
        'infile',
        help='HXL file to read (if omitted, use standard input).',
        nargs='?'
        )
    parser.add_argument(
        'outfile',
        help='HXL file to write (if omitted, use standard output).',
        nargs='?'
        )
    parser.add_argument(
        '-W',
        '--whitespace-all',
        help='Normalise whitespace in all columns',
        action='store_const',
        const=True,
        default=False
        )
    parser.add_argument(
        '-w',
        '--whitespace',
        help='Comma-separated list of tags for normalised whitespace.',
        metavar='tag,tag...',
        type=TagPattern.parse_list
        )
    parser.add_argument(
        '-u',
        '--upper',
        help='Comma-separated list of tags to convert to uppercase.',
        metavar='tag,tag...',
        type=TagPattern.parse_list
        )
    parser.add_argument(
        '-l',
        '--lower',
        help='Comma-separated list of tags to convert to lowercase.',
        metavar='tag,tag...',
        type=TagPattern.parse_list
        )
    parser.add_argument(
        '-D',
        '--date-all',
        help='Normalise all dates.',
        action='store_const',
        const=True,
        default=False
        )
    parser.add_argument(
        '-d',
        '--date',
        help='Comma-separated list of tags for date normalisation.',
        metavar='tag,tag...',
        type=TagPattern.parse_list
        )
    parser.add_argument(
        '-N',
        '--number-all',
        help='Normalise all numbers.',
        action='store_const',
        const=True,
        default=False
        )
    parser.add_argument(
        '-n',
        '--number',
        help='Comma-separated list of tags for number normalisation.',
        metavar='tag,tag...',
        type=TagPattern.parse_list
        )
    parser.add_argument(
        '-r',
        '--remove-headers',
        help='Remove text header row above HXL hashtags',
        action='store_const',
        const=False,
        default=True
        )
    args = parser.parse_args(args)
    
    with hxl(args.infile or stdin) as source, make_output(args.outfile, stdout) as output:

        if args.whitespace_all:
            whitespace_arg = True
        else:
            whitespace_arg = args.whitespace

        if args.date_all:
            date_arg = True
        else:
            date_arg = args.date

        if args.number_all:
            number_arg = True
        else:
            number_arg = args.number

        filter = CleanFilter(source, whitespace=whitespace_arg, upper=args.upper, lower=args.lower, date=date_arg, number=number_arg)
        write_hxl(output.output, filter, args.remove_headers)

#
# Command-line support
#

def hxlcount_main(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    """
    Run hxlcount with command-line arguments.
    @param args A list of arguments, excluding the script name
    @param stdin Standard input for the script
    @param stdout Standard output for the script
    @param stderr Standard error for the script
    """

    # Command-line arguments
    parser = argparse.ArgumentParser(description = 'Generate aggregate counts for a HXL dataset')
    parser.add_argument(
        'infile',
        help='HXL file to read (if omitted, use standard input).',
        nargs='?'
        )
    parser.add_argument(
        'outfile',
        help='HXL file to write (if omitted, use standard output).',
        nargs='?'
        )
    parser.add_argument(
        '-t',
        '--tags',
        help='Comma-separated list of column tags to count.',
        metavar='tag,tag...',
        type=TagPattern.parse_list,
        default='loc,org,sector,adm1,adm2,adm3'
        )
    parser.add_argument(
        '-a',
        '--aggregate',
        help='Hashtag to aggregate.',
        metavar='tag',
        type=TagPattern.parse
        )

    args = parser.parse_args(args)
    with hxl(args.infile or stdin) as source, make_output(args.outfile, stdout) as output:
        filter = CountFilter(source, args.tags, args.aggregate)
        write_hxl(output.output, filter)


def hxlcut_main(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    parser = argparse.ArgumentParser(description = 'Cut columns from a HXL dataset.')
    parser.add_argument(
        'infile',
        help='HXL file to read (if omitted, use standard input).',
        nargs='?'
        )
    parser.add_argument(
        'outfile',
        help='HXL file to write (if omitted, use standard output).',
        nargs='?'
        )
    parser.add_argument(
        '-i',
        '--include',
        help='Comma-separated list of column tags to include',
        metavar='tag,tag...',
        type=TagPattern.parse_list
        )
    parser.add_argument(
        '-x',
        '--exclude',
        help='Comma-separated list of column tags to exclude',
        metavar='tag,tag...',
        type=TagPattern.parse_list
        )
    args = parser.parse_args(args)

    with hxl(args.infile or stdin) as source, make_output(args.outfile, stdout) as output:
        filter = ColumnFilter(source, args.include, args.exclude)
        write_hxl(output.output, filter)

def hxlmerge_main(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    """
    Run hxlmerge with command-line arguments.
    @param args A list of arguments, excluding the script name
    @param stdin Standard input for the script
    @param stdout Standard output for the script
    @param stderr Standard error for the script
    """

    parser = argparse.ArgumentParser(description = 'Merge part of one HXL dataset into another.')
    parser.add_argument(
        'infile',
        help='HXL file to read (if omitted, use standard input).',
        nargs='?'
        )
    parser.add_argument(
        'outfile',
        help='HXL file to write (if omitted, use standard output).',
        nargs='?'
        )
    parser.add_argument(
        '-m',
        '--merge',
        help='HXL file to write (if omitted, use standard output).',
        metavar='filename',
        required=True
        )
    parser.add_argument(
        '-k',
        '--keys',
        help='HXL tag(s) to use as a shared key.',
        metavar='tag,tag...',
        required=True,
        type=TagPattern.parse_list
        )
    parser.add_argument(
        '-t',
        '--tags',
        help='Comma-separated list of column tags to include from the merge dataset.',
        metavar='tag,tag...',
        required=True,
        type=TagPattern.parse_list
        )
    parser.add_argument(
        '-r',
        '--replace',
        help='Replace empty values in existing columns (when available) instead of adding new ones.',
        action='store_const',
        const=True,
        default=False
    )
    parser.add_argument(
        '-O',
        '--overwrite',
        help='Used with --replace, overwrite existing values.',
        action='store_const',
        const=True,
        default=False
    )
    args = parser.parse_args(args)

    # FIXME - will this be OK with stdin/stdout?
    with hxl(args.infile or stdin) as source, make_output(args.outfile, stdout) as output, hxl(args.merge) if args.merge else None as merge_source:
        filter = MergeFilter(source, merge_source=merge_source,
                             keys=args.keys, tags=args.tags, replace=args.replace, overwrite=args.overwrite)
        write_hxl(output.output, filter)


#
# Utility scripts
#

def run_script(func):
    """Try running a command-line script, with exception handling."""
    try:
        func(sys.argv[1:], sys.stdin, sys.stdout)
    except HXLException as e:
        print >>sys.stderr, "Fatal error (" + e.__class__.__name__ + "): " + str(e.message)
        print >>sys.stderr, "Exiting ..."
        sys.exit(2)
    except KeyboardInterrupt:
        print >>sys.stderr, "Interrupted"
        sys.exit(2)

def make_output(filename, stdout=sys.stdout):
    if filename:
        return FileOutput(filename)
    else:
        return StreamOutput(stdout)

class FileOutput(object):

    def __init__(self, filename):
        self.output = open(filename, 'w')

    def __enter__(self):
        return self

    def __exit__(self, value, type, traceback):
        close(self.output)

class StreamOutput(object):

    def __init__(self, output):
        self.output = output

    def __enter__(self):
        return self

    def __exit__(self, value, type, traceback):
        pass
            
    

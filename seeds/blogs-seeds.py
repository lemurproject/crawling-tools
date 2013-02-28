#!/usr/bin/env python

import sys
import os
import urlparse
import fileinput
import logging
import argparse
import gzip
import itertools as it

pjoin = os.path.join

site_patterns = {
    'wordpress': [
        '2012/01/', '2012/02/', '2012/03/', '2012/04/', '2012/05/',
    ],
    'blogger': [
        '2012_01_01_archive.html',
        '2012_02_01_archive.html',
        '2012_03_01_archive.html',
        '2012_04_01_archive.html',
        '2012_05_01_archive.html'
    ]
}

def seeds_for_url(url, site):
    try:
        url = url.rstrip('/')
        if not site:
            # Guess based on the host
            parsed = urlparse.urlparse(url)
            assert parsed.netloc, 'Empty host name'

            if parsed.netloc.endswith('.wordpress.com'):
                site = 'wordpress'
            elif parsed.netloc.endswith('.blogspot.com'):
                site = 'blogger'

        patterns = site_patterns.get(site)
        assert len(patterns) > 0, 'Skipping line, unknown site'
        return ['%s/%s' % (url, p) for p in patterns]

    except Exception as e:
        logger.debug('Error parsing URL: %s %s' % (line, e))
        return []


def generate_seeds(lines, site=None):
    '''Generate the seeds for a sequence of lines.
    
    `site`: Name of the website used to generate the seeds. Use `None` to
       generate it from the host name (not always correct for sites like 
       Wordpress).
    '''
    for line in lines:
        line = line.strip()
        for u in seeds_for_url(line, site):
            yield u

def output_stdout(seeds):
    for s in seeds:
        print s


def grouper(n, iterable):
    "Collect data into fixed-length chunks or blocks"
    # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return it.izip_longest(*args)


def output_heritrix(seeds, outdir, n):
    '''
    Writes the seeds into separeted files, according to the directory layout
    for Heritrix jobs.

    It creates first a file named $outdir/seeds.txt with the first 1000 seeds,
    the rest are written in files named $outdir/action/sites-$i.seeds.gz; each
    file will contain up to `n` entries.

    '''
    assert os.path.isdir(outdir)
    assert os.path.isdir(pjoin(outdir, 'action'))
    print 'heritrix', outdir

    base_seeds = it.islice(seeds, 0, 1000)
    base_fname = pjoin(outdir, 'seeds.txt')
    base_fp = open(base_fname)
    for seed in base_seeds:
        base_fp.write(seed)
        base_fp.write('\n')
    base_fp.close()

    groups_seeds = grouper(seeds, n)
    for n, group in enumerate(groups_seeds):
        group_fname = pjoin(outdir, 'action', 'sites-%s.seeds.gz' % n, 'w+')
        group_fp = gzip.open(group_fname)
        for seed in group:
            if not seed:
                continue
            group_fp.write(seed)
        group_fp.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--heritrix-dir', 
        help='Directory for writing the output as Heritrix seed files.')
    parser.add_argument('-n', default=100000, 
        help='Number of URLs to be grouped (for Heritrix seed files only)')
    parser.add_argument('-s', '--site', choices=site_patterns.keys(),
        help='Name of the website used to generate the patterns.')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('input', nargs='*', help='Input file')

    args = parser.parse_args()

    if len(args.input) == 0:
        print >> sys.stderr, 'Reading from the standard input'

    logging_level = logging.INFO
    if args.verbose:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level)

    # Read the lines from stdin or from the arguments
    lines = fileinput.input(args.input, openhook=fileinput.hook_compressed)

    # Generate the seeds
    seeds = generate_seeds(lines, site=args.site)

    # Write the output
    if args.heritrix_dir:
        output_heritrix(seeds, args.heritrix_dir, args.n)
    else:
        output_stdout(seeds)


if __name__ == '__main__':
    main()

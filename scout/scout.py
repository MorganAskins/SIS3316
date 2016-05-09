#!/usr/bin/env python2
import scout_configure
import connection
import readout
import time
import argparse

def main():
  args = aparse()
  host = connection.sis_address()
  if not host:
    print 'run connection.py on its own with elevated permissions first'
    exit()
  scout_configure.setup(host, 3333, False)
  print 'Configured sis3316 at ip %s' % host
  readout.main(host, 3333, args.fname, range(0,16), args.time)

def aparse():
  parser = argparse.ArgumentParser()
  parser.add_argument('fname', type=str,
      help="Output data file")
  parser.add_argument('-t', '--time', type=int, default=0,
      help="Runtime")
  return parser.parse_args()


if __name__ == '__main__':
  main()

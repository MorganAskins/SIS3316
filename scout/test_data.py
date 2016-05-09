#!/usr/bin/env python2
import io
from struct import unpack
from parse import Parse
import matplotlib.pylab as plt
import argparse

def aparser():
  aparser = argparse.ArgumentParser()
  aparser.add_argument('fname', type=str,
      help="Input data file")
  return aparser.parse_args()

def main():
  args = aparser()
  infile = io.open(args.fname, 'rb')
  data = infile.read()

  #test_integer = unpack('<I', '\x00\x02\x00\xe8')[0]
  # Test integer is found at data[44:48]
  test_integer = unpack('<I', data[44:48])[0]
  print('0xE: %s, MAW: %i, Samples: %i' % (hex(test_integer >> 28), test_integer & (1<<27), test_integer & 0x3ffffff))
  #test_integer = unpack('<I', '@\x00\x00\xe0')[0]
  # Seek through this data and find this integer
  def check(intgr):
    num = unpack('<I', intgr)[0]
    if num == test_integer:
      return True
    return False
  num_bytes = len(data)/4
  start_points = []
  for i in range(num_bytes):
    if check( data[i*4:(i*4+4)] ):
      start_points.append(i*4+4)
  evt_length = 64
  evt_plots = []
  for sp in start_points:
    values = []
    for i in range(evt_length):
      values.append(unpack('<I', data[(sp+i*4):(sp+4+i*4)])[0])
    evt_plots.append(values)
  for ep in evt_plots:
    plt.plot(ep)
  plt.show()

  print('num events:', len(start_points))
  print('start points:', start_points)

if __name__ == '__main__':
  main()

#!/usr/bin/env python2
import io
from struct import unpack
from struct import pack
import argparse
import numpy as np
import sys

def aparser():
  aparser = argparse.ArgumentParser()
  aparser.add_argument('fname', type=str,
      help="Input data file")
  return aparser.parse_args()

class sisparser():
  '''
  Parse data and reorganize into a .scout file. Data will
  be ordered in timing and then channel number.
  '''
  def __init__(self, infile):
    self.infile = io.open(infile, 'rb')
    out_name = infile.split('.')[0] + '.scout'
    self.outfile = io.open(out_name, 'wb')
    self.event = 0
    self.events = {}

  def parse(self):
    while True:
      if self.infile.peek() is '':
        break
      self.write_channel()
      if self.infile.tell() % 100000:
        sys.stderr.write('Processed %.2f MB\r' % (self.infile.tell() / (1.0e6))) 
    self.header()
    for ts in sorted(self.events):
      ev = self.events[ts]
      chlist = sorted(ev, key=lambda k: k['channel'])
      for ch in chlist:
        self.outfile.write(ch['raw'])

  def header(self):
    '''
    Add header to beginning of .scout file giving:
    events ('<I'), number of channels ('<B'), TBA
    '''
    total_events = len(self.events)
    total_channels = len(self.events.itervalues().next())
    length_raw = len(self.events.itervalues().next()[0]['raw'])
    self.outfile.write( pack('<I', total_events) )
    self.outfile.write( pack('<I', total_channels) )
    self.outfile.write( pack('<I', length_raw) )
    

  def write_channel(self):
    channel_data = self.read_channel()
    ts = channel_data['timestamp']
    if ts not in self.events:
      self.events[ts]=[]
    self.events[ts].append(channel_data)

  def read_channel(self):
    '''
    Since data files can become very large, events are read
    sequentially, each written and then removed from memory
    and not stored in memory
    '''
    data = self.infile
    cd = {} #channel data in dictionary
    raw = b''
    raw += data.read(4)
    ch_fmt, ts_hi= unpack('<HH', raw[-4:])
    ch, fmt = (ch_fmt >> 4), (ch_fmt & 0xF)
    cd['channel'] = ch
    raw += data.read(4)
    ts_lo, ts_mid= unpack('<HH', raw[-4:])
    timestamp = (ts_hi << 32) + (ts_mid << 16) + ts_lo #in adc counts
    cd['timestamp'] = timestamp
    if (fmt & 0b0001):
      # peak high value
      raw += data.read(28)
    if (fmt & 0b0010):
      raw += data.read(8)
    if (fmt & 0b0100):
      raw += data.read(8)
    if (fmt & 0b1000):
      raw += data.read(8)
    # Length of waveform and maw info
    raw += data.read(4)
    stuff = unpack('<I', raw[-4:])[0]
    OxE, fMAW = (stuff >> 28), (stuff & (1<<27))    
    status, samples = (stuff & (1<<26)), (stuff & 0x3ffffff)
    raw += data.read(4*samples)
    cd['raw'] = raw
    # We are now at the end of the channel's events
    return cd

def main():
  args = aparser()
  sp = sisparser(args.fname)
  sp.parse()

if __name__ == '__main__':
  main()

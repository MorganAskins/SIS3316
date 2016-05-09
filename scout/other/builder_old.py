#!/usr/bin/env python
import io
from struct import unpack
from struct import pack
import argparse
import h5py as hp
import numpy as np
import sys
import json

def aparser():
  aparser = argparse.ArgumentParser()
  aparser.add_argument('fname', type=str,
      help="Input data file")
  return aparser.parse_args()

class sisparser():
  '''
  Parse the sis3316 and write data to an hdf5 file
  TODO: Currently I throw an error if the MAW enable
  bit is set for a channel because I don't need it and
  don't want to deal with it. This can be fix, but has
  the unfortunate problem that the MAW length is not given.
  Currently writes to another custom binary file that
  preserves event structure and event information
  '''
  def __init__(self, infile):
    self.infile = io.open(infile, 'rb')
    #out_name = infile.split('.')[0] + '.hdf5'
    #self.outfile = hp.File(out_name, 'w')
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
    #try:
    #  grp = self.outfile.create_group(str(ts))
    #except ValueError:
    #  grp = self.outfile[str(ts)]
    #chgrp = grp.create_group(str(channel_data['channel']))
    #for key, value in channel_data.iteritems():
    #  chgrp.create_dataset(key, data=value)

  def read_channel(self):
    '''
    Since data files can become very large, events are read
    sequentially, each written and then removed from memory
    and not stored in memory
    '''
    # Assume we are at the start of an event and seeking the end
    # for a single channel, then iterate until that same channel
    # occ'153292120947993'urs again, then check timestamps to confirm events
    data = self.infile
    cd = {} #channel data in dictionary
    raw = ''
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
      raw += data.read(4)
      idx_phv, phv = unpack('<HH', raw[-4:])
      cd['peak_high_value_idx'], cd['peak_high_value'] = idx_phv, phv
      raw += data.read(4)
      info_gate1 = unpack('<I', raw[-4:])[0]
      info, gate1 = (info_gate1 >> 24), (info_gate1 & 0xFF000000)
      cd['gate_1'] = gate1
      raw += data.read(4)
      gate2 = unpack('<I', raw[-4:])[0]
      cd['gate_2'] = gate2
      raw += data.read(4)
      gate3 = unpack('<I', raw[-4:])[0]
      cd['gate_3'] = gate3
      raw += data.read(4)
      gate4 = unpack('<I', raw[-4:])[0]
      cd['gate_4'] = gate4
      raw += data.read(4)
      gate5 = unpack('<I', raw[-4:])[0]
      cd['gate_5'] = gate5
      raw += data.read(4)
      gate6 = unpack('<I', raw[-4:])[0]
      cd['gate_6'] = gate6
    if (fmt & 0b0010):
      raw += data.read(4)
      gate7 = unpack('<I', raw[-4:])[0]
      cd['gate_7'] = gate7
      raw += data.read(4)
      gate8 = unpack('<I', raw[-4:])[0]
      cd['gate_8'] = gate8
    if (fmt & 0b0100):
      raw += data.read(4)
      maw_before_trig = unpack('<I', raw[-4:])[0]
      cd['maw_before_trig'] = maw_before_trig
      raw += data.read(4)
      maw_after_trig= unpack('<I', raw[-4:])[0]
      cd['maw_after_trig'] = maw_after_trig
    if (fmt & 0b1000):
      raw += data.read(4)
      start_energy = unpack('<I', raw[-4:])[0]
      cd['start_energy'] = start_energy
      raw += data.read(4)
      max_energy = unpack('<I', raw[-4:])[0]
      cd['max_energy'] = max_energy
    # Length of waveform and maw info
    raw += data.read(4)
    stuff = unpack('<I', raw[-4:])[0]
    OxE, fMAW = (stuff >> 28), (stuff & (1<<27))    
    status, samples = (stuff & (1<<26)), (stuff & 0x3ffffff)
    waveform = []
    for i in range(samples):
      raw += data.read(4)
      waveform.append(unpack('<I', raw[-4:])[0])
    cd['waveform'] = waveform
    cd['raw'] = raw
    # We are now at the end of the channel's events
    return cd


def main():
  args = aparser()
  sp = sisparser(args.fname)
  sp.parse()

if __name__ == '__main__':
  main()

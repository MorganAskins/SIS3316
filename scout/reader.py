#!/usr/bin/env python2

import io
from struct import unpack
import numpy as np
import argparse
import matplotlib.pyplot as plt
import os, sys

class scoutparser():
  '''
  Similar to sisparser but with a header and ordered events
  '''
  def __init__(self, infile):
    self.infile = io.open(infile, 'rb')
    self.header()
    self.channels = []

  def __iter__(self):
    self.current_iter = 0
    self.stop_iter = self.num_events
    return self

  def next(self):
    if self.current_iter >= self.num_events:
      raise StopIteration
    else:
      self.load_event(self.current_iter)
      self.current_iter += 1
      return self.event


  def header(self):
    '''
    Read the header of the .scout file to gain information
    '''
    self.num_events = unpack('<I', self.infile.read(4))[0]
    self.num_channels = unpack('<I', self.infile.read(4))[0]
    self.ch_bytes = unpack('<I', self.infile.read(4))[0]
    self.start = self.infile.tell()

  def load_event(self, event):
    data = self.infile
    event_start = self.start + event*self.num_channels*self.ch_bytes
    data.seek(event_start)
    self.event = scoutevent()
    for i in range(self.num_channels):
      channel = scoutchannel(data.read(self.ch_bytes))
      self.event.add_channel(channel)

class scoutevent():
  '''
  Contains event information
  '''
  def __init__(self):
    self.channels = []

  def add_channel(self, channel):
    self.channels.append(channel)


class scoutchannel():
  '''
  Contains the following variables:
  ch, fmt, timestamp, idx_phv, phv, info
  gate{1..8}, maw_before_trig, maw_after_trig
  start_energy, 0xE, fMAW, status, samples
  waveform (as np array if '<I')
  '''
  def __init__(self, chan_data):
    self.load_channel(chan_data)

  def byte_reader(self, byte_in):
    '''
    Generator 4 byte integers from byte array
    '''
    ba = byte_in 
    msg = b''
    for idx, bite in enumerate(ba):
      msg += bite
      if not ((idx+1) % 4):
        yield msg
        msg = b''

  def load_channel(self, cd):
    reader = self.byte_reader(cd)
    ch_fmt, ts_hi = unpack('<HH', next(reader))
    self.ch, self.fmt = (ch_fmt >> 4), (ch_fmt & 0xF)
    ts_lo, ts_mid = unpack('<HH', next(reader))
    self.timestamp = (ts_hi << 32) + (ts_mid << 16) + ts_lo
    if (self.fmt & 0b0001):
      self.idx_phv, self.phv = unpack('<HH', next(reader))
      info_gate1 = unpack('<I', next(reader))[0]
      self.info, self.gate1 = (info_gate1 >> 24), (info_gate1 & 0xFF000000)
      self.gate2 = unpack('<I', next(reader))[0]
      self.gate3 = unpack('<I', next(reader))[0]
      self.gate4 = unpack('<I', next(reader))[0]
      self.gate5 = unpack('<I', next(reader))[0]
      self.gate6 = unpack('<I', next(reader))[0]
    if (self.fmt & 0b0010):
      self.gate7 = unpack('<I', next(reader))[0]
      self.gate8 = unpack('<I', next(reader))[0]
    if (self.fmt & 0b0100):
      self.maw_before_trig = unpack('<I', next(reader))[0]
      self.maw_after_trig = unpack('<I', next(reader))[0]
    if (self.fmt & 0b1000):
      self.start_energy = unpack('<I', next(reader))[0]
      self.max_energy = unpack('<I', next(reader))[0]
    stuff = unpack('<I', next(reader))[0]
    self.OxE, self.fMAW = (stuff >> 28), (stuff & (1<<27))
    self.status, self.samples = (stuff & (1<<26)), (stuff & 0x3ffffff)
    waveform_bytes = b''
    while True:
      try:
        waveform_bytes += next(reader)
      except StopIteration:
        break
    self.waveform = np.frombuffer(waveform_bytes, dtype='<I')

def get_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('file', type=str,
      help="filename")
  return parser.parse_args()

if __name__ == '__main__':
  args = get_args()
  scout = scoutparser(args.file)
  print scout.num_events
  for idx,ev in enumerate(scout):
    plt.plot(ev.channels[2].waveform)
    if idx > 50:
      break
    
  plt.show()

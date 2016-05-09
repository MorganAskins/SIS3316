#!/usr/bin/env python2
import sys, os
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import sis3316
import argparse

def parser():
  parser = argparse.ArgumentParser()
  parser.add_argument('host', type=str,
      help="SIS3316 IP Address")
  parser.add_argument('-p', '--port', type=int, default=3333,
      help="SIS3316 Host port, default 3333")
  parser.add_argument('--debug', action='store_true',
      help="Turn debug verbosity on")
  return parser.parse_args()

class bugger():
  def __init__(self, debug):
    self._debug = debug
  def bprint(self, txt):
    if self._debug:
      print(txt)

def setup(host, port, debug):
  bug = bugger(debug)
  bug.bprint( 'Connecting to %s:%i' % (host,port) )
  dev = sis3316.Sis3316_udp(host, port)
  dev.open()
  dev.reset()
  dev.configure()
  dev.flags = ['nim_ti_as_te', 'extern_ts_clr_ena', 'extern_trig_ena']
  #active_channels = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
  active_channels = [0,1,2,3]
  chflags = ['extern_trig', 'invert']
  # 0x74 LEMO TI to TE
  dev.write(0x74, 0x10000)
  # Turn on sample saving for group 1
  sample_size = 128 & 0xFFFE
  sample_value = 0x0 + (sample_size << 16)
  dev.write(0x1020, sample_value)
  ## Thresholds
  threshold = 134218528 
  high_threshold = 134742000 
  #dev.write(0x7c,0xF0000)
  for ch in dev.channels:
    if ch.idx in active_channels:
      #ch.dac_offset = 10000
      ch.flags = chflags
      ch.event_format_mask = 9
      ch.trig.cfd_ena = 3
      ch.trig.threshold = 100000
      ch.trig.high_threshold = 120000
      ch.trig.out_pulse_length = 4
  for gr in dev.groups:
    if (gr.idx == 0):
      gr.clear_link_error_latch_bits()
      gr.enable = True 
      gr.addr_threshold = 6092
      gr.accum1_start = 0
      gr.accum2_start = 12
      gr.accum3_start = 12
      gr.accum4_start = 12
      gr.accum5_start = 12
      gr.accum6_start = 72
      gr.accum1_window = 12
      gr.accum2_window = 20
      gr.accum3_window = 30
      gr.accum4_window = 40
      gr.accum5_window = 60 
      gr.accum6_window = 30 
      gr.gate_window = 1040 
      gr.gate_coinc_window = 0
      gr.delay = 90
      gr.sum_trig.enable = 1
      gr.sum_trig.cfd_ena = 3
      gr.sum_trig.threshold = threshold 
      gr.sum_trig.high_suppress_ena = 1
      gr.sum_trig.high_threshold = high_threshold 
      gr.sum_trig.out_pulse_length = 4
      gr.sum_trig.maw_gap_time = 4
      gr.sum_trig.maw_peaking_time = 8
      gr.raw_window = 128
      gr.maw_delay = 0
      gr.maw_window = 128

  # All finished
  dev.close()
  dev.__del__()
  
if __name__ == '__main__':
  args=parser()
  setup(args.host, args.port, args.debug)

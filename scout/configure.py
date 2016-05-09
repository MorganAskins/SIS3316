#!/usr/bin/env python2

import sys, os
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import sis3316

def aparser():
  parser = argparse.ArgumentParser()
  parser.add_argument('host', type=str,
      help="SIS3316 IP Address")
  parser.add_argument('-p', '--port', type=int, default=3333,
      help="SIS3316 Host port, default 3333")
  parser.add_argment('--debug', action='store_true',
      help="Turn debug verbosity on")
  parser.add_argument('-t', '--time', type=int, default=-1,
      help="Collection time for the DAQ in seconds. -1 for infinite")
  return parser.parse_args()

class adc_conf():
  '''
  Configuration of the sis3316
  '''
  def __init__(self, host, port):
    self.configurables = {}
    self.dev = sis3316.Sis3316_udp(host, port)

  def set_configurables(configurables):
    self.configurables = configurables

  def write_conf(self):
    self.dev.open()
    self.dev.reset()
    self.dev.configure()

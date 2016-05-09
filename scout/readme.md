SCOUT
=====

Scout is an alpha/beta coincidence counter consisting
of 4-channels read simultaneously on a single trigger.
The trigger is the sum of channels 1-4, and reads full
waveforms for all channels to store in data.

Tools
-----
The following tools are written specifically for this
application of the sis3316 daq.

- Connection creator: Establish the network interface
  with the sis3316. Runs in two modes: one-shot, and
  monitoring daemon.
- Configure:  Read/write sis3316 configuration, and
  store/recall this information in a config file.
- DAQ: Start/stop acquisition and save in a raw data file.
  This data file will contain run information and config
  settings in its header
- Builder: First pass, organize data in Tree/Event structure,
  in a custom binary file (data.data => data.scout)
- Viewer: Display single event information from a data.scout
  file
- Analysis: Event classifier (alpha/beta), integrator,
  simplified data output, plots, etc.
- Control Gui: Imports all of the above applications and
  provides the user with a simple interface to run the
  detector.

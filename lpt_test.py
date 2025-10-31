#!/usr/bin/env python3
"""
Test TTL pulse timing.
Recording timing can be tested with lpt_timing.py
"""
from subprocess import run
from psychopy import core, parallel

# do we actually use the parallel port? or just testing?
ports = {
        'eegtask': "/dev/parport0", # 2025-10-31 - linux eeg
        "xxx": 53264 # 2025-10 - win11
        }
#host = os.environ.get("HOSTNAME","")
host = run("hostname", capture_output=True).stdout.decode().strip()
port = ports.get(host, None)
pp = None
if port:
    pp = parallel.ParallelPort(address=port)
    print(f"# Using port {port} on  host '{host}'")
else:
    print(f"# Warning: host '{host}' does not have an assocated port. printing only")


def ttl(val, wait=0.100):
    """Send trigger value to parallel port then clear pins.
    @param val   value to send between 1 and 255
    @param wait  time in seconds to wait before clearing pins (ttl=0)"""
    if not pp:
        #print(f"{core.getTime():02.04f}\t{val}, wait {wait}")
        print(f"# TTL {val} not sent, waiting {wait}")
        core.wait(wait)
        return

    pp.setData(val)
    core.wait(wait)
    pp.setData(0) # reset pins, get ready for next trigger


ttl(128, 0.050) # trigger start recording, zero'ed after 50ms

interval = core.StaticPeriod()
dur = 0.500
interval.start(dur)
for _ in range(15):
    interval.complete()   # wait for whatever's left
    interval.start(dur)   # start new interval
    ttl(100)              # send trigger (note, interval already started)
    print(f"{core.getTime():02.04f}\t100")

ttl(129, 0.050) # stop recording

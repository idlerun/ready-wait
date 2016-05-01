#!/usr/bin/env python3

import yaml
import socket as sk
import httplib2
import time
import logging
from logging import warning, debug, info, error

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)

with open("/etc/ready_wait.yaml", "r") as f:
  conf = yaml.load(f.read())

def wait_for_tcp(host, port):
  addr = "TCP %s:%d" % (host, port)
  secs = 0
  info("Waiting for %s" % addr)
  while(1):
    if secs > 0:
      time.sleep(1)
    secs = secs + 1
    if secs % 10 == 0:
      debug("...waiting for %s" % addr)

    try:
      s = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
      result = s.connect_ex((host, port))
      s.close()
      if result == 0:
        info("%s ready!" % addr)
        break
    except KeyboardInterrupt:
      raise
    except:
      continue

def wait_for_http(host, port, uri, status, contains):
  addr = "http://%s:%d%s" % (host, port, uri)
  secs = 0
  info("Waiting for %s (status=%s, contains='%s')" % (addr, status, contains))
  fail_reason = ""
  while(1):
    if secs > 0:
      time.sleep(1)
    secs = secs + 1
    if secs % 10 == 0:
      debug("...waiting for %s (status=%s, contains='%s'), fail_reason='%s'" % (addr, status, contains, fail_reason))
    try:
      resp, content = httplib2.Http().request(addr, "GET")
      if status is not None:
        if int(resp['status']) != status:
          fail_reason = "status=%s" % resp['status']
          continue
      if contains is not None:
        content_str = content.decode('ascii')
        if not contains in content_str:
          fail_reason = "content=%s" % content_str.replace('\n','\\n')
          continue
      info("%s ready!" % addr)
      break
    except KeyboardInterrupt:
      raise
    except httplib2.ServerNotFoundError:
      fail_reason = "ServerNotFoundError"
      continue
    except ConnectionRefusedError:
      fail_reason = "ConnectionRefusedError"
      continue
  
for host in conf:
  reqs = conf[host]
  if "tcp" in reqs:
    port = int(reqs["tcp"].get("port", "80"))
    wait_for_tcp(host, port)
  elif "http" in reqs:
    port = int(reqs["http"].get("port", "80"))
    uri = reqs["http"].get("uri", "/")
    status = int(reqs["http"].get("status", None))
    contains = reqs["http"].get("contains", None)
    wait_for_http(host,port,uri,status,contains)

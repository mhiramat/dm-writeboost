"""
lc_daemon.py

Copyright (C) 2012-2013 Akira Hayakawa <ruby.wktk@gmail.com>
"""

from __future__ import with_statement
from daemon import DaemonContext

from daemon.pidfile import PIDLockFile
# or
#from daemon.pidfile import PIDLockFile

import time
import psutil

import dirnode
import lc_common_tools as tools

dc = DaemonContext(
		pidfile = PIDLockFile('/tmp/lc_daemon.pid'),
		stdout  = open('/var/log/lc_daemon_out.log', 'w'),
		stderr  = open('/var/log/lc_daemon_err.log', 'w+'))
				
class Daemon:
	
	def __init__(self):
		t = tools.table()
			
	def update_migrate_state(self, cache_id):
		cache = tools.Cache(cache_id)
		intvl = int(cache.update_interval)
		t = int(time.time())	
		
		if (t % intvl):
			return
			
		b = True
		for device_id in self.t[cache_id]:
			device = tools.Device(device_id)
			
			device.backing.update(intvl)
			
			thes = int(device.migrate_threshold)
			if device.backing.util > thes:
				b = False
				
		if int(cache.lc_node.force_migrate):
			b = True
				
		if b:		
			cache.lc_node.allow_migrate = 1
		else:
			cache.lc_node.allow_migrate = 0

	def modulate_migration(self):
		for cache_id in self.t.keys():		
			update_migrate_state(cache_id)

	def should_flush_buffer(self, cache):
		t = int(time.time())
		intvl = int(cache.lc_node.flush_current_buffer_interval)
		if not intvl:
			return False

		if(t % intvl):
			return False

		current_val = int(cache.lc_node.last_flushed_segment_id)
		b = (current_val == cache.last_flushed_segment_id)
		cache.last_flushed_segment_id = current_val
		return b

	def flush_buffer_periodically(self):
		for cache_id in self.t.keys():
			cache = tools.Cache(cache_id)
			if not should_flush_buffer(cache):
				continue
			cache.lc_node.flush_current_buffer = 1
		return

	def should_commit_super_block(self, cache):
		t = int(time.time())
		intvl = int(cache.lc_node.commit_super_block_interval)
		if not intvl:
			return False

		if(t % intvl):
			return False

		return True

	def commit_super_block_periodically(self):
		for cache_id in self.t.keys():
			cache = tools.Cache(cache_id)
			if not should_commit_super_block(cache):
				continue
			cache.lc_node.commit_super_block = 1
		return

	def loop(self):
		while True:
			modulate_migration()
			flush_buffer_periodically()
			commit_super_block_periodically()
			
			time.sleep(1)

def run_lc_daemon():
	context = Daemon()
	context.loop()

with dc:
	run_lc_daemon()

# -*- coding: utf-8 -*-

# Copyright (c) 2012 Wu Tangsheng(lanbaba) <wuts73@gmail.com>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
	
import os, sys, threading, logging
from Queue import *
from ossync.lib import queue_model
from ossync.lib import helper
try:
	import pyinotify
except ImportError as e:
	print e.message
	exit(0)

class EventHandler(pyinotify.ProcessEvent):
	"""事件处理"""
	
	def __init__(self, monitered_dir, queue, bucket):
		self.monitered_dir = monitered_dir
		self.queue = queue
		self.bucket = bucket 
		self.logger =  logging.getLogger('app')
		dbpath =  'db/ossync.db'
		self.qm = queue_model.QueueModel(dbpath)
	
	def process_IN_CREATE(self, event):
		self.process_event(event, 'CREATE')
		
	def process_IN_DELETE(self, event):
		self.process_event(event, 'DELETE')
		
	def process_IN_MODIFY(self, event):
		self.process_event(event, 'MODIFY')
		
	def process_IN_MOVED_FROM(self, event):
		self.logger.info("Moved from file: %s "  %   os.path.join(event.path, event.name))
		self.process_event(event, 'DELETE')
	
	def process_IN_MOVED_TO(self, event):
		self.logger.info("Moved to file: %s "  %   os.path.join(event.path, event.name)) 
		realpath = os.path.join(event.path, event.name)
		if event.dir:
			self.queue_dir(realpath)
		self.process_event(event, 'CREATE')
		
	def process_event(self, event, action):
		if len(action) == 0:
			return False
		realpath = os.path.join(event.path, event.name)
		relpath = os.path.relpath(realpath, self.monitered_dir)
		if action == 'DELETE':
			if event.dir:
				relpath += '/'
		self.logger.info(action.title() + " file: %s " % realpath)
		#print   "Modify file: %s "  %   os.path.join(event.path, event.name)
		el = self.bucket  + '::' + self.monitered_dir + '::' + relpath + '::' + action[0] 
		self.save_el(self.monitered_dir, relpath, self.bucket, action[0])
		self.queue_el(el)
		
	def queue_dir(self, queue_path):
		files = list(helper.walk_files(queue_path, yield_folders = True))
		if len(files) > 0:
			for path in files:
				relpath = os.path.relpath(path, self.monitered_dir)
				self.save_el(self.monitered_dir, relpath, self.bucket,'C')
				el = self.bucket  + '::' + self.monitered_dir + '::' + relpath + '::' + 'C' 
				self.queue_el(el)
	
	def save_el(self, root, relpath, bucket, action):
		hashcode = helper.calc_el_md5(root, relpath, bucket)
		self.qm.open()
		if self.is_el_existed(hashcode):
			self.qm.update_action(hashcode, action)
			self.qm.update_status(hashcode, 0)
		else:
			data={"root": root, "relpath": relpath, "bucket": bucket, "action": action, "status":  0, "retries": 0}
			self.qm.save(data)
		self.qm.close()
		
	def is_el_existed(self, hashcode):
		row = self.qm.get(hashcode)
		if row:
			return True
		return False
		
	
	def queue_el(self, el):
		'''el: element of queue , formated as "bucket::root::path::C|M|D"
		   C means CREATE, M means MODIFY, D means DELETE
		'''
		try:
			self.queue.put(el, block = True, timeout = 1)
			msg = 'queue element:' + el
			#print msg
			self.logger.info(msg)
		except Full as e:
			#print e
			self.logger.error(e.message)

class InotifyThread(threading.Thread):
	def __init__(self, bucket, root, queue, *args, **kwargs):
		threading.Thread.__init__(self, *args, **kwargs) 
		self.bucket = bucket
		self.queue = queue
		self.root = root
		self.logger =  logging.getLogger('app')
		self._terminate = False

	def terminate(self):
		self._terminate = True
		self.notify.stop()
	
	def start_notify(self, monitered_dir):
		wm = pyinotify.WatchManager()
		mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY | pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO
		self.notifier = pyinotify.Notifier(wm, EventHandler(monitered_dir, self.queue, self.bucket), timeout = 10)
		wm.add_watch(monitered_dir, mask, rec = True, auto_add = True) 
		self.logger.info('now starting monitor %s'%(monitered_dir)) 
		# self.notifier.loop()
		while True:
			if self._terminate:
				break
			self.notifier.process_events()
			if self.notifier.check_events():
				self.notifier.read_events()
		
	def run(self):
		self.start_notify(self.root)
		return
		
if __name__ == '__main__': 
	queue = Queue()
	root = '.'
	bucket = 'dzdata'
	logger = logging.getLogger('app')
	logger.setLevel(logging.INFO)
	logger.addHandler(logging.FileHandler('logs/app.log'))
	inotifythd = InotifyThread(bucket, root, queue)
	inotifythd.start()
		
		
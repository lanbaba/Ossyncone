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

import os, threading, logging
import os.path
from Queue import *
import hashlib
from ossync.lib import helper
from ossync.lib import queue_model

class QueueThread(threading.Thread):
	
	""" 此线程的作用是将bucket,root, path压入要上传的队列，队列元素格式：
	   "bucket::root::relpath::action::life"
	   其中action表示文件是新建还是修改还是删除;life表示重入次数
	"""
	def __init__(self, oss_mappers, queue, *args, **kwargs):
		threading.Thread.__init__(self, *args, **kwargs)
		self.oss_mappers = oss_mappers
		self.queue = queue
		self._terminate = False
		self.logger =  logging.getLogger('app')
		dbpath =  'db/ossync.db'
		self.qm = queue_model.QueueModel(dbpath) 
		
	def terminate(self):
		self._terminate = True
	
	def queue_folders(self, bucket, folders):
		"""将目录中的文件解析成队列元素并压入队列"""
		files = {}
		elements = []
		for d in folders:
			files[d] = list(helper.walk_files(os.path.normpath(d), yield_folders = True))
			if len(files) > 0:
				for k in files:
					if len(files[k]) > 0:
						for path in files[k]:
							self.queue_el(bucket, k, path)
	
	def queue_el(self, bucket, root, path):
		"""根据bucket和root以及路径生成队列元素"""
		relpath = os.path.relpath(path, root) # 相对于root的相对路径 
		el = bucket + '::' + root + '::' + relpath + '::C'
		hashcode = helper.calc_el_md5(root, relpath, bucket)
		if not self.is_el_queued(hashcode): 
			data={"root": root, "relpath": relpath, "bucket": bucket, "action": 'C', "status":  0, "retries" : 0}
			self.qm.save(data)
			try:
				self.queue.put(el, block = True, timeout = 1)
				msg = 'queue element:' + el
				#print msg
				self.logger.info(msg)
			except Full as e:
				self.logger.error(e.message) 
	
		
	def is_el_queued(self, hashcode):
		row = self.qm.get(hashcode)
		if row:
			return True
		return False
	
	def run(self):
		if self.oss_mappers == None or len(self.oss_mappers) == 0:
			self.queue.put(None)
			return
		self.qm.open()
		for oss_mapper in self.oss_mappers:
			bucket = oss_mapper['bucket']
			local_folders = oss_mapper['local_folders']
			if(len(bucket) > 0 and len(local_folders) > 0):
				self.queue_folders(bucket, local_folders)
		self.qm.close()
		self.queue.put(None)
		#self.queue.join()
		return
		
			
					
			
		
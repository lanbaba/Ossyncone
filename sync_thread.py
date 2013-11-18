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

import os, sys, threading
import logging
import hashlib
from Queue import *
from ossync.lib import queue_model
from ossync.lib import helper
import time
try:
    from ossync.sdk.oss_api import *
except:
    from ossync.oss_api import *
try:
    from ossync.sdk.oss_xml_handler import *
except:
    from ossync.oss_xml_handler import *
from config.setting import *

LARGE_FILE_SIZE = 5000000 # File larege than 2M will be depart small parts

class SyncThread(threading.Thread):
	def __init__(self, oss, queue, *args, **kwargs):
		threading.Thread.__init__(self, *args, **kwargs)
		self.queue = queue
		self.oss = oss
		self._terminate = False
		self.logger =  logging.getLogger('app')
		dbpath =  'db/ossync.db'
		self.qm = queue_model.QueueModel(dbpath)
        
		
	def terminate(self):
		self._terminate = True
		
	def upload(self, bucket, oss_obj_name, filename):
		if not os.path.lexists(filename):
			return None
		success = False
		if(os.path.isdir(filename)):
			oss_obj_name += '/'
			res = self.oss.put_object_with_data(bucket = bucket, object = oss_obj_name, input_content = '')
			if (res.status / 100) == 2:
				success = True
		else:
			file_size = os.path.getsize(filename)
			if file_size > LARGE_FILE_SIZE:
				is_large_file = True    
				res = self.oss.upload_large_file(bucket = bucket, object = oss_obj_name, filename = filename)
			else:
				is_large_file = False
				res = self.oss.put_object_from_file(bucket = bucket, object = oss_obj_name, filename = filename)
			filehash = helper.calc_file_md5(filename) 
			header_map = convert_header2map(res.getheaders())
			etag = safe_get_element("etag", header_map).upper().replace('"', '')
			if (res.status / 100) == 2:
				if is_large_file == False:
					if filehash.upper() == etag:
						success = True
					else:
						success = False
				else:
					success = True
		return success
		
	def exists_oss_object(self, bucket, oss_obj_name):
		headers = {}
		res = self.oss.head_object(bucket, oss_obj_name, headers)
		if (res.status / 100) == 2:
			return True
		else:
			return False
	
	def walk_bucket(self, bucket, prefix, marker, delimiter, maxkeys, headers, result = []):
		res = self.oss.get_bucket(bucket, prefix, marker, delimiter, maxkeys, headers)
		if (res.status / 100) == 2:
			body = res.read()
			h = GetBucketXml(body)
			(file_list, common_list) = h.list() 
			if len(file_list) > 0:
				for item in file_list:
					result.append(item[0])
			if len(common_list) > 0: 
				for path in common_list:
					result.append(path)
					self.walk_bucket(bucket, path, marker, delimiter, maxkeys, headers, result)

	def delete_oss_object(self, bucket, oss_obj_name):
		headers = {}
		res = self.oss.delete_object(bucket, oss_obj_name, headers)
		if (res.status / 100) == 2:
			return True
		else:
			return False
		
	def delete_oss_objects(self, bucket, oss_obj_name):
		headers = {}
		result = []
		marker = ''
		delimiter = '/'
		maxkeys = 100
		self.walk_bucket(bucket, oss_obj_name, marker, delimiter, maxkeys, headers, result)
		if len(result) > 0:
			for item in result:
				self.oss.delete_object(bucket, item, headers)
		else:
			self.oss.delete_object(bucket, oss_obj_name, headers)
		return True
			
	def queue_el(self, el):
		'''el: element of queue , formated as "bucket::root::path"'''
		try:
			self.queue.put(el, block = True, timeout = 1)
			msg = 'requeue element:' + el 
			self.logger.info(msg)
		except Full as e:
			self.logger.error(e.message)
			print e
	
	def is_el_processed(self, hashcode):
		row = self.qm.get(hashcode)
		if row and str(row['status']) == '1':
			return True
		return False
		
	def run(self):
		self.logger.info('Now starting sync thread ...')
		self.qm.open()
		while True:
			if self._terminate:
				break
			item = self.queue.get()
			if item is None:
				break 
			(bucket, root, relpath, action) = item.split('::')
			if len(bucket) > 0 and len(root) > 0 and len(relpath) > 0 and len(action) > 0:
				hashcode = helper.calc_el_md5(root, relpath, bucket)
				if not self.is_el_processed(hashcode):
					oss_obj_name = os.path.join(os.path.basename(root), relpath)
					if len(oss_obj_name) > 0:
						if(action == 'M' or action == 'C'): 
							success = self.upload(bucket, oss_obj_name, os.path.join(root, relpath)) 
							msg = 'put object ' + oss_obj_name + ' to bucket ' + bucket
						if(action == 'D'): 
							success = self.delete_oss_objects(bucket, oss_obj_name)
							msg = 'delete object '  + oss_obj_name + ' of bucket ' + bucket
						if success: 
							msg += ' success'
							self.logger.info(msg)
							self.qm.update_status(hashcode, 1)
						else:
							if success == False:
								msg += ' failure'  
								self.logger.error(msg)
								"""requeue losing element"""
								row = self.qm.get(hashcode)
								if row:
									retries = int(row['retries'] )
									if retries < MAX_RETRIES:
										self.queue_el(item)
										self.qm.update_retries(hashcode, retries + 1)
									else:
										self.logger.critical(msg + ' exceed max retries')
							else:
								self.logger.critical(msg + ' failure, resource may not exists.')
								pass
		self.qm.close()
		self.queue.task_done()
		return
		
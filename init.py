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

import sys
import os
import os.path
from config.setting import *
from ossync.lib import queue_model
import logging
import logging.handlers
import time
try:
    from ossync.sdk.oss_api import *
except:
    from ossync.oss_api import *

def set_sys_to_utf8():
	reload(sys)
	sys.setdefaultencoding('utf-8')

def get_logger():
	LOG_FILENAME = 'logs/app.log'
	format = logging.Formatter("%(levelname)-10s %(asctime)s %(message)s")
	logging.basicConfig(level = logging.INFO) 
	logger = logging.getLogger('app')
	handler1 = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes = MAX_LOGFILE_SIZE, backupCount = MAX_BACKUP_COUNT)
	handler2 = logging.StreamHandler(sys.stdout)
	handler1.setFormatter(format)
	handler2.setFormatter(format)
	logger.addHandler(handler1)
	# logger.addHandler(handler2)
	return logger
	
def check_config(logger): 
	if len(HOST) == 0 or len(ACCESS_ID) == 0 or len(SECRET_ACCESS_KEY) == 0:
		msg = "Please set HOST and ACCESS_ID and SECRET_ACCESS_KEY"
		#print msg
		logger.critical(msg)
		exit(0)
	if len(oss_mappers) == 0:
		msg = "please set OSS Mappers"
		#print msg
		logger.critical(msg)
		exit(0)
	oss = OssAPI(HOST, ACCESS_ID, SECRET_ACCESS_KEY)
	for oss_mapper in oss_mappers:
		bucket = oss_mapper['bucket']
		acl = ''
		headers = {}
		res = oss.create_bucket(bucket, acl, headers) 
		if (res.status / 100) != 2:
			msg = "Bucket: " + bucket + " is not existed or create bucket failure, please rename your bucket."
			#print msg
			logger.critical(msg)
			exit(0)
		local_folders = oss_mapper['local_folders']
		if len(local_folders) > 0:
			for folder in local_folders:
				if not os.path.exists(folder) or not os.path.isdir(folder):
					msg = "Local folder: " + folder + " is not existed or is not a direcotry.Please check you setting."
					#print msg
					logger.critical(msg)
					exit(0)
		else:
			msg = "please at least set one local folder for each bucket"
			#print msg
			logger.critical(msg)
			exit(0)

def queue_unprocessed(queue, logger):
	dbpath =  'db/ossync.db'
	qm = queue_model.QueueModel(dbpath)
	qm.open()
	items = qm.find_all(status = 0)
	if items:
		for item in items:
			if int(item['retries']) < MAX_RETRIES:
				el = item['bucket'] + '::' + item['root'] + '::' + item['relpath'] +  '::' + item['action']
				queue.put(el, block = True, timeout = 1)
				msg = 'queue unprocessed element:' + el 
				logger.info(msg)
	qm.close()
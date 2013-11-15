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

import os, threading
from Queue import *
from ossync.sdk.oss_api import *
from queue_thread import QueueThread
from sync_thread import SyncThread
from inotify_thread import InotifyThread
from init import *

if __name__ == '__main__':
	try:
		set_sys_to_utf8()
		logger = get_logger()
		check_config(logger)
		queue = Queue()
		# check unprocessed items, if exists queue them
		queue_unprocessed(queue, logger)
		oss = OssAPI(HOST, ACCESS_ID, SECRET_ACCESS_KEY)
		
		syncthd = SyncThread(oss, queue)
		syncthd.start() 
		
		queuethd = QueueThread(oss_mappers, queue)
		queuethd.start()
	except KeyboardInterrupt as e:
		for thd in threading.enumerate():
			if thd is main_thread:
				continue
			else:
				thd.terminate()
		logger.error(msg)
		#print e.message()
		exit(0)
			
		
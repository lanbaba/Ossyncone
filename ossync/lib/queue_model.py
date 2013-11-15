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

import sqlite3, md5
import itertools
import hashlib

class QueueModel(object):
	def __init__(self, dbpath):
		self.dbpath = dbpath
	
	def open(self):
		self.conn = sqlite3.connect(self.dbpath)
		self.conn.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
		self.cursor = self.conn.cursor()
		
	def close(self):
		self.cursor.close()
		self.conn.close() 
	
	def save(self, data={"root": '', "relpath": '', "bucket": '', "action": '', "status":  0, "retries": 0}):
		if(len(data) == 0):
			return False
		m = hashlib.md5()
		m.update(data['root'] + data['relpath'] + data['bucket'])
		hashcode = m.hexdigest()
		self.cursor.execute('insert into queue values(?, ?, ?, ?, ?, ?, ?)', (data['root'], data['relpath'], data['bucket'], data['action'], data['status'], hashcode, data['retries']))
		self.conn.commit()
		
	def get(self, hashcode):
		self.cursor.execute('select * from queue where hashcode=?', (hashcode, ))
		result = self._map_fields(self.cursor)
		if len(result) > 0:
			return result[0]
		return None
		
	def find_all(self, status): 
		self.cursor.execute('select * from queue where status=?', (status, ))
		result = self._map_fields(self.cursor)
		if len(result) > 0:
			return result
		return None
			
	def update_status(self, hashcode, status):
		self.cursor.execute('update queue set status=? where hashcode=?', (status, hashcode))
		self.conn.commit()
	
	def update_action(self, hashcode, action):
		self.cursor.execute('update queue set action=? where hashcode=?', (action, hashcode))
		self.conn.commit()
		
	def update_retries(self, hashcode, retries):
		self.cursor.execute('update queue set retries=? where hashcode=?', (retries, hashcode))
		self.conn.commit()
		
	def delete(self, hashcode):
		self.cursor.execute('delete from queue where hashcode=?', (hashcode,))
		self.conn.commit()
		
	def _map_fields(self, cursor):
		"""将结果元组映射到命名字段中"""
		filednames = [d[0].lower() for d in cursor.description]
		result = []
		while True:
			rows = cursor.fetchmany()
			if not rows:
				break
			for row in rows:
				result.append(dict(itertools.izip(filednames, row)))
		return result
				
		
	
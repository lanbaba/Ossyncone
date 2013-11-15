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

import os
import sys

# check if python version >= 2.6 and < 3.0
if sys.version_info < (2, 6):
	sys.stderr.write("Sorry, OSSync requires at least Python 2.6\n")
	sys.exit(0)
if sys.version_info >= (3, 0):
	sys.stderr.write("Sorry, Python 3.0+ is unsupported at present。\n")
	sys.exit(0)

# check if linux kernel supports inotify
if not os.path.exists("/proc/sys/fs/inotify"):
	sys.stderr.write("Sorry, your linux kernel doesn't support inotify。\n")
	sys.exit(0)

print "Start to install necessary modules ..."
# check if pip has been installed
excode = os.system("pip --version")
if excode > 0:
	# try to install pip
	os.system("sudo curl http://python-distribute.org/distribute_setup.py | python")
	os.system("curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python")
	# clean temp files
	os.system("rm -f distribute*.tar.gz")

# try to install pyinotify
os.system("sudo pip install pyinotify")

# check if pyinotify has been installed
try:
	import pyinotify
	print "Installation complete successfully!" 
except ImportError as e:
	sys.stderr.write("Sorry, Installation pyinotify module failure! Please try to install it manually。\n")
	sys.exit(0)


	

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

# OSS 连接参数
####################
# OSS              #
####################

HOST = "oss.aliyuncs.com"
ACCESS_ID = ""
SECRET_ACCESS_KEY = ""

# OSS Bucket和本地目录同步映射关系，一个Bucket对应一个或多个本地目录(local_folder)。
# 可以定义多个bucket。示例：
# oss_mappers = [{'bucket': 'dzdata', 'local_folders': ['/root/testdata/audios', '/root/testdata/docs']},
# {'bucket': 'privdata', 'local_folders': ['/root/testdata/images', '/root/testdata/pdfs']}]
####################
# OSS MAP          #
####################
oss_mappers = [{'bucket': 'dzdata', 'local_folders': ['/root/testdata/audios', '/root/testdata/docs']}]

# 日志选项
####################
# LOGGING SETTING  #
####################
LOGFILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../", "logs/app.log")
MAX_LOGFILE_SIZE = 104857600 # 默认日志文件大小为100M，每次达大小限制时，会自动加后缀生成备份文件
MAX_BACKUP_COUNT = 5 # 默认备份文件为5个

# 上传文件或者删除object的最大重试次数
####################
# MAX_RETRIES      #
####################
MAX_RETRIES = 10

# 上传文件线程数
####################
# MAX_RETRIES      #
####################
NTHREADS = 5

# 数据库路径
####################
# DB PATH          #
####################
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../", "db/ossync.db")

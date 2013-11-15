# -*- coding: utf-8 -*-

# OSS 连接参数
####################
# OSS              #
####################

HOST = "oss.aliyuncs.com"
ACCESS_ID = "myid"
SECRET_ACCESS_KEY = "mykey"

# OSS Bucket和本地目录同步映射关系，一个Bucket对应一个或多个本地目录(local_folder)。
# 可以定义多个bucket。示例：
#oss_mappers = [{'bucket': 'dzdata', 'local_folders': ['/root/testdata/audios', '/root/testdata/docs']},{'bucket': 'privdata', 'local_folders': ['/root/testdata/images', '/root/testdata/pdfs']}]
####################
# OSS MAP          #
####################
oss_mappers = [{'bucket': 'mybucket', 'local_folders': ['/path/to/localfolder']}]

# 日志选项
####################
# LOGGING SETTING  #
####################
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

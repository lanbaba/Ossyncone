# Ossync修改版

Ossync是一款开源的、基于inotify机制的阿里云同步上载工具，采用Python开发。License : [MIT](http://rem.mit-license.org/).这个版本是在实时同步版基础上修改的，只是实现增量备份，没用采用Inotify机制。每次备份完毕自动退出，下次启动会自动备份新增或修改的内容。建议用crobtab设置一个定时器，比如定时在凌晨三点启动。

## 主要特色
     
  * **可以一次同步多个本地文件夹和多个bucket** - 只要定义好本地文件夹和bucket的映射关系，可以同时将多个本地文件夹同步到多个bucket.
  * **基于消息队列的多线程快速同步** - 采用消息队列和多线程机制，实现快速同步.
  * **安全准确同步** - 文件上传校验和失败重传确保文件完整同步。

## 安装
将本程序解压到任意目录, 并进入该目录，运行：

 		sudo python setup.py
 		
如果提示：“Installation complete successfully!”，表明安装成功。否则，请检查是否满足以下条件并手动安装pyinotify模块。

* Python版本大于2.6(建议使用python2.7, 暂不支持python3)
* 检查和系统是否有/proc/sys/fs/inotify/目录，以确定内核是否支持inotify，即linux内核版本号大于2.6.13。
* 安装pyinotify模块，[https://github.com/seb-m/pyinotify](https://github.com/seb-m/pyinotify)。

   
## 运行
 * 在config目录下进行相应配置，请参考配置文件中的说明文字.
 * 在程序根目录下运行:
 
 		nohup python ossync.py >/dev/null 2>&1 &
 
## 定时备份
 * 以凌晨三点启动备份为例， 运行： 
 
 		crontab -e
 	
 * 增加一行： 0 3 * * * nohup python ~/ossyncone/ossync.py &
 * 保存退出。
  		
**注：请查看logs目录下的日志文件以了解系统运行状况。**


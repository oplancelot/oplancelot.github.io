---
layout: post
title: speed up mapped efs share in windows 
description: samba-efs-sys_get_nfs4_quota()调查
category: posts
tags: samba efs 
draft: false
mermaid: false

---
### 1.背景
AWS efs mount 在linux ，linux 搭建 samba服务，提供给win server 访问。

使用windows ec2 直接访问 samba服务，有时文件打开会有延迟，这个例子是延迟了两分钟。

XXX程序需要重试一次move文件才成功，查看samba日志发现从写文件开始到写文件结束，经过了2分钟。

```
[2021/12/22 00:09:41.639667,  2] ../../source3/smbd/open.c:1447(open_file)
XXXXX opened file XXXXX.xml read=No write=Yes (numopen=1)
[2021/12/22 00:11:41.709831,  3] ../../source3/smbd/smb2_write.c:215(smb2_write_complete_internal)
  smb2: fnum 1302514779, file XXXXX.xml, length=6143 offset=0 wrote=6143
```

中间有多次sys_get_nfs4_quota()的报错。 尝试带入的参数1、3、4都是失败了，只有2成功，但是却又提示“sys_get_nfs4_quota() failed for mntpath[/mnt/efs] bdev[xxxx.xxxx.amazonaws.com:/] qtype[1] id[-1]: Function not implemented”

```
[2021/12/22 00:09:41.639667,  2] ../../source3/smbd/open.c:1447(open_file)
XXXXX opened file XXXXX.xml read=No write=Yes (numopen=1)
[2021/12/22 00:09:41.647973,  3] ../../source3/smbd/smb2_server.c:3213(smbd_smb2_request_error_ex)
  smbd_smb2_request_error_ex: smbd_smb2_request_error_ex: idx[1] status[NT_STATUS_FILE_IS_A_DIRECTORY] || at ../../source3/smbd/smb2_create.c:296
[2021/12/22 00:09:41.649989,  3] ../../source3/smbd/trans2.c:3460(smbd_do_qfsinfo)
  smbd_do_qfsinfo: level = 1007
[2021/12/22 00:09:41.650418,  3] ../../source3/lib/sysquotas_nfs.c:141(sys_get_nfs_quota)
  sys_get_nfs_quota: got unsupported quota type '1', only supported type is '2' (SMB_USER_QUOTA_TYPE)
[2021/12/22 00:09:41.650430,  3] ../../source3/lib/sysquotas.c:561(sys_get_quota)
  sys_get_nfs4_quota() failed for mntpath[/mnt/efs] bdev[xxx.xxxx.amazonaws.com:/] qtype[1] id[-1]: Function not implemented.
[2021/12/22 00:10:41.654095,  3] ../../source3/lib/sysquotas.c:561(sys_get_quota)
  sys_get_nfs4_quota() failed for mntpath[/mnt/efs] bdev[xxx.xxxx.amazonaws.com:/] qtype[2] id[99]: Permission denied.
[2021/12/22 00:10:41.655302,  3] ../../source3/lib/sysquotas_nfs.c:141(sys_get_nfs_quota)
  sys_get_nfs_quota: got unsupported quota type '3', only supported type is '2' (SMB_USER_QUOTA_TYPE)
[2021/12/22 00:10:41.655315,  3] ../../source3/lib/sysquotas.c:561(sys_get_quota)
  sys_get_nfs4_quota() failed for mntpath[/mnt/efs] bdev[xxx.xxxx.amazonaws.com:/] qtype[3] id[-1]: Function not implemented.
[2021/12/22 00:10:41.655383,  3] ../../source3/lib/sysquotas_nfs.c:141(sys_get_nfs_quota)
  sys_get_nfs_quota: got unsupported quota type '4', only supported type is '2' (SMB_USER_QUOTA_TYPE)
[2021/12/22 00:10:41.655390,  3] ../../source3/lib/sysquotas.c:561(sys_get_quota)
  sys_get_nfs4_quota() failed for mntpath[/mnt/efs] bdev[xxx.xxxx.amazonaws.com:/] qtype[4] id[99]: Function not implemented.
```

调查sys_get_nfs4_quota()

函数原代码是

https://download.samba.org/pub/unpacked/samba_master/source3/lib/sysquotas.c

https://download.samba.org/pub/unpacked/samba_master/source3/lib/sysquotas_nfs.c



### 2.解决方案如下

We had similar issues and found a solution for it. We were able to narrow the issue down to SAMBA failing to report EFS size in time. More specifically, samba fails to execute sys_get_nfs4_quota(), timing out in about 60 sec.

To overcome this issue, we added a custom script to samba to report 8 Exabytes instantly without trying to calculate the size. Given that this is unlimited EFS (in theory), the reported size does not matter, and returning fixed number is ok. That solves the 60 sec timeout.

To do this, create a file in /etc/samba/samba-dfree and add the two lines below:

```
#!/bin/bash
echo "8000000000 8000000000"
```

Then in the samba config file, add the following parameters to either global section, or the specific EFS mount section, depending on your needs:

```
dfree command = /etc/samba/samba-dfree
dfree cache time = 60
```

Save the config file. Restart SAMBA and the delay should go away. Hope this helps.

### 3.参考

https://serverfault.com/questions/811957/any-way-to-speed-up-mapped-efs-share-in-windows 英文问答

[WindowsでマップされたEFS共有を高速化する方法はありますか](https://www.webdevqa.jp.net/ja/windows/windows%E3%81%A7%E3%83%9E%E3%83%83%E3%83%97%E3%81%95%E3%82%8C%E3%81%9Fefs%E5%85%B1%E6%9C%89%E3%82%92%E9%AB%98%E9%80%9F%E5%8C%96%E3%81%99%E3%82%8B%E6%96%B9%E6%B3%95%E3%81%AF%E3%81%82%E3%82%8A%E3%81%BE%E3%81%99%E3%81%8B%EF%BC%9F/960035193/)日语问答

 [Bug 13625](https://bugzilla.samba.org/show_bug.cgi?id=13625) - sys_get_nfs4_quota() crippling slow when sharing large NFS e.g. Amazon EFS 

[about dfree](https://github.com/int128/samba-dfree/blob/master/README.md)  github

[dfree original](https://www.samba.org/samba/docs/current/man-html/smb.conf.5.html)官方smb.conf配置文件，参考dfree章节

```
dfree command (S)
The dfree command setting should only be used on systems where a problem occurs with the internal disk space calculations. This has been known to happen with Ultrix, but may occur with other operating systems. The symptom that was seen was an error of "Abort Retry Ignore" at the end of each directory listing.

This setting allows the replacement of the internal routines to calculate the total disk space and amount available with an external routine. The example below gives a possible script that might fulfill this function.

In Samba version 3.0.21 this parameter has been changed to be a per-share parameter, and in addition the parameter dfree cache time was added to allow the output of this script to be cached for systems under heavy load.

The external program will be passed a single parameter indicating a directory in the filesystem being queried. This will typically consist of the string ./. The script should return two integers in ASCII. The first should be the total disk space in blocks, and the second should be the number of available blocks. An optional third return value can give the block size in bytes. The default blocksize is 1024 bytes.

Note: Your script should NOT be setuid or setgid and should be owned by (and writeable only by) root!

Where the script dfree (which must be made executable) could be:

 
#!/bin/sh
df "$1" | tail -1 | awk '{print $(NF-4),$(NF-2)}'
or perhaps (on Sys V based systems):

 
#!/bin/sh
/usr/bin/df -k "$1" | tail -1 | awk '{print $3" "$5}'
Note that you may have to replace the command names with full path names on some systems. Also note the arguments passed into the script should be quoted inside the script in case they contain special characters such as spaces or newlines.

By default internal routines for determining the disk capacity and remaining space will be used.

No default

Example: dfree command = /usr/local/samba/bin/dfree
```

```
dfree cache time (S)
The dfree cache time should only be used on systems where a problem occurs with the internal disk space calculations. This has been known to happen with Ultrix, but may occur with other operating systems. The symptom that was seen was an error of "Abort Retry Ignore" at the end of each directory listing.

This is a new parameter introduced in Samba version 3.0.21. It specifies in seconds the time that smbd will cache the output of a disk free query. If set to zero (the default) no caching is done. This allows a heavily loaded server to prevent rapid spawning of dfree command scripts increasing the load.

By default this parameter is zero, meaning no caching will be done.

No default

Example: dfree cache time = 60
```


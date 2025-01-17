# python 多线程实例-m3u8下载器

使用方式：

`pip install H_m3u8DL`

## 介绍

主要用来多线程下载文件，对m3u8链接进行了 解析、下载、解密、合并、删除等操作

支持windows,mac,linux

支持多种方式调用

### 参数介绍

对于普通用户可直接在控制台使用:

```
hm3u8dl "https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8"
```

```
hm3u8dl "https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8" -key "kQ2aSmyG1FDSmzpqTso/0w==" -title "视频名称"
```

```
	-m3u8url: m3u8链接、文件、文件夹、List
    -title:视频名称
    -base_uri_parse:自定义baseuri
    -threads:线程数
    -key:自定义key
    -iv:自定义iv
    -method:自定义方法 'SAMPLE-AES-CTR', 'cbcs', 'SAMPLE-AES','AES-128','copyrightDRM'
    -work_dir:工作目录
    -headers:自定义请求头
    -enable_del:下载完成后删除多余文件False True
    -merge_mode:合并方法，1:二进制合并 2:二进制合并后再用ffmpeg 转码 3:用ffmpeg 合并
    -proxy:设置代理 {'http':'http://127.0.0.1:8888','https:':'https://127.0.0.1:8888'}
```

其中m3u8url 可为链接、本地m3u8文件路径、文件夹路径、txt 文件（按 name,m3u8url,key  的形式一行一个  ）

专业用户命令介绍如下：

首先从在pycharm 中导入包 `from H_m3u8DL import m3u8download`

#### m3u8url (必填，其余参数全为非必填)

1.可直接输入m3u8链接：

```
m3u8url = 'https://hls.cntv.myhwcdn.cn/asp/hls/2000/0303000a/3/default/363b41f09f6045a4ab95c7df387732bf/2000.m3u8'
 
 m3u8download(m3u8url)
```

2.本地m3u8文件地址：

```
m3u8url = r"C:\Users\happy\Desktop\1.m3u8"
m3u8download(m3u8url=m3u8rul)
```

3.包含m3u8文件的文件夹：

软件会自动扫描该文件夹下所有m3u8文件，并进行下载

```
m3u8url = r"C:\Users\happy\Desktop\"
m3u8download(m3u8url=m3u8rul)
```

4.含有m3u8内容的txt 文件

txt内容如下：

title,m3u8url,key

```
0,https://1252524126.vod2.myqcloud.com/529d8d60vodtransbj1252524126/cbcde1e4387702298833985463/drm/v.f421220.m3u8
1,https://1252524126.vod2.myqcloud.com/529d8d60vodtransbj1252524126/cbcde1e4387702298833985463/drm/v.f421220.m3u8
3,https://1252524126.vod2.myqcloud.com/529d8d60vodtransbj1252524126/cbcde1e4387702298833985463/drm/v.f421220.m3u8
```

```
m3u8url = r"C:\Users\happy\Desktop\1.txt"
m3u8download(m3u8url=m3u8rul)
```

#### title  

自定义视频名称

#### threads

线程数，默认16

#### key

视频解密时key，支持base64,hex格式，支持链接形式，支持本地文件链接形式

base64: 

```
m3u8download(m3u8url='https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8',key='kQ2aSmyG1FDSmzpqTso/0w==')
```

hex:

```
m3u8download(m3u8url='https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8',key='910d9a4a6c86d450d29b3a6a4eca3fd3')

```

链接：

```
key = 'http://******.key'
```

本地链接：

```
key = r"C:\Users\happy\Desktop\key.key"
```

#### iv

一般不需要自己填，自动解析，除非是 youku_AES

#### method

解密时对应的解密方法，当前支持 AES-128、SAMPLE-AES-CTR、KOOLEARN-ET、Widevine、copyrightDRM,一般不用更改，自动识别

```
m3u8download(m3u8url='https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8',key='910d9a4a6c86d450d29b3a6a4eca3fd3',method='AES-128')
```

```
m3u8download(m3u8url,title,key='',method='copyrightDRM')
```

#### work_dir

工作目录，默认为当前目录下的 Downloads 文件夹

```
m3u8download(m3u8url='https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8',key='910d9a4a6c86d450d29b3a6a4eca3fd3',work_dir='工作目录')
    
```

#### headers

自定义请求头，可以根据自己需要改

```
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63030532) Edg/100.0.4896.60',
        'Cookie': '',
        'Connection': 'close',
        'referer':""
    }
    m3u8download(m3u8url='https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8',key='910d9a4a6c86d450d29b3a6a4eca3fd3',work_dir='工作目录',headers=headers)

```

#### enable_del

删除除视频、音频之外的多余文件，默认为True，改为False之后可保留分片和解析的文件

```
m3u8download(m3u8url='https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8',key='910d9a4a6c86d450d29b3a6a4eca3fd3',work_dir='工作目录',enable_del=False)
```

#### merge_mode

视频合并方式

```
merge_mode=1 为直接二进制合并
```

```
merge_mode=2 先二进制合并再 ffmpeg 转码
```

```
merge_mode=3 用ffmpeg 合并
```

默认为1

#### base_uri_parse

解析m3u8链接时用的网址前缀，一般可自动识别

#### proxy

添加代理，当前支持`http https`

```
from H_m3u8DL import m3u8download
m3u8download(m3u8url=m3u8rul,proxy={"http": "http://127.0.0.1:7890", "https": "https://127.0.0.1:7890"})
```

### 修复记录

2022.6.15

修复若干问题，自动添加 `ffmpeg mp4decrypt` 等工具包

2022.6.14

修复 default 方法解析

2022.06.11

默认合并方式改为二进制合并，优化进度条显示

2022.06.10

修复baseuri解析错误

2022.06.06 

添加代理，新增 `H_m3u8DL "m3u8url"` 下载


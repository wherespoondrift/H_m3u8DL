import json, sys, os
import time, base64
from argparse import ArgumentParser
from H_m3u8DL import parser, download, merge, delFile, idm5, decrypt, version


def m3u8download(
        m3u8url,
        title='',
        base_uri_parse='',
        threads=16,
        key=None,
        iv=None,
        method=None,
        work_dir=None,
        headers=None,
        enable_del=True,
        merge_mode=1,
        proxy=None
):
    """ 程序入口

    :param m3u8url: m3u8链接、文件、文件夹、List
    :param title:视频名称
    :param base_uri_parse:自定义baseuri
    :param threads:线程数
    :param key:自定义key
    :param iv:自定义iv
    :param method:自定义方法 'SAMPLE-AES-CTR', 'cbcs', 'SAMPLE-AES','AES-128','copyrightDRM'
    :param work_dir:工作目录
    :param headers:自定义请求头
    :param enable_del:下载完成后删除多余文件False True
    :param merge_mode:合并方法，1:二进制合并 2:二进制合并后再用ffmpeg 转码 3:用ffmpeg 合并
    :param proxy:设置代理 {'http':'http://127.0.0.1:8888','https:':'https://127.0.0.1:8888'}
    :return:None
    """

    # 构造m3u8下载信息
    # list: m3u8url = [{'m3u8url':m3u8url,'title':title},{'m3u8url':m3u8url,'title':title}]

    try:
        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63030532) Edg/100.0.4896.60',
                'Cookie': '',
                'Connection': 'close'
            }
        if work_dir is None:
            work_dir = './Downloads'
        if type(proxy) == str:
            proxies = {'http': proxy}
        elif type(proxy) == json:
            proxies = proxy
        else:
            proxies = None
        if method == 'default':
            method = None
        if '.mp4' in m3u8url and 'm3u8' not in m3u8url:
            idm5.download(url=m3u8url, save_name=title if '.mp4' in title else title + '.mp4')

        else:
            if type(m3u8url) == list:
                infos = m3u8url
                for info in infos:
                    m3u8download(m3u8url=info['m3u8url'], title='' if 'title' not in info else info['title'],
                                 base_uri_parse=None if 'base_uri_parse' not in info else info['base_uri_parse'],
                                 enable_del=True if 'enable_del' not in info else info['enable_del'],
                                 merge_mode=1 if 'merge_mode' not in info else info['merge_mode'],
                                 headers=None if 'headers' not in info else info['headers'],
                                 work_dir=None if 'work_dir' not in info else info['work_dir'],
                                 method=None if 'method' not in info else info['method'],
                                 key=None if 'key' not in info else info['key'],
                                 proxy=None if 'proxy' not in info else info['proxy'])

                sys.exit(0)
            # dir: m3u8url = r'c:\windows\'

            elif os.path.isdir(m3u8url):
                for root, dirs, files in os.walk(m3u8url):
                    for f in files:
                        file = os.path.join(root, f)
                        if os.path.isfile(file):
                            if file.split('.')[-1] == 'm3u8':
                                m3u8download(m3u8url=file, key=key, title=title, base_uri_parse=base_uri_parse,
                                             enable_del=enable_del, merge_mode=merge_mode, headers=headers,
                                             work_dir=work_dir, method=method, proxy=proxies)
                sys.exit(0)
            # txt 文件中 title,m3u8url  一行一个链接
            elif os.path.isfile(m3u8url):
                if m3u8url[-4:] == '.txt':
                    with open(m3u8url, 'r', encoding='utf-8') as f:
                        m3u8texts = f.read()
                    list_m3u8text = m3u8texts.split('\n')
                    for m3u8text in list_m3u8text:
                        m3u8texts = m3u8text.split(',')
                        title = m3u8texts[0]
                        m3u8url = m3u8texts[1]
                        if len(m3u8texts) >= 3:
                            key = m3u8texts[2]
                        m3u8download(m3u8url=m3u8url, key=key, title=title, base_uri_parse=base_uri_parse,
                                     enable_del=enable_del, merge_mode=merge_mode, headers=headers, work_dir=work_dir,
                                     method=method, proxy=proxies)
                    sys.exit(0)
            WideVine = ['SAMPLE-AES-CTR', 'cbcs', 'SAMPLE-AES']

            title, durations, count, temp_dir, data, method, enable_del, merge_mode, key = parser.Parser(m3u8url, title,
                                                                                                         base_uri_parse,
                                                                                                         method=method,
                                                                                                         key=key, iv=iv,
                                                                                                         work_dir=work_dir,
                                                                                                         headers=headers,
                                                                                                         enable_del=enable_del,
                                                                                                         merge_mode=merge_mode).run()

            tm = time.strftime("%H:%M:%S", time.gmtime(durations))
            print(title, tm, f'method:{method}')
            segments = json.loads(data)['segments']

            infos = []
            for segment in segments:
                name = segment['title'] + '.ts'
                info1 = {
                    'title': temp_dir + '/video/' + name,
                    'link': segment['uri'],
                    'proxies': proxies
                }

                if 'key' in segment or method != None:

                    info1['method'] = method
                    if method == 'copyrightDRM':
                        info1['key'] = key
                        info1['iv'] = key

                        decrypt.decrypt_copyrightDRM(m3u8url, title, key)
                        print('调用执行完成')
                        sys.exit(0)

                    elif method in WideVine:
                        info1['key'] = key
                        info1['iv'] = key
                    else:
                        info1['key'] = base64.b64decode(segment['key']['uri'])
                        info1['iv'] = bytes.fromhex(segment['key']['iv'])
                infos.append(info1)

            download.FastRequests(infos, threads=threads, headers=headers).run()  # 下载

            # 下载完成，开始合并
            merge.Merge(temp_dir, mode=merge_mode)

            if method in WideVine:
                decrypt.decrypt2(temp_dir, key)
            # 删除多余文件
            if enable_del:
                delFile.del_file(temp_dir)
            print()
    except Exception as e:
        print(f'出错:',e)



def main(argv=None):
    parser = ArgumentParser(
        prog=f"version {version.version}",
        description=("一个python写的m3u8流视频下载器,适合全平台,https://github.com/hecoter/H_m3u8DL")
    )

    parser.add_argument("m3u8url", default='', help="链接、本地文件链接、文件夹链接、txt文件")
    parser.add_argument("-title", default='', help="视频名称")
    parser.add_argument("-base_uri_parse", default='', help="解析时的baseuri")
    parser.add_argument("-threads", default=16, help='线程数')
    parser.add_argument("-key", default=None, help='key')
    parser.add_argument("-iv", default=None, help='iv')
    parser.add_argument("-method", default=None, help='解密方法')
    parser.add_argument("-work_dir", default='./Downloads', help='工作目录')
    parser.add_argument("-headers", default=None, help='请求头')
    parser.add_argument("-enable_del", default=True, help='下载完删除多余文件')
    parser.add_argument("-merge_mode", default=3, help='1:二进制合并，2：二进制合并完成后用ffmpeg转码，3：用ffmpeg转码')
    parser.add_argument("-proxy", default=None,
                        help="代理：{'http':'http://127.0.0.1:8888','https:':'https://127.0.0.1:8888'}")
    args = parser.parse_args(argv)
    if args.m3u8url == '':
        pass
    else:
        m3u8download(m3u8url=args.m3u8url, title=args.title, base_uri_parse=args.base_uri_parse, threads=args.threads,
                     key=args.key, iv=args.iv, method=args.method, work_dir=args.work_dir, headers=args.headers,
                     enable_del=args.enable_del, merge_mode=args.merge_mode, proxy=args.proxy)


if __name__ == '__main__':
    main()

    # m3u8url = 'https://pl-ali.youku.com/playlist/m3u8?vid=XNDMwMjk5OTU2MA%3D%3D&type=cmaf4hd2&ups_client_netip=3b343443&utid=qYJ6Ge93NBcCATs0NGZhFahZ&ccode=0502&psid=adeceb5a3428ffc7bdfebbd119d3ca1c41346&ups_userid=1577938132&ups_ytid=1577938132&app_ver=4.0.77&duration=10429&expire=18000&drm_type=19&drm_device=7&drm_default=16&sm=1&nt=1&oss_file=05007D0000619E0FA68BB780000000EA1B47F2-462B-4E34-B1B7-E6221757DE75&media_type=standard%2Csubtitle&hotvt=1&dyt=0&ups_ts=1655351638&onOff=16&encr=0&ups_key=3b7f9224b69b0b4546783190655e6716'
    # key = '6710b9f92a2ef916f92fe5ba1c424ba9'
    # m3u8download(m3u8url,key=key)


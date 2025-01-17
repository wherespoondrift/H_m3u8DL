import m3u8
import os, re, json, sys

import requests
from rich.table import Table
from rich.console import Console
import H_m3u8DL
from H_m3u8DL import decrypt
from H_m3u8DL.decrypt_plus import Decrypt_plus



class Parser:
    def __init__(
            self, m3u8url, title='',base_uri_parse='',method=None, key=None, iv=None, work_dir='./Downloads', headers=None,enable_del=True,merge_mode=3,proxies=None):

        if not os.path.exists(work_dir):
            os.makedirs(work_dir)

        if title == '':
            title = self.guess_title(m3u8url)


        self.title = self.check_title(title)
        self.proxies = proxies
        self.temp_dir = work_dir + '/' + self.title

        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

        if not os.path.exists(self.temp_dir + '/video'):
            os.makedirs(self.temp_dir + '/video')
        if not os.path.exists(self.temp_dir + '/audio'):
            os.makedirs(self.temp_dir + '/audio')

        self.m3u8url = m3u8url
        self.headers = headers
        self.method = method
        self.key = key
        self.iv = iv
        self.work_dir = work_dir
        self.enable_del = enable_del
        self.merge_mode = merge_mode
        self.durations = 0
        self.count = 0
        self.resolution = ''
        self.base_uri_parse = base_uri_parse

    def resume(self, List1):
        table = Table()
        console = Console(color_system='256', style=None)
        List2 = []
        if List1 == []:
            print('列表获取错误')
            return
        elif len(List1) == 1:
            return List1
        i = 0
        table.add_column(f'[red]序号')
        table.add_column(f'[red]名称')
        table.add_column(f'[red]清晰度')
        table.add_column(f'[red]链接')
        for List in List1:
            # print("{:>3}  {:<30} {:<10}{:<50}".format(i,List['title'],List['resolution'],List['m3u8url']))
            table.add_row(str(i),None if 'title' not in List else List['title'],None if 'resolution' not in List else List['resolution'],List['m3u8url'])
            # print('{:^8}'.format(i), List['Title'],List['play_url'])
            i = i + 1
        console.print(table)
        numbers = input('输入下载序列（① 5 ② 4-10 ③ 4 10）:')
        if ' ' in numbers:
            for number in numbers.split(' '):
                number = int(number)
                List2.append(List1[number])
        elif '-' in numbers:
            number = re.findall('\d+', numbers)
            return List1[int(number[0]):int(number[1]) + 1]
        else:
            number = re.findall('\d+', numbers)
            List2.append(List1[int(number[0])])
            return List2
        return List2

    def guess_title(self,m3u8url):

        def youku():
            vid = re.findall('vid=(.+?)&', m3u8url)[0].replace('%3D', '=')
            parse_url = f'https://ups.youku.com/ups/get.json?vid={vid}&ccode=0532&client_ip=192.168.1.1&client_ts=1652685&utid=zugIG23ivx8CARuB3b823VC%2B'

            response = requests.get(parse_url,verify=False).json()
            title = response['data']['video']['title']
            return title
        if 'cibntv.net/playlist/m3u8?vid=' in m3u8url or 'youku.com/playlist/m3u8?vid=' in m3u8url:
            title = youku()
        else:
            title = m3u8url.split('?')[0].split('/')[-1].split('\\')[-1].replace('.m3u8', '')
        return title

    def run(self):

        # preload

        if 'xet.tech' in self.m3u8url:
            self.m3u8url = Decrypt_plus().xiaoetong(m3u8url=self.m3u8url)
        elif 'huke88.com' in self.m3u8url:
            (self.m3u8url,self.key) = Decrypt_plus().DecodeHuke88Key(m3u8url=self.m3u8url)
        # elif 'play.bokecc.com' in self.m3u8url:
        #     (self.m3u8url, self.key) = Decrypt_plus().DecodeBokeccKey(m3u8url=self.m3u8url)
        def preload(m3u8obj):
            def del_privinf(data):
                if '#EXT-X-PRIVINF' in data:
                    data = re.sub('#EXT-X-PRIVINF.+', '', data, re.DOTALL)
                    return del_privinf(data)
                return data
            if '#EXT-X-PRIVINF:' in m3u8obj.dumps():
                response = requests.get(self.m3u8url,verify=False,proxies=self.proxies).text
                m3u8data = del_privinf(response)
                with open('temp.m3u8','w',encoding='utf-8') as f:
                    f.write(m3u8data)
                    f.close()
                m3u8obj = m3u8.load('temp.m3u8')
                m3u8obj = preload(m3u8obj)
            return m3u8obj

        m3u8obj = m3u8.load(uri=self.m3u8url, headers=self.headers, verify_ssl=False,http_client=m3u8.DefaultHTTPClient(proxies=self.proxies))

        m3u8obj = preload(m3u8obj)
        raw = m3u8obj.dumps()
        with open(self.work_dir + '/' + self.title + '/' + 'raw.m3u8', 'w', encoding='utf-8') as f:
            f.write(raw)
        segments = m3u8obj.data['segments']

        # 处理baseuri
        if m3u8obj.base_uri.count('//') > 1:
            m3u8obj.base_uri = '/'.join(m3u8obj.base_uri.split('/')[:3])

        if self.base_uri_parse != '':
            m3u8obj.base_uri = self.base_uri_parse

        ########################################
        if m3u8obj.data['playlists'] != []:
            infos = []

            print('检测到大师列表，构造链接……')
            playlists = m3u8obj.data['playlists']

            # self.base_uri_parse = '/'.join(m3u8obj.base_uri.split('/')[:-3])
            for playlist in playlists:

                if 'resolution' in playlist['stream_info']:
                    resolution = playlist['stream_info']['resolution']
                elif 'resolu' in playlist['stream_info']:
                    resolution = playlist['stream_info']['resolu']
                else:
                    resolution = ''
                info = {
                    'm3u8url':m3u8obj.base_uri + playlist['uri'] if playlist['uri'][:4] != 'http' else playlist['uri'],# playlist['uri']
                    'title':self.title +'_' + resolution,
                    'base_uri_parse':m3u8obj.base_uri,
                    'resolution':resolution,
                    'work_dir':self.work_dir,
                    'headers':self.headers,
                    'enable_del':self.enable_del,
                    'merge_mode':self.merge_mode,
                    'method':self.method,
                    'key':self.key
                }
                infos.append(info)

            # 视频之后的其他文件
            if m3u8obj.data['media'] != []:
                medias = m3u8obj.data['media']

                # self.base_uri_parse = '/'.join(m3u8obj.base_uri.split('/')[:-3])
                for media in medias:

                    if 'stream_info' not in media:
                        resolution = ''

                    elif 'resolution' in media['stream_info']:
                        resolution = media['stream_info']['resolution']
                    elif 'resolu' in media['stream_info']:
                        resolution = media['stream_info']['resolu']
                    else:
                        resolution = ''
                    info = {
                        'm3u8url':m3u8obj.base_uri + media['uri'] if media['uri'][:4] != 'http' else media['uri'],
                        'title':self.title +'_' + resolution if resolution != '' else self.title + f'_{media["type"]}',
                        'resolution': resolution,
                        'base_uri_parse': m3u8obj.base_uri,
                        'work_dir': self.work_dir,
                        'headers': self.headers,
                        'enable_del': self.enable_del,
                        'merge_mode': self.merge_mode,
                        'method':self.method,
                        'key':self.key
                    }

                    infos.append(info)
            infos = self.resume(infos)
            H_m3u8DL.m3u8download(infos)

            sys.exit(0)

        if 'key' in segments[0] or  m3u8obj.data['keys'] != [None]:

            self.method, segments = decrypt.Decrypt(m3u8obj, self.temp_dir, method=self.method, key=self.key,
                                                    iv=self.iv).run()


            WideVine = ['SAMPLE-AES-CTR','cbcs','SAMPLE-AES'] # 针对widevine加密采取二进制合并
            if self.method in WideVine:
                self.merge_mode = 1
        self.count = len(segments)

        for i, segment in enumerate(segments):
            # 计算时长
            if 'duration' in segment:
                self.durations += segment['duration']
            if 'http' != segment['uri'][:4]:
                if segment['uri'][:2] == '//':
                    segment['uri'] = 'https:' + segment['uri']
                else:
                    segment['uri'] = m3u8obj.base_uri + segment['uri']

                segments[i]['uri'] = segment['uri']
            segment['title'] = str(i).zfill(6)
            segments[i]['title'] = segment['title']


        data = json.dumps(m3u8obj.data, indent=4,default=str)

        with open(f'{self.work_dir}/{self.title}/meta.json', 'w', encoding='utf-8') as f:
            f.write(data)
        # 写入raw.m3u8


        return self.title, self.durations, self.count, self.temp_dir, data, self.method,self.enable_del,self.merge_mode,self.key

    def check_title(self, title):
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        new_title = re.sub(rstr, "_", title)  # 替换为下划线
        if new_title[-1] == ' ':
            new_title = new_title[:-1]
            new_title = self.check_title(new_title)

        return new_title

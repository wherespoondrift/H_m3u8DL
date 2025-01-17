import os
import platform
import sys
class util:
    def __init__(self):
        self.platform = platform.system()
        basePath = os.path.realpath(__file__).replace('Util.py','Tools/')
        if self.platform == 'Windows':
            self.ffmpegPath = basePath + 'ffmpeg.exe'
            self.mp4decryptPath = basePath + 'mp4decrypt_win.exe'
            self.youkudecryptPath = basePath + 'youkudecrypt.exe'
        elif self.platform == 'Linux':
            self.ffmpegPath = 'ffmpeg'
            self.mp4decryptPath = basePath + 'mp4decrypt_linux'
            self.youkudecryptPath = None
        else:
            self.ffmpegPath = None
            self.mp4decryptPath = None
            self.youkudecryptPath = None


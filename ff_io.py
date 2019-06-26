import subprocess

class FFIO:
    def __init__(self, popen, framesz, offset=None):
        self.popen = popen
        self.framesz = framesz
        self.rd = False
        self.cnt = 0
        if offset != None:
            self.rd = True
            self.forward_frames(offset)
    def read_frame(self):
        self.ans = b''
        while len(self.ans) < self.framesz:
            self.ans += self.popen.stdout.read(self.framesz - len(self.ans))
        self.cnt += 1
        return self.ans
    def write_frame(self, frame):
        while frame:
            frame = frame[self.popen.stdin.write(frame):]
        self.cnt += 1
    def forward_frames(self, n, sink=None):
        l = self.framesz * n
        wrcnt = 0
        while l:
            chunk = self.popen.stdout.read(min(100000000, l))
            l -= len(chunk)
            print('fwd', len(chunk), 'left', l)
            if sink != None:
                sink.write_frame(chunk)
                wrcnt += 1
        self.cnt += n
        if sink != None:
            sink.cnt += n - wrcnt
    def close(self):
        if self.rd: self.popen.kill()
        else:
            self.popen.stdin.close()
            self.popen.wait()

class FFIOManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.size = '%dx%d'%(width, height)
        self.video_sources = {}
        self.audio_sources = {}
    def open_video_source(self, file, offset):
        if file in self.video_sources:
            if self.video_sources[file].cnt > offset:
                self.video_sources[file].close()
                del self.video_sources[file]
                print('backward seek')
            else:
                print('forward seek, reusing')
                self.video_sources[file].forward_frames(offset - self.video_sources[file].cnt)
                return self.video_sources[file]
        else:
            print('opening from scratch')
        p = subprocess.Popen(('ffmpeg', '-i', file, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', self.size, '-r', '30', '-'), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        ans = FFIO(p, self.width * self.height * 3, offset)
        self.video_sources[file] = ans
        return ans
    def open_audio_source(self, file, offset):
        if file in self.audio_sources:
            if self.audio_sources[file].cnt > offset:
                self.audio_sources[file].close()
                del self.audio_sources[file]
                print('backward seek')
            else:
                print('forward seek, reusing')
                self.audio_sources[file].forward_frames(offset - self.audio_sources[file].cnt)
                return self.audio_sources[file]
        else:
            print('opening from scratch')
        p = subprocess.Popen(('ffmpeg', '-i', file, '-f', 's16le', '-ac', '2', '-ar', '48000', '-'), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        ans = FFIO(p, 6400, offset)
        self.audio_sources[file] = ans
        return ans
    def open_video_sink(self, file):
        if file == None: return NullSink()
        p = subprocess.Popen(('ffmpeg', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', self.size, '-r', '30', '-i', '-', '-y', file), stdin=subprocess.PIPE)
        return FFIO(p, self.width * self.height * 3)
    def open_audio_sink(self, file):
        if file == None: return NullSink()
        p = subprocess.Popen(('ffmpeg', '-f', 's16le', '-ac', '2', '-ar', '48000', '-i', '-', '-y', file), stdin=subprocess.PIPE)
        return FFIO(p, 6400)

class NullSink:
    def write_frame(self, fr):
        raise RuntimeError("This sink is disabled")
    def close(self): pass

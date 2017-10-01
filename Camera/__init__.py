import subprocess,os,signal

class CameraController(object):
    midori = curl = uv4l = None
    vidHeight = 600
    vidWidth = 800
    fileName = os.getcwd()+"/tests/test.h264"
    orgFileName = os.getcwd()+"/tests/test.h264"

    def __init__(self, height=600, width=800, fileName=""):
        self.vidWidth=width
        self.vidHeight=height
        if len(fileName) > 0:
            self.orgFileName=fileName
        self.incFileName()

    def start(self):
        uv4lCom = ["uv4l", "--driver", "raspicam", "--width", str(self.vidWidth), "--height", str(self.vidHeight), "--enable-server", "--encoding", "h264"]
        print "UV4L Command: "+' '.join(uv4lCom)
        self.uv4l = subprocess.Popen(uv4lCom, preexec_fn=os.setsid)
        return self

    def stop(self):
        if self.uv4l != None:
            subprocess.Popen(["pkill", "uv4l"])
            
    def incFileName(self):
        path = '/'.join(self.orgFileName.split('/')[:-1])
        name = '.'.join(self.orgFileName.split('/')[-1].split('.')[:-1])
        ext = self.orgFileName.split('/')[-1].split('.')[-1]
        fileName = self.orgFileName
        n = 1
        while os.path.exists(fileName):
            fileName = path + '/' + name + '-' + str(n) + '.' + ext
            n += 1
        self.fileName = fileName

    def openBrowser(self):
        DEVNULL = open(os.devnull, 'wb')
        midoriCom = ["midori",  "-a", "localhost:8080/stream", "-e", "NavigationBar"]
        print "Midori Command: "+' '.join(midoriCom)
        self.midori  = subprocess.Popen(midoriCom, stderr=DEVNULL, preexec_fn=os.setsid)

    def startRecord(self):
        curlCom = ["curl", "localhost:8080/stream/video.h264"]
        ffCom = ['ffmpeg', '-y', '-i', '-', '-c:v', 'copy', '-an', '-f', 'segment', '-segment_time', '10', self.fileName.split('.')[0]+'\(%d\)'+'.'+self.fileName.split('.')[1]]
        fullCom = curlCom + ['|'] + ffCom
        print "full Command: "+' '.join(fullCom)
        if not os.path.exists('/'.join(self.fileName.split('/')[:-1])):
            os.mkdir('/'.join(self.fileName.split('/')[:-1]))
        self.curl = subprocess.Popen(fullCom, shell=True)

    def stopRecord(self):
        if self.curl != None and self.curl.pid != None:
            subprocess.Popen(["kill",str(self.curl.pid)])
        self.incFileName()


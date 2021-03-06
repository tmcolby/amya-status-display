from PIL import Image, ImageDraw, ImageFont
from showip.showIP import ShowIP
import subprocess
from subprocess import Popen, PIPE
import shlex
import sys, os
from time import sleep
from datetime import datetime
import hashlib
import re
from led import Led
import time
from pythonping import ping
import threading
from jsonconfig import JsonConfig

canReachServer = False
def ping_server():
    global canReachServer
    config = JsonConfig('/storage/configs/pickled.config.json')
    host = config.get('mqtt','connection','host')
    try:
        canReachServer = ping(host, count=1).success()
    except:
        pass
    logger.debug(f"can reach server: {canReachServer}")
    threading.Timer(10, ping_server).start()

def _procCmds(cmds):
    p = [0 for c in cmds]
    for i,c in enumerate(cmds):
       args = shlex.split(c)
       if i == 0: # first cmd
           p[i] = Popen(args, stdout=PIPE)
       else:
           p[i] = Popen(args, stdin=p[i-1].stdout, stdout=PIPE)
    p[0].stdout.close()
    resp = str(p[len(p)-1].communicate()[0],'utf-8')
    return resp
    
def _serviceStatus(service):
    return os.system('systemctl is-active --quiet ' + service) == 0

def _gatherServiceInfo():
    serviceList = [
        'amya-cmd-resp-controllerd.service',
        'amya-cmd-resp-slaved.service',
        'amya-logo-2.service',
        'amya-monitor-ramdisk.service',
        'amya-node-api.service',
        'amya-publish-pickled.service',
        'amya-serial-polld.service',
        'amya-serial-server.service'
    ]
    status = map(_serviceStatus, serviceList)
    return dict(zip(serviceList, status))

def _gatherInfo():
    sip = ShowIP()
    hostname = sip.getHostname()
    connected, net, host, mac = sip.getIPText()
    provisioned = False
    goingUporDown = False
    activity = False
    return connected, net, host, mac, hostname
    
def _isLocalLink(IP):
    regex = r"^169.254"
    m = re.match(regex,IP)
    return m != None

def _getTime():
    now = datetime.now()
    ascnow = now.strftime("%b %-d, %Y")
    asctime = now.strftime("%-I:%M %p")
    return (ascnow, asctime)

def _makeImage():
    connected, net, host, mac, hostname = _gatherInfo()
    dt, dtime = _getTime()

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, 20)
    bigfont = ImageFont.truetype(font_path, 22)

    if connected:
        screenColor = "green.png"
    else:
        screenColor = "red.png"
    img = Image.open(screenColor) 

    d = ImageDraw.Draw(img)
    fill = (255,255,255)
    d.text((8,105), "Network: {}".format(net), fill=fill, font=font)
    d.text((8,131), "IP: {}".format(host), fill=fill, font=font)
    d.text((8,157), "MAC: {}".format(mac), fill=fill, font=font)
    d.text((8,183), "Hostname: {}".format(hostname), fill=fill, font=font)
    d.text((100,14), "{}".format(dt), fill=fill, font=bigfont)
    d.text((100,50), "{}".format(dtime), fill=fill, font=bigfont)
#    cmd = 'rm ./pil*'
#    args = shlex.split(cmd)
#    p = subprocess.Popen(args, stdout=subprocess.DEVNULL)

    img.save('pil_text.png')
    # cmd = 'mv pil_text.temp.png pil_text.png'
    # args = shlex.split(cmd)  
    # p = subprocess.Popen(args, stdout=subprocess.DEVNULL)

def makeImage():
    connected, net, host, mac, hostname = _gatherInfo()
    dt, dtime = _getTime()

    canvasW, canvasH =(320, 240)
    green = (34, 177, 76)
    red = (222, 60, 60)
    white = (255, 255, 255)
    grey = (181, 181, 181)
    black = (0,0,0)
    
    if connected:
        screenColor = green
    else:
        screenColor = red
    bg = Image.new('RGB', (canvasW, canvasH), screenColor)
    
    logo = Image.open("awt_logo.png")
    logoW, logoH = logo.size
    logoPastePos = (int((canvasW-logoW)/2), 3)
    
    bg.paste(logo, logoPastePos, logo)
    
    fontPath = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    fontSize = 17
    font = ImageFont.truetype(fontPath, fontSize)
    line = "this line of text fills the screen width"
    textOverlay = ImageDraw.Draw(bg)
    
    verticalLineSpace = 0.3 # multiplier ie: .3 means 30%

    fill = black

    textOverlay.text((8,105), " Network: {}".format(net), fill=fill, font=font)
    textOverlay.text((8,131), "      IP: {}".format(host), fill=fill, font=font)
    textOverlay.text((8,157), "     MAC: {}".format(mac), fill=fill, font=font)
    textOverlay.text((8,183), "Hostname: {}".format(hostname), fill=fill, font=font)
    textOverlay.text((14,70), "{}".format(dt), fill=fill, font=font)
    textOverlay.text((164,70), "{}".format(dtime), fill=fill, font=font)
    bg.show()
    bg.save("pil_text.png")
		
		
# led setup
led = Led()
led.set_output(False)

SERIAL_IDLE_TIME = 60  # sec
def makeImage_2():
    global led

    canvasW, canvasH =(320, 240)
    
    white = (255, 255, 255)
    grey = (181, 181, 181)
    black = (0,0,0)
    red = (255, 0, 0)
    orange = (255, 153, 0)
    yellow = (255, 225, 0)
    green = (102, 255, 102)
    blue = (0, 102, 255)
    
    whiteTextFill = white
    greyTextFill = white
    blackTextFill = white
    redTextFill =  white
    yellowTextFill = black
    orangeTextFill = black
    greenTextFill = black
    blueTextFill = white
    
    connected, net, host, mac, hostname = _gatherInfo()
    dt, dtime = _getTime()
    
        # serviceList = [
        # 'amya-cmd-resp-controllerd.service',
        # 'amya-cmd-resp-slaved.service',
        # 'amya-logo-2.service',
        # 'amya-monitor-ramdisk.service',
        # 'amya-node-api.service',
        # 'amya-publish-pickled.service',
        # 'amya-serial-polld.service',
        # 'amya-serial-server.service'
    # ]
    
    serviceStatus = _gatherServiceInfo()
    isConfigured = os.path.isfile('/storage/opt/easy-rsa/easyrsa3/pki/ca.crt')
    global canReachServer
    # canReachServer = serviceStatus["amya-publish-pickled.service"]
    isLocalLink = _isLocalLink(host) 
    goingUporDown = False # don't know how to detect this yet.

    activity = False
    try:
        lastSerialPortActivity = os.stat('/tmp/pickleTracker')
        lastSerialPortActivity = lastSerialPortActivity.st_mtime
    except:
        lastSerialPortActivity = time.time() - SERIAL_IDLE_TIME - 1
    if (time.time() - lastSerialPortActivity) < SERIAL_IDLE_TIME:
        activity = True

   # '- Operational display
   # '- Add badge that flashes when a serial string is RCVD from RW unit but failed publication; use a second badge type if also successful publication to the broker
   # '- Change background colors:
   # '- Black on boot up and programmatic or commanded shut down (can't do anything on ACPI)
   # '- RED: no LAN connection or there is a local-link IP address
   # '- ORANGE: Got LAN IP addresss, but not configured
   # '- YELLOW:  Got IP addresss, is configured, cannot reach server
   # '- GREEN: all good: IP address, services running normally
   # '- BLUE: (as in  holding its breath...): All good, but no serial data in past X minutes
   # '- Font and font color: maximum readability with given background from wide angle

    if not goingUporDown and not connected or (connected and isLocalLink): 
        screenColor = red
        fill = redTextFill
        led.set_output(index=0, state=False)
    elif not goingUporDown and connected and not isLocalLink and not isConfigured :
        screenColor = orange
        fill = orangeTextFill
        led.set_output(index=0, state=False)
    elif not goingUporDown and connected and not isLocalLink and isConfigured and not canReachServer:
        screenColor = yellow
        fill = yellowTextFill
        led.set_output(index=0, state=False)
    elif not goingUporDown and connected and not isLocalLink and isConfigured and canReachServer and activity:
        screenColor = green
        fill = greenTextFill
        led.set_output(index=0, state=True)
    elif not goingUporDown and connected and not isLocalLink and isConfigured and canReachServer and not activity:
        screenColor = blue
        fill = blueTextFill
        led.set_output(index=0, state=True)
    elif goingUporDown:
        screenColor = black
        fill = blackTextFill
        led.set_output(index=0, state=False)
    else:
        screenColor = black
        fill = blackTextFill
        led.set_output(index=0, state=False)

       
    bg = Image.new('RGB', (canvasW, canvasH), screenColor)
    
    logo = Image.open("awt_logo.png")
    logoW, logoH = logo.size
    logoPastePos = (int((canvasW-logoW)/2), 3)
    
    bg.paste(logo, logoPastePos, logo)
    
    fontPath = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    fontSize = 17
    font = ImageFont.truetype(fontPath, fontSize)
    line = "this line of text fills the screen width"
    textOverlay = ImageDraw.Draw(bg)
    
    verticalLineSpace = 0.3 # multiplier ie: .3 means 30%

    textOverlay.text((8,105), " Network: {}".format(net), fill=fill, font=font)
    textOverlay.text((8,131), "      IP: {}".format(host), fill=fill, font=font)
    textOverlay.text((8,157), "     MAC: {}".format(mac), fill=fill, font=font)
    textOverlay.text((8,183), "Hostname: {}".format(hostname), fill=fill, font=font)
    textOverlay.text((14,70), "{}".format(dt), fill=fill, font=font)
    textOverlay.text((164,70), "{}".format(dtime), fill=fill, font=font)
    bg.show()
    bg.save("pil_text.png")

def testActive():
    cmd1 = 'ps aux'
    cmd2 = 'grep fbi' 
    cmd3 = 'grep -o noverbose'
    cmds = [cmd1, cmd2, cmd3]
    resp = _procCmds(cmds)
    return 'noverbose' in resp

def main():
    # cli commands
    updateDisplayCmd = 'fbi -d /dev/fb0 -noverbose -once -cachemem 1 -nocomments -readahead -T 1 pil_text.png'
    killFbiCmd = 'pkill fbi'
    getFbiPid = 'pgrep fbi'
    killPid = 'kill {}'

    # kick off ping server thread
    ping_server()

    # internal function to execute cli commands
    def execute_cmd(cmd):
        args = shlex.split(cmd)
        p = subprocess.Popen(args, stdout=subprocess.PIPE)
        return p.communicate()
        #stdout, stderr = p.communicate()

    # first things first.. lets start with a clean slate.. no running fbi processes
    execute_cmd(killFbiCmd)
           
    
    imageHashWas=None
    imageHashNow=None

    # get two instances of fbi running initially.  this, for some reason, prevents killing
    # the fbi processes from blanking out the display and showing "oops terminated" in console
    makeImage_2()
    logger.debug("starting the first fbi processes now..")
    execute_cmd(updateDisplayCmd)
    pid, _ = execute_cmd(getFbiPid)
    #mainPid = pid.pop(0).strip().decode('utf-8')
    pid = pid.strip().decode('utf-8').split('\n')
    if len(pid) > 1:
        logger.debug("what the heck?! ..there should only be one fbi process running")
    mainPid = pid.pop(0)
    logger.debug("main fbi PID: {}".format(mainPid))

    while True:
        # the display, once written to by fbi, does not need fbi running in the
        # background, so we just just blindly issue a command to kill it.
        #execute_cmd(killFbiCmd)

        # make a new image every loop and capture an sha1 hash of the image
        makeImage_2()
        imageHashNow=hashlib.sha1(open('pil_text.png', 'rb').read()).hexdigest()

        # here we detect if the image has changed
        # we dont write to the display unless the image has changed 
        if imageHashNow != imageHashWas:
            execute_cmd(updateDisplayCmd)
            pid, _ = execute_cmd(getFbiPid)
            pid = pid.decode('utf-8').strip().split('\n')
            logger.debug("fbi processes: {}".format(pid))
            pid.remove(mainPid)
            if pid:
                for n in pid:
                #for n in pid[1:]: 
                    logger.debug("killing fbi process: {}".format(n))
                    execute_cmd(killPid.format(n))
        imageHashWas = imageHashNow
        
        sleep(1)


if __name__ == "__main__":
    import logging
    import logging.handlers
    import sys

    #create local logger
    logger = logging.getLogger(__name__)
    LOG_TO_CONSOLE = True

    if LOG_TO_CONSOLE:
        handler = logging.StreamHandler(stream=sys.stdout)
    else:
        handler = logging.handlers.RotatingFileHandler(__file__+'.log', maxBytes=5000000, backupCount=1)

    formatter = logging.Formatter(fmt='%(asctime)s %(name) -55s %(levelname)-9s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    #create a logging whitelist - (comment out code in ~~ block to enable all child loggers)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    loggingWhitelist = ('root', '__main__')
    class Whitelist(logging.Filter):
        def __init__(self, *whitelist):
            self.whitelist = [logging.Filter(name) for name in whitelist]
        
        def filter(self, record):
            return any(f.filter(record) for f in self.whitelist)
    #add the whitelist filter to the handler
    handler.addFilter(Whitelist(*loggingWhitelist))
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #assign the handler to root logger (we use the root logger so that we get output from all child logger used in other modules)
    logging.root.addHandler(handler)
    #set the logging level for root logger
    logging.root.setLevel(logging.DEBUG)

    main()


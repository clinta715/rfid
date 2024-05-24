import serial
import serial.tools.list_ports
from os import system, name 
import argparse
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import json
import string
import re
import sys

serialport = "COM4"
cors_origin = "*"
line = []
line2 = []
sid = "0000"
pid = "0000"
bar = "Not Scanned."
newsid = "0000"
newpid = "0000"
newbar = "Not Scanned."
port = 8000
useconsole = 0
scannermode = 0
bindto = "localhost"

def writecard( newsid, newpid, newbar ):
    if scannermode == 0:
        print("- INFO: (Blue Sun Scanner) Sending: [writerfida 10 " + newsid + "]")
        serialcmd = "writerfida 10 " + newsid + "\n"
        try:
            ser.write( serialcmd.encode() )
        except:
            print("- ERROR: Resetting COM port.  Try again.")
            resetcom()
            return        
        ser.flush()
            
        print("- INFO: (Blue Sun Scanner) Return: [" + ser.read(37).decode(encoding='ascii', errors="backslashreplace") + "]" )
        print("- INFO: (Blue Sun Scanner) Sending: [writerfida 20 " + newpid + "]")
        serialcmd = "writerfida 20 " + newpid + "\n"
        ser.write( serialcmd.encode() )
        ser.flush()

        print("- INFO: (Blue Sun Scanner) Sending: [writerfida 30 " + newbar  + "]")
        serialcmd = "writerfida 30 " + newbar + "\n"
        ser.write( serialcmd.encode() )
        ser.flush()
        
    if scannermode == 1:
        ser.flush()
        serialcmd = "W" + newsid + newpid + newbar
        print("- INFO: (Dairyland Scanner) Sending: [" + serialcmd + "]")
        
        try:
            ser.write( serialcmd.encode() )
        except:
            print("- ERROR: (Dairyland Scanner) Error: Can't write to serial port!")
            return
        ser.flush()

    if scannermode == 0:
        while ser.read(1):
            done = 0

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def send_cors_headers(self):
        self.send_response(200, "ok")
        self.send_header("Access-Control-Allow-Origin", cors_origin)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Expose-Headers", "Content-Length, Content-Range")
        #self.send_header("Access-Control-Allow-Credentials", "true");
        self.send_header("Access-Control-Allow-Headers", "Accept,Origin,DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range")
        #self.send_header("Access-Control-Max-Age", "1")
        self.send_header("Content-type", "application/json")
        self.end_headers()        

    def do_GET(self):
        global newsid, newpid, newbar
        self.send_cors_headers()
        readcard()
        self.wfile.write(b"{")
        self.wfile.write(b" \"sid\" : \"" + sid.encode() + b"\",")
        self.wfile.write(b" \"pid\" : \"" + pid.encode() + b"\",")
        self.wfile.write(b" \"bar\" : \"" + bar.encode() + b"\"")
        self.wfile.write(b"}")

    def do_POST(self):
        self.send_cors_headers()
        content_len = int(self.headers["Content-Length"])
        post_body = self.rfile.read(content_len)
        rfidwrite = json.loads(post_body)
        print( json.dumps(rfidwrite) )
        
        writecard( rfidwrite["sid"], rfidwrite["pid"], rfidwrite["bar"] )
        
    def do_OPTIONS(self):
        print("- INFO: Responding to OPTIONS request")
        self.send_cors_headers()

httpd = HTTPServer( (bindto, port ), SimpleHTTPRequestHandler)

def readcard():
    global sid, pid, bar
    done = 0

    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
    while ser.read(1):
        done = 0
    
    print("- INFO: Current tag contents:")
    
    if scannermode == 0:
        print("- INFO: (Blue Sun Scanner) Sending: [readrfida 10 4]")
        try: 
            ser.write(b"readrfida 10 4\n")
        except:
            resetcom()
            print("- ERROR: Resetting COM port!  Try again.")
            return
            
        ser.flush()
        print("- INFO: (Blue Sun Scanner) Return: [" + ser.read(38).decode(encoding="ascii", errors="backslashreplace") + "]")
        sid = re.sub("[^A-Za-z0-9]+", " ", str(ser.read(4).decode(encoding="ascii",errors="replace"))).lstrip()
        sid = sid[:4]
    
        if sid == "Read":
            print("- ERROR: (Blue Sun Scanner) Error: Read error!")
            sid = "ERR!"
            pid = "ERR!"
            bar = "ERR!"
            print( "- INFO: (Blue Sun Scanner) SID: [" + sid + "]" )
            print( "- INFO: (Blue Sun Scanner) PID: [" + pid + "]")
            print( "- INFO: (Blue Sun Scanner) BAR: [" + bar + "]")
            ser.flush()
            return

    if scannermode == 1:
        print("- INFO: (Dairyland Scanner) Sending: [R]")
        ser.write(b"R")
        ser.flush()
        newsid = re.sub('[^A-Za-z0-9]+', ' ', str(ser.readline().decode(encoding='ascii', errors="replace"))).lstrip()
        newpid = re.sub('[^A-Za-z0-9]+', ' ', str(ser.readline().decode(encoding='ascii', errors="replace"))).lstrip()
        newbar = re.sub('[^A-Za-z0-9]+', ' ', str(ser.readline().decode(encoding='ascii', errors="replace"))).lstrip()
        
        newbar.replace("\x0A",".")
        newsid.replace("\x0A",".")
        newpid.replace("\x0A",".")
        
        newbar.replace("\x0D",".")
        newsid.replace("\x0D",".")
        newpid.replace("\x0D",".")
        
        sid = newsid[4:8]
        pid = newpid[4:8]
        bar = newbar[4:16]
        
        if bar[:3] == "/11":
            newbar = "ERR!"
            bar = "ERR!"
        if sid[:3] == "/11":
            newsid = "ERR!"
            sid = "ERR!"
        if pid[:3] == "/11":
            newpid = "ERR!"
            pid = "ERR!"
        
        newsid = sid
        newpid = pid
        newbar = bar
        
    print( "- SID: [" + sid + "]" )

    if scannermode == 0:
        print("- INFO: (Blue Sun Scanner) Sending: [readrfid 20 4]")
        ser.write(b"readrfida 20 4\n")
        ser.flush()
        print("- INFO: (Blue Sun Scanner) Return: [" + ser.read(43).decode(encoding="ascii", errors="backslashreplace") + "]")
        pid = re.sub("[^A-Za-z0-9]+", " ", str(ser.read(4).decode(encoding="ascii",errors="replace"))).lstrip()
        pid = pid[:4]

    print( "- PID: [" + pid + "]")

    if scannermode == 0:
        print("- INFO: (Blue Sun Scanner) Sending: [readrfid 30 12]")
        ser.write(b"readrfida 30 12\n")
        ser.flush()
        print("- INFO: (Blue Sun Scanner) Return: [" + ser.read(41).decode(encoding="ascii", errors="backslashreplace") + "]")
        bar = re.sub("[^A-Za-z0-9]+", " ", str(ser.read(12).decode(encoding="ascii",errors="replace"))).lstrip()
        bar = bar[:12]

    print( "- BAR: [" + bar + "]")

    ser.flush()
    return
    
def resetcom():
    isopen = 0

    while not( isopen ):
        try:
            if scannermode == 0:
                baudrate = 115200
            else:
                baudrate = 9600
    
            comlist = serial.tools.list_ports.comports()
            connected = []
            for element in comlist:
                connected.append(element.device)
            print("- INFO: Connected COM ports: " + str(connected) )
            ser = serial.Serial( serialport, baudrate, timeout=1 )  # should make this an argument
            isopen = 1
        except:
            isopen = 0
            print("- ERROR: Can't open serial port!")
            sys.exit()

    print( "- INFO: Using serial port: [" + ser.name + "]")
    print( "- INFO: Waiting for RFID reader to initialize... ")

    if scannermode == 0:
        while not ser.read(1):
            done = 0
    else:
        while ser.read(1):
            done = 0        

parser = argparse.ArgumentParser(description="why would you describe this", prog="mlr")
parser.add_argument("-p", "--port", default="/dev/ttyACM0", help="Name of serial port e.g. /dev/ttyACM0" )
parser.add_argument("-tcp", "--tcpport", default="8000", help="TCP/IP port for HTTP listener (default 8000)" )
parser.add_argument("-mode", "--scanmode", default="dairyland", help="Scanner mode: dairyland or bluesun")
parser.add_argument("-o", "--origin", default="*", help="CORS origin value")
parser.add_argument("-of", "--outfile", default="con:", help="Output log file name.")
parser.add_argument("-b", "--bind", default="localhost", help="Address to bind to" )
args = parser.parse_args(sys.argv[1:])

serialport = args.port
port = args.tcpport
cors_origin = args.origin
output_file = args.outfile
bindto = args.bind

if args.scanmode == "dairyland":
    scannermode = 1
else:
    scannermode = 0

#try:
#    f = open(output_file, "w")
#    sys.stdout = f # Change the standard output to the file we created.
#    sys.stderr = f # stderr
#except:
#    print("- ERROR: Can't open output logfile!");
    
print("- Dairyland Labs RFID Driver")

isopen = 0

while not( isopen ):
    try:
        if scannermode == 0:
            baudrate = 115200
        else:
            baudrate = 9600
            
        comlist = serial.tools.list_ports.comports()
        connected = []
        for element in comlist:
            connected.append(element.device)
            print("- INFO: Connected COM ports: " + str(connected) )
            
        ser = serial.Serial( serialport, baudrate, timeout=1 )  # should make this an argument
        isopen = 1
        
    except:
        isopen = 0
        print("- ERROR: Can't open specified COM port!")
        sys.exit()

print( "- INFO: Using serial port: [" + ser.name + "]")
print( "- INFO: Waiting for RFID reader to initialize... ")

if scannermode == 0:
    while not ser.read(1):
        done = 0
else:
    while ser.read(1):
        done = 0        

print("- INFO: Starting webserver at [http://" + bindto + ":" + str(port) + "]")

httpd.serve_forever()
sys.stdout = original_stdout # Reset the standard output to its original value
sys.exit()

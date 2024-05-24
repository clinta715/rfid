import serial
import serial.tools.list_ports
from os import system, name 
import argparse
import sys
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import json
import string
import re

serialport = "COM4"
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

def writecard( newsid, newpid, newbar ):
    if scannermode == 0:
        print("- (Blue Sun Scanner) Sending: [writerfida 10 " + newsid + "]")
        serialcmd = "writerfida 10 " + newsid + "\n"
        try:
            ser.write( serialcmd.encode() )
        except:
            print("- (Blue Sun Scanner) Error: Can't write to serial port!")
            return        
        ser.flush()
            
        print("- (Blue Sun Scanner) Return: [" + ser.read(37).decode(encoding='ascii', errors="backslashreplace") + "]" )

        print("- (Blue Sun Scanner) Sending: [writerfida 20 " + newpid + "]")
        serialcmd = "writerfida 20 " + newpid + "\n"
        ser.write( serialcmd.encode() )
        ser.flush()

        print("- (Blue Sun Scanner) Sending: [writerfida 30 " + newbar  + "]")
        serialcmd = "writerfida 30 " + newbar + "\n"
        ser.write( serialcmd.encode() )
        ser.flush()
        
    if scannermode == 1:
        ser.flush()
        serialcmd = "W" + newsid + newpid + newbar
        print("- (Dairyland Scanner) Sending: [" + serialcmd + "]")
        
        try:
            ser.write( serialcmd.encode() )
        except:
            print("- (Dairyland Scanner) Error: Can't write to serial port!")
            return
        ser.flush()

    if scannermode == 0:
        while ser.read(1):
            done = 0

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        global newsid, newpid, newbar
        self.send_response(200)

        if self.path[:3] == "/ui":
            if not self.path[:4] == "/ui?": readcard()
            self.send_header("Content-type", "text/html")
            self.end_headers()
            indexxfile = open("index.html", "r")
            indexdata = indexxfile.read()
            self.wfile.write( indexdata.encode() )
            indexxfile.close()
            
        if self.path[:5] == "/json":
            self.send_header("Content-type", "application/json")
            self.end_headers()
            readcard()
            self.wfile.write(b"{")
            self.wfile.write(b" \"sid\" : \"" + sid.encode() + b"\",")
            self.wfile.write(b" \"pid\" : \"" + pid.encode() + b"\",")
            self.wfile.write(b" \"bar\" : \"" + bar.encode() + b"\"")
            self.wfile.write(b"}")
        
        if self.path[:6] == "/write": 
            newsid = self.path[7:11]
            newpid = self.path[11:15]
            newbar = self.path[15:27]
            writecard( newsid, newpid, newbar )
            #readcard()

    def do_POST(self):
        content_len = int(self.headers['Content-Length'])
        post_body = self.rfile.read(content_len)
        rfidwrite = json.loads(post_body)
        print( json.dumps(rfidwrite) )
        
        writecard( rfidwrite['sid'], rfidwrite['pid'], rfidwrite['bar'] )

httpd = HTTPServer( ("localhost", port ), SimpleHTTPRequestHandler)

def readcard():
    global sid, pid, bar
    done = 0

    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
    while ser.read(1):
        done = 0
    
    print("- Current tag contents:")
    
    if scannermode == 0:
        print("- (Blue Sun Scanner) Sending: [readrfida 10 4]")
        ser.write(b'readrfida 10 4\n')
        ser.flush()
        print("- (Blue Sun Scanner) Return: [" + ser.read(38).decode(encoding='ascii', errors="backslashreplace") + "]")
        sid = re.sub('[^A-Za-z0-9]+', ' ', str(ser.read(4).decode(encoding='ascii',errors="replace"))).lstrip()
        sid = sid[:4]
    
        if sid == "Read":
            print("- (Blue Sun Scanner) Error: Read error!")
            sid = "ERR!"
            pid = "ERR!"
            bar = "ERR!"
            print( "- (Blue Sun Scanner) SID: [" + sid + "]" )
            print( "- (Blue Sun Scanner) PID: [" + pid + "]")
            print( "- (Blue Sun Scanner) BAR: [" + bar + "]")
            ser.flush()
            return

    if scannermode == 1:
        print("- (Dairyland Scanner) Sending: [R]")
        ser.write(b'R')
        ser.flush()
        # print("- Return: [" + ser.read(4).decode(encoding='ascii', errors="backslashreplace") + "]") 
        newsid = re.sub('[^A-Za-z0-9]+', ' ', str(ser.readline().decode(encoding='ascii', errors="replace"))).lstrip()
        # print("- Return: [" + ser.read(6).decode(encoding='ascii', errors="backslashreplace") + "]")
        newpid = re.sub('[^A-Za-z0-9]+', ' ', str(ser.readline().decode(encoding='ascii', errors="replace"))).lstrip()
        # print("- Return: [" + ser.read(6).decode(encoding='ascii', errors="backslashreplace") + "]")
        newbar = re.sub('[^A-Za-z0-9]+', ' ', str(ser.readline().decode(encoding='ascii', errors="replace"))).lstrip()
        
        newbar.replace('\x0A','.')
        newsid.replace('\x0A','.')
        newpid.replace('\x0A','.')
        
        newbar.replace('\x0D','.')
        newsid.replace('\x0D','.')
        newpid.replace('\x0D','.')
        
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
        print("- (Blue Sun Scanner) Sending: [readrfid 20 4]")
        ser.write(b'readrfida 20 4\n')
        ser.flush()
        print("- (Blue Sun Scanner) Return: [" + ser.read(40).decode(encoding='ascii', errors="backslashreplace") + "]")
        pid = re.sub('[^A-Za-z0-9]+', ' ', str(ser.read(4).decode(encoding='ascii',errors="replace"))).lstrip()
        pid = pid[:4]

    print( "- PID: [" + pid + "]")

    if scannermode == 0:
        print("- (Blue Sun Scanner) Sending: [readrfid 30 12]")
        ser.write(b'readrfida 30 12\n')
        ser.flush()
        print("- (Blue Sun Scanner) Return: [" + ser.read(41).decode(encoding='ascii', errors="backslashreplace") + "]")
        bar = re.sub('[^A-Za-z0-9]+', ' ', str(ser.read(12).decode(encoding='ascii',errors="replace"))).lstrip()
        bar = bar[:12]

    print( "- BAR: [" + bar + "]")

    ser.flush()
    return
        
parser = argparse.ArgumentParser(description='why would you describe this', prog='mlr')
parser.add_argument('-p', '--port', default='/dev/ttyACM0', help='Name of serial port e.g. /dev/ttyACM0' )
parser.add_argument('-tcp', '--tcpport', default='8000', help='TCP/IP port for HTTP listener (default 8000)' )
parser.add_argument('-mode', '--scanmode', default='dairyland', help='Scanner mode: dairyland or bluesun')

args = parser.parse_args(sys.argv[1:])

serialport = args.port
port = args.tcpport

if args.scanmode == "dairyland":
    scannermode = 1
else:
    scannermode = 0

isopen = 0

print("- Dairyland Labs RFID TEST")
print("- Starting webserver at [http://localhost:" + str(port) + "]")

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
        print("- Connected COM ports: " + str(connected) )
        ser = serial.Serial( serialport, baudrate, timeout=1 )  # should make this an argument
        isopen = 1
    except:
        isopen = 0
        serialport = input("- Can't open COM port, enter new port:")

print( "- Using serial port: [" + ser.name + "]")

print( "- Waiting for RFID reader to initialize... ")

if scannermode == 0:
    while not ser.read(1):
        done = 0
else:
    while ser.read(1):
        done = 0

print( "- Ready -- server waiting.")

httpd.serve_forever()

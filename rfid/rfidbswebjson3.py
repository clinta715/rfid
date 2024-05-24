import serial
import serial.tools.list_ports
from os import system, name 
import argparse
import sys
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import json

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

def writecard( newsid, newpid, newbar ):
    print("- Sending: [writerfida 10 " + newsid + "]")
    serialcmd = "writerfida 10 " + newsid + "\n"
    ser.write( serialcmd.encode() )
    ser.flush()
    print("- Return: [" + ser.read(37).decode(encoding='ascii', errors="replace") + "]" )

    print("- Sending: [writerfida 20 " + newpid + "]")
    serialcmd = "writerfida 20 " + newpid + "\n"
    ser.write( serialcmd.encode() )
    ser.flush()

    print("- Sending: [writerfida 30 " + newbar  + "]")
    serialcmd = "writerfida 30 " + newbar + "\n"
    ser.write( serialcmd.encode() )
    ser.flush()

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
    
    print("- Sending: [readrfida 10 4]")
    ser.write(b'readrfida 10 4\n')
    ser.flush()
    print("- Return: [" + ser.read(38).decode(encoding='ascii', errors="replace") + "]")
    sid = str(ser.read(4).decode(encoding='ascii',errors="replace"))
    sid = sid[:4]
    
    if sid == "Read":
        print("- Read error!")
        sid = "ERR!"
        pid = "ERR!"
        bar = "ERR!"
        print( "- SID: [" + sid + "]" )
        print( "- PID: [" + pid + "]")
        print( "- BAR: [" + bar + "]")
        ser.flush()
        return

    print( "- SID: [" + sid + "]" )

    print("- Sending: [readrfid 20 4]")
    ser.write(b'readrfida 20 4\n')
    ser.flush()
    print("- Return: [" + ser.read(40).decode(encoding='ascii', errors="replace") + "]")
    pid = str(ser.read(4).decode(encoding='ascii',errors="replace"))
    pid = pid[:4]

    print( "- PID: [" + pid + "]")

    print("- Sending: [readrfid 30 12]")
    ser.write(b'readrfida 30 12\n')
    ser.flush()
    print("- Return: [" + ser.read(41).decode(encoding='ascii', errors="replace") + "]")
    bar = str(ser.read(12).decode(encoding='ascii',errors="replace"))
    bar = bar[:12]

    print( "BAR: [" + bar + "]")

    ser.flush()
    return
        
parser = argparse.ArgumentParser(description='why would you describe this', prog='mlr')
parser.add_argument('-p', '--port', default='/dev/ttyACM0', help='Name of serial port e.g. /dev/ttyACM0' )
parser.add_argument('-tcp', '--tcpport', default='8000', help='TCP/IP port for HTTP listener (default 8000)' )

args = parser.parse_args(sys.argv[1:])

serialport = args.port
port = args.tcpport

isopen = 0

print("- Dairyland Labs RFID TEST")
print("- Starting webserver at [http://localhost:" + str(port) + "]")

while not( isopen ):
    try:
        comlist = serial.tools.list_ports.comports()
        connected = []
        for element in comlist:
            connected.append(element.device)
        print("- Connected COM ports: [" + str(connected) + "]")
        ser = serial.Serial( serialport, 115200, timeout=1 )  # should make this an argument
        isopen = 1
    except:
        isopen = 0
        serialport = input("- Can't open COM port, enter new port:")

print( "- Using serial port: [" + ser.name + "]")

print( "- Waiting for RFID reader to initialize... ")

while not ser.read(1):
    done = 0

print( "- Ready -- server waiting.")

httpd.serve_forever()

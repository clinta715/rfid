import argparse
import json
import re
import serial
import serial.tools.list_ports
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Tuple

# Configuration
DEFAULT_PORT = 8000
DEFAULT_SERIAL_PORT = '/dev/ttyACM0'
DEFAULT_CORS_ORIGIN = "*"
DEFAULT_SCANNER_MODE = "dairyland"

# Global variables
ser = None
sid = "0000"
pid = "0000"
bar = "Not Scanned."

class RFIDScanner:
    def __init__(self, mode: str, serial_port: str):
        self.mode = mode
        self.serial_port = serial_port
        self.baudrate = 9600 if mode == "dairyland" else 115200

    def initialize(self):
        global ser
        try:
            ser = serial.Serial(self.serial_port, self.baudrate, timeout=1)
            print(f"- Using serial port: [{ser.name}]")
            print("- Waiting for RFID reader to initialize... ")
            self._wait_for_reader()
            return True
        except serial.SerialException as e:
            print(f"- Error initializing serial port: {e}")
            return False

    def _wait_for_reader(self):
        if self.mode == "bluesun":
            while not ser.read(1):
                pass
        else:
            while ser.read(1):
                pass

    def read_card(self) -> Tuple[str, str, str]:
        if self.mode == "bluesun":
            return self._read_card_bluesun()
        else:
            return self._read_card_dairyland()

    def _read_card_bluesun(self) -> Tuple[str, str, str]:
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        commands = [
            ('readrfida 10 4\n', 'sid'),
            ('readrfida 20 4\n', 'pid'),
            ('readrfida 30 12\n', 'bar')
        ]

        results = {}
        for cmd, key in commands:
            print(f"- (Blue Sun Scanner) Sending: [{cmd.strip()}]")
            ser.write(cmd.encode())
            ser.flush()
            response = ser.read(38).decode(encoding='ascii', errors="backslashreplace")
            print(f"- (Blue Sun Scanner) Return: [{response}]")
            value = re.sub('[^A-Za-z0-9]+', ' ', ser.read(4 if key != 'bar' else 12).decode(encoding='ascii', errors="replace")).strip()
            results[key] = value[:4 if key != 'bar' else 12]

        if results['sid'] == "Read":
            print("- (Blue Sun Scanner) Error: Read error!")
            return "ERR!", "ERR!", "ERR!"

        return results['sid'], results['pid'], results['bar']

    def _read_card_dairyland(self) -> Tuple[str, str, str]:
        print("- (Dairyland Scanner) Sending: [R]")
        ser.write(b'R')
        ser.flush()

        results = {}
        for key in ['sid', 'pid', 'bar']:
            value = re.sub('[^A-Za-z0-9]+', ' ', ser.readline().decode(encoding='ascii', errors="replace")).strip()
            value = value.replace('\x0A', '.').replace('\x0D', '.')
            results[key] = value[4:8 if key != 'bar' else 16]

            if value[:3] == "/11":
                results[key] = "ERR!"

        return results['sid'], results['pid'], results['bar']

    def write_card(self, new_sid: str, new_pid: str, new_bar: str):
        if self.mode == "bluesun":
            self._write_card_bluesun(new_sid, new_pid, new_bar)
        else:
            self._write_card_dairyland(new_sid, new_pid, new_bar)

    def _write_card_bluesun(self, new_sid: str, new_pid: str, new_bar: str):
        commands = [
            (f"writerfida 10 {new_sid}\n", new_sid),
            (f"writerfida 20 {new_pid}\n", new_pid),
            (f"writerfida 30 {new_bar}\n", new_bar)
        ]

        for cmd, value in commands:
            print(f"- (Blue Sun Scanner) Sending: [{cmd.strip()}]")
            try:
                ser.write(cmd.encode())
                ser.flush()
                print(f"- (Blue Sun Scanner) Return: [{ser.read(37).decode(encoding='ascii', errors='backslashreplace')}]")
            except serial.SerialException as e:
                print(f"- ERROR: {e}")
                return

        while ser.read(1):
            pass

    def _write_card_dairyland(self, new_sid: str, new_pid: str, new_bar: str):
        ser.flush()
        cmd = f"W{new_sid}{new_pid}{new_bar}"
        print(f"- (Dairyland Scanner) Sending: [{cmd}]")
        try:
            ser.write(cmd.encode())
            ser.flush()
        except serial.SerialException as e:
            print(f"- (Dairyland Scanner) Error: {e}")

class RFIDRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.cors_origin = kwargs.pop('cors_origin', DEFAULT_CORS_ORIGIN)
        self.scanner = kwargs.pop('scanner')
        super().__init__(*args, **kwargs)

    def send_cors_headers(self):
        self.send_response(200, "ok")
        self.send_header("Access-Control-Allow-Origin", self.cors_origin)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Accept,Origin,DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range")
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        self.send_cors_headers()
        sid, pid, bar = self.scanner.read_card()
        response = json.dumps({"sid": sid, "pid": pid, "bar": bar})
        self.wfile.write(response.encode())

    def do_POST(self):
        self.send_cors_headers()
        content_len = int(self.headers['Content-Length'])
        post_body = self.rfile.read(content_len)
        rfid_write = json.loads(post_body)
        print(json.dumps(rfid_write))
        
        self.scanner.write_card(rfid_write['sid'], rfid_write['pid'], rfid_write['bar'])
        
    def do_OPTIONS(self):
        print("- Responding to OPTIONS request")
        self.send_cors_headers()

def parse_arguments():
    parser = argparse.ArgumentParser(description='RFID Server for Dairyland Labs')
    parser.add_argument('-p', '--port', default=DEFAULT_SERIAL_PORT, help='Name of serial port e.g. /dev/ttyACM0')
    parser.add_argument('-tcp', '--tcpport', type=int, default=DEFAULT_PORT, help='TCP/IP port for HTTP listener (default 8000)')
    parser.add_argument('-mode', '--scanmode', default=DEFAULT_SCANNER_MODE, choices=['dairyland', 'bluesun'], help='Scanner mode: dairyland or bluesun')
    parser.add_argument('-o', '--origin', default=DEFAULT_CORS_ORIGIN, help='CORS origin value')
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    print("- Dairyland Labs RFID SERVER")
    print(f"- Starting webserver at [http://localhost:{args.tcpport}]")

    scanner = RFIDScanner(args.scanmode, args.port)
    if not scanner.initialize():
        print("Failed to initialize the RFID scanner. Exiting.")
        return

    handler = lambda *args, **kwargs: RFIDRequestHandler(*args, cors_origin=args.origin, scanner=scanner, **kwargs)
    httpd = HTTPServer(("localhost", args.tcpport), handler)
    
    print("- Ready -- server waiting.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down the server...")
        httpd.socket.close()

if __name__ == "__main__":
    main()

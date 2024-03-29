from flask import Flask, make_response, send_file
import serial, time, os, socket

labels = ['press_dump', 'c1', 'purge', 'c3', 'c4', 'lox_qd', 'lox_dump', 'fuel_vent', 'c_lox_fill', 'mpv', 'ignite', 'c11', 'lox_vent', 'press_qd', 'c14', 'press_fill']
log = open('/home/rocket/logs/controls.csv', 'a')
port = '/dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.4:1.0'
app = Flask(__name__)

while True:
    try:
        time.sleep(1)
        serial_port = serial.Serial(port, 9600, timeout=0.1)
    except:
        continue
    finally:
        break

def millis():
    return int(time.time_ns() / 1000000)

addr = ('127.0.0.1', 2000)
client = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)

@app.route('/favicon.ico')
def favicon():
    return ('', 200)

@app.route('/controls/<request>')
def handle_request(request):
    print("GOT: " + request)
    response = make_response('failure', 200)
    serial_request = 'S' + request + 'E\n'
    for _ in range(5):
        try:
            serial_port.write(serial_request.encode())
            serial_response = serial_port.readline()
        except:
            os._exit(1)
            
        try:
            serial_response = serial_response.decode()
            log.write(serial_response)
            log.flush()
        except:
            continue

        if (serial_response == serial_request):
            data = []
            data[:0] = request
            if (len(data) == len(labels)):
                now = millis()
                line = ','.join(data)
                log.write(str(now) + ',' + line + '\n')
                log.flush()
                for l, d in zip(labels, data):
                    bytes = (l + ' ' + l + '=' + d + ' ' + str(now * 1000000)).encode()
                    client.sendto(bytes, addr)
                prev = now
            response = make_response('success', 200)
            break

    response.mimetype = 'text/plain'
    return response

if __name__ == '__main__':
    app.run(debug=True)

"""
@app.route('/config/download/<path:filename>')
def download_file(filename):
    file = '/home/ubuntu/logs/' + filename
    return send_file(file, as_attachment=True)


@app.route('/config/upload')
def download_file(filename):
    file = '/home/ubuntu/logs/' + filename
    return send_file(file, as_attachment=True)
"""


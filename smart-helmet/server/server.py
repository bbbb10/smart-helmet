from flask import Flask, request, jsonify
import serial
import time

app = Flask(__name__)

# 아두이노 시리얼 포트 설정 (환경에 맞는 포트로 변경)
SERIAL_PORT = '/dev/ttyUSB0'  # 아두이노가 연결된 포트 (리눅스 기준)
BAUD_RATE = 9600  # 아두이노 보드와의 통신 속도

# 시리얼 포트 초기화
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

@app.route('/')
def index():
    return "Smart Helmet Data Server is Running!"

@app.route('/data', methods=['GET'])
def get_data():
    try:
        # 아두이노에서 데이터를 읽어오기
        if ser.is_open:
            data = ser.readline().decode('utf-8').strip()  # 아두이노에서 전송한 데이터를 읽기
            if data:
                return jsonify({'status': 'success', 'data': data}), 200
            else:
                return jsonify({'status': 'error', 'message': 'No data received'}), 400
        else:
            return jsonify({'status': 'error', 'message': 'Serial port not open'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/send_data', methods=['POST'])
def send_data():
    try:
        data = request.json  # JSON 형식의 데이터를 받음
        if 'message' in data:
            message = data['message']
            ser.write(message.encode())  # 아두이노로 데이터 전송
            return jsonify({'status': 'success', 'message': f'Message \"{message}\" sent to Arduino'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'No message found in request'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    try:
        # 시리얼 포트 연결 확인
        if ser.is_open:
            print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud")
        else:
            print(f"Failed to connect to {SERIAL_PORT}")
    except Exception as e:
        print(f"Error opening serial port: {e}")

    # 서버 실행
    app.run(host='0.0.0.0', port=5000, debug=True)

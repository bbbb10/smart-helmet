from flask import Flask, request, render_template, jsonify, send_file
from datetime import datetime
import pytz, csv
import numpy as np
import joblib
import boto3
import os
import traceback  # 예외 출력용 추가

app = Flask(__name__)
data = []

# SNS 설정 (미국 리전에서 생성한 주제)
sns_client = boto3.client("sns", region_name="us-east-1")
TOPIC_ARN = "arn:aws:sns:us-east-1:864186153678:impact-alert-us"

# 문자 전송 함수
def send_sms_alert(impact, timestamp, latitude, longitude):
    message = f"""사고 감지 알림
스마트 헬멧이 강한 충격을 감지했습니다.
시간: {timestamp}
충격량: {impact:.2f}
위치: https://www.google.com/maps?q={latitude},{longitude}

즉시 조치를 확인하세요.
"""
    try:
        sns_client.publish(
            TopicArn=TOPIC_ARN,
            Message=message,
            Subject="스마트헬멧 경고"
        )
        print("[DEBUG] 문자 전송 성공")
    except Exception:
        print("[ERROR] 문자 전송 실패:")
        traceback.print_exc()

# 한국 시간 반환
def get_korea_time():
    korea_tz = pytz.timezone('Asia/Seoul')
    return datetime.now(korea_tz).strftime('%Y-%m-%d %H:%M:%S')

# 충격량 계산
def calculate_impact(x, y, z):
    return (x**2 + y**2 + z**2)**0.5

# 머신러닝 모델 로드 (new_shock_model.pkl 사용)
model = joblib.load('new_shock_model.pkl')

# 이메일 알림 (테스트용 출력)
def send_email_alert(message):
    print("[EMAIL ALERT] " + message)

@app.route('/')
def index():
    return render_template('index.html', data=data)

@app.route('/receive', methods=['POST'])
def receive_data():
    global data
    json_data = request.get_json()

    accel_x = float(json_data.get('accel_x', 0))
    accel_y = float(json_data.get('accel_y', 0))
    accel_z = float(json_data.get('accel_z', 0))
    impact = calculate_impact(accel_x, accel_y, accel_z)
    latitude = json_data.get('latitude', 0.0)
    longitude = json_data.get('longitude', 0.0)
    timestamp = get_korea_time()

    input_data = np.array([[accel_x, accel_y, accel_z, impact]])
    prediction = model.predict(input_data)[0]
    label_map = {1: 'Normal', 2: 'Warning', 3: 'Danger'}
    label = label_map.get(prediction, f'Pred: {prediction}')

    print(f"[LOG] 예측: {prediction}, 라벨: {label}, 충격량: {impact:.2f}")

    if prediction == 3:  # Danger 상황
        send_sms_alert(impact, timestamp, latitude, longitude)

        message = f"""스마트 헬멧에서 위험 충격 감지
시간: {timestamp}
충격량: {impact:.2f}
위치: https://www.google.com/maps?q={latitude},{longitude}
"""
        send_email_alert(message)

    data.append({
        'accel_x': accel_x,
        'accel_y': accel_y,
        'accel_z': accel_z,
        'impact': impact,
        'latitude': latitude,
        'longitude': longitude,
        'timestamp': timestamp,
        'label': label
    })

    return jsonify(status="success", prediction=int(prediction), label=label)

@app.route('/label', methods=['POST'])
def label_data():
    index = int(request.form['index'])
    label = request.form['label']
    if 0 <= index < len(data):
        data[index]['label'] = label
    return '', 204

@app.route('/download', methods=['GET'])
def download_csv():
    filename = 'data.csv'
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'accel_x', 'accel_y', 'accel_z', 'impact', 'latitude', 'longitude', 'label'])
        writer.writeheader()
        writer.writerows(data)
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

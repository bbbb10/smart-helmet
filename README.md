# smart-helmet
충격 감지 스마트 헬멧 캡스톤 프로젝트

**-작품 개요 : AI로 사고를 감지해 실시간 구조 요청이 가능한 스마트 헬멧**

이 작품은 사고 발생 시 충격 데이터를 분석해 AI 모델로 사고 여부를 판단하고, 즉시 가족 또는 병원에 알림을 전송하는 사물인터넷 기반 스마트 헬멧입니다. 가속도센서, GPS모듈 등을 통해 사고 발생 위치와 강도를 실시간으로 파악하고, 서버를 통해 분석 후 관제센터에 정보를 전달하는 시스템을 구현했습니다.

**-주요 적용 기술 및 구조**

개발 환경: Windows 10, Ubuntu (AWS EC2 서버), Google Colab

개발 도구: Visual Studio Code, Git Bash

개발 언어: Python, JavaScript

주요 기술: Flask, AWS EC2, AWS SNS  

**-작품 설명**  
1. MPU-6050과 NEO-7M이 충격·위치 데이터를 측정
2. Arduino Nano 33 IoT로 Flask 서버에 실시간 전송
3. 웹페이지에 데이터 실시간 표시, 사용자 수동 라벨링 및 CSV 저장
4. Colab에서 CSV 기반 학습, 충격 분류용 .pkl 모델 생성
5. 위험 충격 감지 시 AWS SNS로 보호자·119에 문자 자동 전송
6. 웹 기반 관제 시스템 연동, 실시간 모니터링 및 상태 확인

**-기대효과**  
교통사고 발생 시 초기 대응 시간은 생명과 직결됩니다. 본 스마트 헬멧은 사고 발생 즉시 충격을 감지하고 정확한 사고 여부를 AI로 판별한 뒤, 관제센터와 보호자에게 실시간으로 알림을 전송합니다. 응급 상황 대응 시간을 줄일 수 있어 생존율 향상에 크게 기여할 수 있습니다. 

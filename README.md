# Sensor Monitor - 실시간 데이터 시각화 애플리케이션

PyQt6를 사용한 실시간 센서 데이터 모니터링 및 가시화 애플리케이션입니다.

## 기능

### 📊 실시간 그래프
- 오실로스코프 스타일의 실시간 선 그래프
- 바 그래프로 변경 가능
- 여러 개의 그래프 창 생성 가능
- 그래프 확대/축소 (+/- 20%)
- 자동 스케일링 또는 수동 범위 지정

### 🔌 Serial 통신
- 여러 개의 Serial 포트 동시 연결
- 데이터 Delimiter 커스터마이징 (기본: ,)
- Connection 상태 표시
- 자동 재연결 기능

### 📈 데이터 채널
- 동적 채널 추가/제거
- 각 채널별 색상 선택
- 채널별 데이터 인덱스 지정
- 채널별 가시성 제어

### 🎨 UI/UX
- Dockable 윈도우 시스템
- Serial 연결 관리 패널
- 그래프 목록 및 속성 편집 패널
- 실시간 로그 윈도우
- 메뉴바 및 도구모음

### 💾 데이터 저장
- Serial 데이터 CSV 파일로 저장
- 로그 내보내기

## 설치 및 실행

### 1. 가상환경 생성 및 활성화
```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

또는 개별 설치:
```bash
pip install PyQt6==6.11.0 pyqtgraph==0.14.0 pyserial==3.5 numpy
```

### 3. 애플리케이션 실행
```bash
# Python3 명령으로 실행
python3 main.py
```

## 프로젝트 구조

```
SensorMonitor/
├── main.py                          # 애플리케이션 진입점
├── requirements.txt                 # 패키지 의존성
├── sensor_monitor/
│   ├── __init__.py
│   ├── utils.py                    # 유틸리티 함수 (설정, 색상, 파일 관리)
│   ├── logger.py                   # 로깅 모듈
│   ├── serial_manager.py           # Serial 통신 관리
│   ├── graph_manager.py            # 그래프 및 채널 관리
│   └── ui/
│       ├── __init__.py
│       ├── dialogs.py              # 팝업 대화창
│       └── main_window.py          # 메인 윈도우
└── venv/                           # 가상환경 (자동 생성)
```

## 사용법

### Serial 연결 추가
1. 좌측 패널 "Serial Connections"에서 "Add" 버튼 클릭
2. Connection Name, Port, Baudrate 설정
3. "OK" 버튼으로 추가

### Graph 생성
1. 우측 패널 "Graphs"에서 "Add" 버튼 클릭
2. 그래프 이름 입력
3. "Channels" 버튼으로 데이터 채널 추가

### 데이터 채널 추가
1. 그래프 선택 후 "Channels" 버튼 클릭
2. Channel Name, Serial Connection, Data Index 설정
3. "Choose Color" 버튼으로 색상 선택
4. "OK" 버튼으로 추가

### 그래프 속성 설정
1. 그래프 선택 후 "Properties" 버튼 클릭
2. 제목, 타입(Line/Bar), X-Range 등 설정
3. Y-Axis 범위 자동/수동 선택
4. "OK" 버튼으로 저장

### 그래프 확대/축소
- 메뉴바의 "Zoom In (+)" 버튼: 20% 좁혀짐 (더 자세히 표시)
- 메뉴바의 "Zoom Out (-)" 버튼: 20% 넓혀짐 (더 넓은 범위 표시)

### 데이터 저장
- 메뉴바의 "Save Data" 버튼으로 현재 데이터를 CSV 파일로 저장

## 주요 클래스

### serial_manager.py
- `SerialConfig`: Serial 연결 설정 데이터
- `SerialWorker`: 별도 스레드에서 Serial 데이터 수신
- `SerialManager`: 여러 Serial 연결 관리

### graph_manager.py
- `DataChannel`: 그래프에 표시할 데이터 채널
- `GraphConfig`: 그래프 설정
- `RealTimeGraph`: 실시간 그래프 표시
- `GraphManager`: 여러 그래프 관리

### logger.py
- `Logger`: GUI에서 표시할 로그 관리

### utils.py
- `ConfigManager`: 설정 저장/로드
- `ColorManager`: 색상 관리
- `FileManager`: 파일 저장
- 데이터 파싱 함수들

## 시스템 요구사항

- Python 3.8 이상
- PyQt6 6.11.0
- pyqtgraph 0.14.0
- pyserial 3.5
- numpy 1.25.0 이상

## 예제: 아두이노 데이터 수신

아두이노에서 다음과 같은 형식으로 데이터를 전송할 수 있습니다:

```
10.5,20.3,15.7
11.2,21.1,16.2
12.0,22.5,17.1
...
```

이 경우:
- Delimiter: `,`
- Serial Connection: COM3 (또는 /dev/ttyUSB0)
- Channel 0: 첫 번째 값 (10.5, 11.2, ...)
- Channel 1: 두 번째 값 (20.3, 21.1, ...)
- Channel 2: 세 번째 값 (15.7, 16.2, ...)

## 라이선스

MIT License

## 기여

버그 리포트와 기능 제안은 언제든 환영합니다.

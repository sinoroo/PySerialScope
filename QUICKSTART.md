# Sensor Monitor - 빠른 시작 가이드

## 📋 시스템 요구사항

- **OS**: Linux, macOS, Windows
- **Python**: 3.8 이상 (기본값: Python3)
- **USB-to-Serial 어댑터** (선택사항 - 시리얼 데이터 수신용)

## 🚀 설치 및 실행 (1분 안에!)

### Linux / macOS

```bash
# 프로젝트 디렉토리로 이동
cd /path/to/SensorMonitor

# 실행 권한 부여 (필요시)
chmod +x run.sh

# 실행
./run.sh
```

### Windows

```cmd
# 프로젝트 디렉토리로 이동
cd path\to\SensorMonitor

# 실행
run.bat
```

### 수동 실행 (모든 플랫폼)

```bash
# 가상환경 생성 (처음 1회만)
python3 -m venv venv

# 가상환경 활성화
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 패키지 설치 (처음 1회만)
pip install -r requirements.txt

# 애플리케이션 실행
python3 main.py
```

## 🧪 기본 기능 테스트

설치 후 기본 기능이 제대로 작동하는지 확인하려면:

```bash
# 가상환경이 활성화된 상태에서
python3 test_basic.py
```

모든 테스트가 통과하면 설치가 완료된 것입니다.

## 📊 처음 사용하기

### 1단계: Serial 연결 설정

**좌측 패널** → "Serial Connections" 
- **"Add" 버튼 클릭**
- Connection Name 입력 (예: "아두이노 온습도센서")
- Port 선택 (COM3, /dev/ttyUSB0 등)
- Baudrate 설정 (대부분의 경우 115200)
- Data Delimiter 설정 (기본: ,)
- **"OK" 버튼**

![Serial Connection Dialog](docs/serial_connection.jpg)

### 2단계: 그래프 생성

**우측 패널** → "Graphs"
- **"Add" 버튼 클릭**
- 그래프 이름 입력 (예: "온도 그래프")
- **그래프가 생성됨**

### 3단계: 데이터 채널 추가

**우측 패널** → 그래프 선택 → **"Channels" 버튼**
- 새 창에서 "Add" 또는 "Create" 클릭
- **Channel Name**: 센서명 (예: "온도센서 #1")
- **Serial Connection**: 연결한 Serial 포트 선택
- **Data Index**: 
  - 데이터가 `25.5,60.3` 형식이면:
    - Index 0 = 25.5 (온도)
    - Index 1 = 60.3 (습도)
- **Color**: "Choose Color" 버튼으로 색상 선택
- **"OK" 버튼**

### 4단계: Serial 연결 활성화

**좌측 패널** → Serial Connections에서 연결 선택 → **"Connect" 버튼**

이제 데이터가 실시간으로 그래프에 표시됩니다!

## 🎯 주요 기능 사용법

### 그래프 확대/축소
- **"Zoom In" (+)**: 그래프가 20% 더 좁혀져 더 자세히 표시됩니다
- **"Zoom Out" (-)**: 그래프가 20% 더 넓혀져 더 넓은 범위를 표시합니다

### 그래프 속성 변경
1. 우측 패널에서 그래프 선택
2. **"Properties" 버튼** 클릭
3. 원하는 속성 변경:
   - **Title**: 그래프 제목
   - **Graph Type**: "Line" (선) 또는 "Bar" (막대)
   - **X-Axis Range**: 표시할 데이터 포인트 개수
   - **Y-Axis Range**: 자동/수동 범위 설정
   - **Grid**: 격자 표시/숨김

### 데이터 저장하기
- 메뉴바의 **"Save Data" 버튼** 클릭
- 저장 위치와 파일명 설정
- CSV 파일로 저장됨

### 로그 보기
- **하단 "Logs" 패널**에서 모든 작업 기록 확인
- **"Export" 버튼**: 로그를 텍스트 파일로 저장

## 📡 아두이노 예제

### 온습도 센서 데이터 전송

```cpp
#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);  // Baudrate 115200으로 설정
  dht.begin();
}

void loop() {
  delay(2000);
  
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  
  // 온도,습도 형식으로 송신
  Serial.print(temperature);
  Serial.print(",");
  Serial.println(humidity);
}
```

앱에서 설정:
- **Delimiter**: `,`
- **Channel 0**: 온도 (Data Index: 0)
- **Channel 1**: 습도 (Data Index: 1)

### 멀티 센서 데이터

```cpp
void loop() {
  // 3개 센서 데이터: 온도, 습도, 기압
  Serial.print(temperature);
  Serial.print(",");
  Serial.print(humidity);
  Serial.print(",");
  Serial.println(pressure);
}
```

## ⚙️ 고급 설정

### 설정 파일 수정

프로젝트 디렉토리에 자동 생성되는 `config.json` 파일을 수정하여 기본값을 설정할 수 있습니다:

```json
{
  "serial_ports": [
    {
      "name": "아두이노",
      "port": "/dev/ttyUSB0",
      "baudrate": 115200,
      "delimiter": ","
    }
  ],
  "graphs": [
    {
      "name": "온도 그래프",
      "channels": [...],
      "x_range": 100
    }
  ]
}
```

## 🐛 문제 해결

### Serial 포트가 표시되지 않음
- USB 드라이버 설치 확인
- 연결된 장치 확인 (`ls /dev/tty*`)
- 포트 권한 확인 (Linux): `ls -la /dev/ttyUSB*`

### 데이터가 수신되지 않음
- Baudrate 확인 (장치와 앱이 같은 값)
- Data Delimiter 확인 (기본: `,`)
- 데이터 형식 확인 (숫자만, Delimiter로 구분)

### 그래프에 데이터가 표시되지 않음
1. 채널의 "Data Index" 확인
2. Serial 연결 상태 확인 (좌측 패널 "✓" 표시)
3. 로그 패널에서 오류 메시지 확인

### 애플리케이션 시작 오류
```bash
# PyQt6 재설치
pip install --force-reinstall PyQt6

# 또는 모든 패키지 재설치
pip install -r requirements.txt --force-reinstall
```

## 📚 파일 설명

| 파일 | 설명 |
|------|------|
| `main.py` | 애플리케이션 진입점 |
| `requirements.txt` | Python 패키지 의존성 |
| `test_basic.py` | 기본 기능 테스트 |
| `sensor_monitor/` | 메인 패키지 폴더 |
| `sensor_monitor/utils.py` | 유틸리티 함수 |
| `sensor_monitor/logger.py` | 로깅 시스템 |
| `sensor_monitor/serial_manager.py` | Serial 통신 관리 |
| `sensor_monitor/graph_manager.py` | 그래프 관리 |
| `sensor_monitor/ui/` | GUI 인터페이스 |
| `sensor_monitor/ui/main_window.py` | 메인 윈도우 |
| `sensor_monitor/ui/dialogs.py` | 팝업 대화창 |

## 💡 팁

1. **여러 그래프 생성**: 온도는 한 그래프에, 습도는 다른 그래프에 표시
2. **색상 설정**: 각 채널을 다른 색으로 설정하여 식별 용이
3. **X-Range 조정**: 더 많은 데이터를 보려면 값을 크게, 자세히 보려면 작게
4. **Auto Scale**: Y-Axis를 "Auto Scale"로 설정하면 데이터 범위에 자동 맞추기
5. **데이터 저장**: 장기 분석용으로 "Save Data"로 정기적 백업

## 🔗 관련 리소스

- [PyQt6 문서](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [pyqtgraph 문서](http://www.pyqtgraph.org/)
- [pyserial 문서](https://pyserial.readthedocs.io/)

## 📞 지원

문제가 발생하면:
1. `test_basic.py` 실행하여 기본 기능 확인
2. 로그 패널에서 오류 메시지 확인
3. README.md에서 추가 정보 확인

---

**Sensor Monitor v1.0** - 실시간 센서 데이터 모니터링 애플리케이션

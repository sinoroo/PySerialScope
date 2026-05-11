# Sensor Monitor - 프로젝트 아키텍처

## 📁 프로젝트 구조

```
SensorMonitor/
│
├── main.py                      # 애플리케이션 진입점
├── test_basic.py               # 기본 기능 테스트
├── run.sh                       # Linux/macOS 실행 스크립트
├── run.bat                      # Windows 실행 스크립트
├── requirements.txt             # Python 패키지 의존성
│
├── README.md                    # 상세 설명서
├── QUICKSTART.md               # 빠른 시작 가이드
├── ARCHITECTURE.md             # 이 파일
│
├── config.json                  # 설정 파일 (자동 생성)
│
├── venv/                        # Python 가상환경
│   └── [가상환경 파일들]
│
└── sensor_monitor/              # 메인 패키지
    │
    ├── __init__.py
    ├── utils.py                 # 유틸리티 함수
    ├── logger.py                # 로깅 시스템
    ├── serial_manager.py        # Serial 통신 관리
    ├── graph_manager.py         # 그래프 관리
    │
    └── ui/                      # GUI 인터페이스
        ├── __init__.py
        ├── main_window.py       # 메인 윈도우 레이아웃
        └── dialogs.py           # 팝업 대화창들
```

## 🏗️ 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────┐
│                   Main Window (QMainWindow)                 │
├─────────────────────────────────────────────────────────────┤
│  Toolbar: [Add Serial] [Add Graph] [Zoom In] [Zoom Out]    │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐ │
│  │ Serial Conn      │  │   Graph Tab      │  │ Graphs    │ │
│  │ Panel (Dock)     │  │   Widget Area    │  │ List      │ │
│  │ ─────────────     │  │ ─────────────     │  │ (Dock)    │ │
│  │ • COM3 ✓         │  │ [Line Graph]     │  │ ─────────  │ │
│  │ • COM4 ✗         │  │ [Add/Remove Tabs]│  │ • Graph1  │ │
│  │ [Add] [Remove]   │  │                  │  │ • Graph2  │ │
│  │ [Connect]        │  │                  │  │ [Add]     │ │
│  │ [Disconnect]     │  │                  │  │ [Remove]  │ │
│  └──────────────────┘  └──────────────────┘  └───────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Logs Panel (Dock)                                          │
│  [INFO  10:30:45] Connected to COM3                         │
│  [OK    10:30:46] Graph "Temperature" created              │
│  [WARN  10:30:47] No data received for 5 seconds           │
└─────────────────────────────────────────────────────────────┘
```

## 📦 모듈 설명

### 1. **utils.py** - 유틸리티 기능

```python
class ConfigManager
├── load_config()       # 설정 파일 로드
├── save_config()       # 설정 저장
├── get()              # 설정값 조회
└── set()              # 설정값 변경

class ColorManager
├── get_color()        # 인덱스로 색상 조회
└── get_all_colors()   # 모든 색상 반환

class FileManager
├── save_data()        # 파일에 데이터 저장
└── create_data_file() # 새 파일 생성

Functions:
├── parse_data()       # CSV 형식 데이터 파싱
├── hex_to_rgb()       # 16진수 색상 → RGB
└── rgb_to_hex()       # RGB → 16진수 색상
```

### 2. **logger.py** - 로깅 시스템

```python
class Logger(QObject)
├── info()             # 정보 메시지
├── warning()          # 경고 메시지
├── error()            # 오류 메시지
├── debug()            # 디버그 메시지
├── success()          # 성공 메시지
├── clear()            # 로그 초기화
├── get_logs()         # 모든 로그 반환
└── count()            # 로그 항목 개수
    │
    └─ Signals: log_signal (로그 메시지 전송)

Function:
└── get_logger()       # 전역 Logger 인스턴스
```

### 3. **serial_manager.py** - Serial 통신

```python
@dataclass
SerialConfig
├── name               # 연결명
├── port               # 포트 (COM3, /dev/ttyUSB0)
├── baudrate           # 통신 속도 (기본: 115200)
├── timeout            # 타임아웃 (기본: 1.0초)
└── delimiter          # 데이터 구분자 (기본: ,)

class SerialWorker(QThread)
├── run()              # 메인 스레드 루프 (데이터 수신)
└── stop()             # 수신 중지
    │
    ├─ Signals:
    │  ├── data_received(name, data)
    │  ├── connection_status_changed(name, bool)
    │  └── error_occurred(name, error_msg)
    │
    └─ Methods: readline(), write()

class SerialManager(QObject)
├── add_connection()        # 연결 추가
├── remove_connection()     # 연결 제거
├── connect()               # 연결 시작
├── disconnect()            # 연결 중지
├── is_connected()          # 연결 상태 확인
├── get_all_connections()   # 모든 연결 반환
└── list_available_ports()  # 사용 가능 포트 목록
```

### 4. **graph_manager.py** - 그래프 관리

```python
@dataclass
DataChannel
├── name                  # 채널명
├── serial_connection     # Serial 연결명
├── channel_index         # 데이터 인덱스 (0, 1, 2...)
├── color                 # 표시 색상
└── visible               # 표시 여부

@dataclass
GraphConfig
├── name                  # 그래프명
├── title                 # 그래프 제목
├── channels              # DataChannel 리스트
├── graph_type            # "line"/"bar"
├── x_range               # X축 범위 (데이터 포인트 수)
├── y_min, y_max          # Y축 범위
├── auto_scale_y          # Y축 자동 스케일링
├── grid_x, grid_y        # 격자 표시
└── [그 외 속성들]

class RealTimeGraph
├── get_plot_widget()           # PyQtGraph PlotWidget 반환
├── add_channel()               # 채널 추가
├── remove_channel()            # 채널 제거
├── add_data()                  # 데이터 포인트 추가
├── clear_data()                # 데이터 삭제
├── set_x_range()               # X축 범위 설정
├── set_y_range()               # Y축 범위 설정
└── toggle_grid()               # 격자 토글

class GraphManager(QObject)
├── create_graph()              # 새 그래프 생성
├── delete_graph()              # 그래프 삭제
├── get_graph()                 # 그래프 조회
├── rename_graph()              # 그래프 이름 변경
├── add_channel_to_graph()      # 채널 추가
├── remove_channel_from_graph() # 채널 제거
├── update_channel_color()      # 채널 색상 변경
└── get_all_graphs()            # 모든 그래프 반환
    │
    └─ Signals:
       ├── graph_added(name)
       └── graph_removed(name)
```

### 5. **ui/dialogs.py** - 팝업 대화창

```python
class SerialConnectionDialog(QDialog)
├── 입력 필드:
│   ├── Connection Name
│   ├── Port
│   ├── Baudrate
│   ├── Timeout
│   └── Data Delimiter
└── Methods: get_config()

class DataChannelDialog(QDialog)
├── 입력 필드:
│   ├── Channel Name
│   ├── Serial Connection
│   ├── Data Index
│   ├── Color
│   └── Visibility
└── Methods: get_channel()

class GraphPropertiesDialog(QDialog)
├── 설정 항목:
│   ├── Title
│   ├── Graph Type (Line/Bar)
│   ├── X-Axis Range
│   ├── Y-Axis Range (Auto/Manual)
│   └── Grid Options
└── Methods: get_config()
```

### 6. **ui/main_window.py** - 메인 윈도우

```python
class SerialConnectionWidget(QWidget)
├── 화면 구성:
│   ├── 연결 목록
│   ├── 추가/삭제 버튼
│   └── 연결/해제 버튼
└── Methods: refresh_connections()

class GraphListWidget(QWidget)
├── 화면 구성:
│   ├── 그래프 목록
│   ├── 추가/삭제 버튼
│   ├── 속성 편집 버튼
│   └── 채널 관리 버튼
└── Methods: 
    ├── refresh_graphs()
    ├── add_graph()
    ├── edit_properties()
    └── manage_channels()

class LogWidget(QWidget)
├── 화면 구성:
│   ├── 로그 텍스트 영역
│   ├── Clear 버튼
│   └── Export 버튼
└── Signals: add_log(message)

class MainWindow(QMainWindow)
├── 윈도우 구조:
│   ├── Toolbar (메뉴 버튼들)
│   ├── Left Dock (Serial 연결)
│   ├── Central (그래프)
│   ├── Right Dock (그래프 목록)
│   └── Bottom Dock (로그)
└── Methods:
    ├── add_serial_connection()
    ├── add_graph()
    ├── zoom_in/zoom_out()
    ├── save_data()
    └── on_serial_data_received()
```

## 🔄 데이터 흐름

### 시작 시

```
main.py
    ↓
MainWindow.__init__()
    ├─ SerialManager 생성
    ├─ GraphManager 생성
    ├─ Logger 생성
    └─ UI 구성
```

### Serial 데이터 수신

```
SerialWorker.run()
    ↓
데이터 수신 (readline())
    ↓
data_received Signal 발송
    ↓
MainWindow.on_serial_data_received()
    ↓
parse_data() - CSV 파싱
    ↓
GraphManager를 통해 각 그래프의 채널에 데이터 추가
    ↓
RealTimeGraph.add_data() - 그래프 업데이트
    ↓
PyQtGraph 자동 렌더링
```

### 그래프 창 추가

```
사용자: "Add Graph" 클릭
    ↓
GraphListWidget.add_graph()
    ↓
GraphManager.create_graph()
    ↓
MainWindow에서 탭으로 표시
    ↓
그래프 생성 로그 기록
```

## 🎨 UI 컴포넌트 계층

```
QMainWindow (Main)
├── Central Widget
│   └── QHBoxLayout
│       └── GraphTabWidget (그래프 표시 탭들)
│
├── Dock Widget (Left)
│   └── SerialConnectionWidget
│
├── Dock Widget (Right)
│   └── GraphListWidget
│
└── Dock Widget (Bottom)
    └── LogWidget
```

## 🔌 Signal/Slot 연결

```
SerialWorker
├─ data_received()
│  └→ MainWindow.on_serial_data_received()
│
├─ connection_status_changed()
│  └→ SerialConnectionWidget.refresh_connections()
│
└─ error_occurred()
   └→ Logger.error()

GraphManager
├─ graph_added()
│  └→ GraphListWidget.refresh_graphs()
│
└─ graph_removed()
   └→ GraphListWidget.refresh_graphs()

Logger
└─ log_signal()
   └→ LogWidget.add_log()
```

## 🔐 Thread Safety

- **SerialWorker**: QThread에서 실행 (메인 스레드와 안전)
- **Signal/Slot**: Qt Signal을 통한 스레드 간 안전한 통신
- **데이터 버퍼**: 각 그래프에서 독립적으로 관리

## 🚀 성능 최적화

1. **버퍼링**: 그래프당 x_range만큼만 데이터 보관
2. **효율적인 업데이트**: Signal-slot 기반 이벤트 처리
3. **스레드**: Serial 읽기를 별도 스레드에서 처리
4. **메모리**: 오래된 데이터 자동으로 제거

## 📊 확장 가능성

### 새로운 그래프 타입 추가
```python
# graph_manager.py에서 graph_type 추가
def render_graph():
    if self.config.graph_type == "scatter":
        # 산점도 구현
```

### 새로운 Serial 포맷 지원
```python
# utils.py에서 parse_data() 수정
def parse_data(raw_data, format_type="csv"):
    if format_type == "json":
        # JSON 파싱
    elif format_type == "hex":
        # 16진수 파싱
```

### 데이터베이스 저장
```python
# FileManager를 확장하여 DB 지원
class DatabaseManager:
    def save_to_db(self, connection_name, data):
        # 데이터베이스 저장
```

---

**이 아키텍처는 확장성, 유지보수성, 성능을 고려하여 설계되었습니다.**

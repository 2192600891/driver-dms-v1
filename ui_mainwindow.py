from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1560, 980)
        MainWindow.setMinimumSize(QSize(1360, 820))

        self.actionOpen_camera = QAction(MainWindow)
        self.actionOpen_camera.setObjectName("actionOpen_camera")

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.rootLayout = QVBoxLayout(self.centralwidget)
        self.rootLayout.setContentsMargins(20, 16, 20, 16)
        self.rootLayout.setSpacing(14)

        self.headerFrame = QFrame(self.centralwidget)
        self.headerFrame.setObjectName("headerFrame")
        self.headerLayout = QHBoxLayout(self.headerFrame)
        self.headerLayout.setContentsMargins(16, 12, 16, 12)
        self.headerLayout.setSpacing(10)

        self.titleBox = QVBoxLayout()
        self.titleBox.setSpacing(4)

        self.label_title = QLabel(self.headerFrame)
        self.label_title.setObjectName("label_title")
        self.titleBox.addWidget(self.label_title)

        self.label_subtitle = QLabel(self.headerFrame)
        self.label_subtitle.setObjectName("label_subtitle")
        self.titleBox.addWidget(self.label_subtitle)

        self.headerLayout.addLayout(self.titleBox)
        self.headerLayout.addStretch(1)

        self.headerRight = QVBoxLayout()
        self.headerRight.setSpacing(8)

        self.label_header_state = QLabel(self.headerFrame)
        self.label_header_state.setObjectName("label_header_state")
        self.label_header_state.setAlignment(Qt.AlignCenter)
        self.label_header_state.setMinimumSize(QSize(240, 40))
        self.headerRight.addWidget(self.label_header_state)

        self.label_clock = QLabel(self.headerFrame)
        self.label_clock.setObjectName("label_clock")
        self.label_clock.setAlignment(Qt.AlignCenter)
        self.headerRight.addWidget(self.label_clock)

        self.headerLayout.addLayout(self.headerRight)
        self.rootLayout.addWidget(self.headerFrame)

        self.controlFrame = QFrame(self.centralwidget)
        self.controlFrame.setObjectName("controlFrame")
        self.controlLayout = QVBoxLayout(self.controlFrame)
        self.controlLayout.setContentsMargins(14, 12, 14, 12)
        self.controlLayout.setSpacing(10)

        self.sourceRow = QHBoxLayout()
        self.sourceRow.setSpacing(10)

        self.label_source = QLabel(self.controlFrame)
        self.label_source.setObjectName("label_source")
        self.sourceRow.addWidget(self.label_source)

        self.source_combo = QComboBox(self.controlFrame)
        self.source_combo.setObjectName("source_combo")
        self.source_combo.addItem("")
        self.source_combo.addItem("")
        self.source_combo.addItem("")
        self.source_combo.setMinimumHeight(42)
        self.source_combo.setMinimumWidth(120)
        self.sourceRow.addWidget(self.source_combo)

        self.source_path = QLineEdit(self.controlFrame)
        self.source_path.setObjectName("source_path")
        self.source_path.setReadOnly(True)
        self.source_path.setMinimumHeight(42)
        self.sourceRow.addWidget(self.source_path, 1)

        self.btn_select_source = QPushButton(self.controlFrame)
        self.btn_select_source.setObjectName("btn_select_source")
        self.btn_select_source.setMinimumHeight(42)
        self.sourceRow.addWidget(self.btn_select_source)

        self.chk_video_loop = QCheckBox(self.controlFrame)
        self.chk_video_loop.setObjectName("chk_video_loop")
        self.sourceRow.addWidget(self.chk_video_loop)

        self.controlLayout.addLayout(self.sourceRow)

        self.buttonRow = QHBoxLayout()
        self.buttonRow.setSpacing(10)

        self.btn_start = QPushButton(self.controlFrame)
        self.btn_start.setObjectName("btn_start")
        self.btn_start.setMinimumHeight(44)
        self.buttonRow.addWidget(self.btn_start)

        self.btn_stop = QPushButton(self.controlFrame)
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.setMinimumHeight(44)
        self.buttonRow.addWidget(self.btn_stop)

        self.btn_pause = QPushButton(self.controlFrame)
        self.btn_pause.setObjectName("btn_pause")
        self.btn_pause.setMinimumHeight(44)
        self.buttonRow.addWidget(self.btn_pause)

        self.btn_snapshot = QPushButton(self.controlFrame)
        self.btn_snapshot.setObjectName("btn_snapshot")
        self.btn_snapshot.setMinimumHeight(44)
        self.buttonRow.addWidget(self.btn_snapshot)

        self.btn_clear_log = QPushButton(self.controlFrame)
        self.btn_clear_log.setObjectName("btn_clear_log")
        self.btn_clear_log.setMinimumHeight(44)
        self.buttonRow.addWidget(self.btn_clear_log)

        self.buttonRow.addStretch(1)
        self.controlLayout.addLayout(self.buttonRow)

        self.rootLayout.addWidget(self.controlFrame)

        self.contentLayout = QHBoxLayout()
        self.contentLayout.setSpacing(16)

        self.videoFrame = QFrame(self.centralwidget)
        self.videoFrame.setObjectName("videoFrame")
        self.videoLayout = QVBoxLayout(self.videoFrame)
        self.videoLayout.setContentsMargins(12, 12, 12, 12)

        self.label = QLabel(self.videoFrame)
        self.label.setObjectName("label")
        self.label.setMinimumSize(QSize(980, 700))
        self.label.setAlignment(Qt.AlignCenter)
        self.videoLayout.addWidget(self.label)

        self.contentLayout.addWidget(self.videoFrame, 3)

        self.sidePanel = QFrame(self.centralwidget)
        self.sidePanel.setObjectName("sidePanel")
        self.sidePanel.setMinimumSize(QSize(460, 700))
        self.sidePanel.setMaximumWidth(500)
        self.sideLayout = QVBoxLayout(self.sidePanel)
        self.sideLayout.setContentsMargins(0, 0, 0, 0)
        self.sideLayout.setSpacing(12)

        self.fatigueCard = QFrame(self.sidePanel)
        self.fatigueCard.setObjectName("fatigueCard")
        self.fatigueLayout = QVBoxLayout(self.fatigueCard)
        self.fatigueLayout.setContentsMargins(12, 12, 12, 12)
        self.fatigueLayout.setSpacing(10)

        self.fatigueHead = QHBoxLayout()
        self.label_2 = QLabel(self.fatigueCard)
        self.label_2.setObjectName("label_2")
        self.fatigueHead.addWidget(self.label_2)
        self.fatigueHead.addStretch(1)
        self.label_10 = QLabel(self.fatigueCard)
        self.label_10.setObjectName("label_10")
        self.label_10.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.fatigueHead.addWidget(self.label_10)
        self.fatigueLayout.addLayout(self.fatigueHead)

        self.fatigueCount = QHBoxLayout()
        self.label_3 = QLabel(self.fatigueCard)
        self.label_3.setObjectName("label_3")
        self.fatigueCount.addWidget(self.label_3)
        self.label_4 = QLabel(self.fatigueCard)
        self.label_4.setObjectName("label_4")
        self.fatigueCount.addWidget(self.label_4)
        self.fatigueLayout.addLayout(self.fatigueCount)

        self.label_fatigue_meter_title = QLabel(self.fatigueCard)
        self.label_fatigue_meter_title.setObjectName("label_fatigue_meter_title")
        self.fatigueLayout.addWidget(self.label_fatigue_meter_title)

        self.progress_fatigue = QProgressBar(self.fatigueCard)
        self.progress_fatigue.setObjectName("progress_fatigue")
        self.progress_fatigue.setTextVisible(True)
        self.progress_fatigue.setValue(0)
        self.fatigueLayout.addWidget(self.progress_fatigue)

        self.sideLayout.addWidget(self.fatigueCard)

        self.behaviorCard = QFrame(self.sidePanel)
        self.behaviorCard.setObjectName("behaviorCard")
        self.behaviorLayout = QVBoxLayout(self.behaviorCard)
        self.behaviorLayout.setContentsMargins(12, 12, 12, 12)
        self.behaviorLayout.setSpacing(10)

        self.behaviorHead = QHBoxLayout()
        self.label_5 = QLabel(self.behaviorCard)
        self.label_5.setObjectName("label_5")
        self.behaviorHead.addWidget(self.label_5)
        self.behaviorHead.addStretch(1)
        self.label_9 = QLabel(self.behaviorCard)
        self.label_9.setObjectName("label_9")
        self.label_9.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.behaviorHead.addWidget(self.label_9)
        self.behaviorLayout.addLayout(self.behaviorHead)

        self.behaviorTags = QHBoxLayout()
        self.label_6 = QLabel(self.behaviorCard)
        self.label_6.setObjectName("label_6")
        self.label_6.setAlignment(Qt.AlignCenter)
        self.behaviorTags.addWidget(self.label_6)
        self.label_7 = QLabel(self.behaviorCard)
        self.label_7.setObjectName("label_7")
        self.label_7.setAlignment(Qt.AlignCenter)
        self.behaviorTags.addWidget(self.label_7)
        self.label_8 = QLabel(self.behaviorCard)
        self.label_8.setObjectName("label_8")
        self.label_8.setAlignment(Qt.AlignCenter)
        self.behaviorTags.addWidget(self.label_8)
        self.behaviorLayout.addLayout(self.behaviorTags)

        self.behaviorCounts = QHBoxLayout()
        self.label_phone_count = QLabel(self.behaviorCard)
        self.label_phone_count.setObjectName("label_phone_count")
        self.label_phone_count.setAlignment(Qt.AlignCenter)
        self.behaviorCounts.addWidget(self.label_phone_count)
        self.label_smoke_count = QLabel(self.behaviorCard)
        self.label_smoke_count.setObjectName("label_smoke_count")
        self.label_smoke_count.setAlignment(Qt.AlignCenter)
        self.behaviorCounts.addWidget(self.label_smoke_count)
        self.label_drink_count = QLabel(self.behaviorCard)
        self.label_drink_count.setObjectName("label_drink_count")
        self.label_drink_count.setAlignment(Qt.AlignCenter)
        self.behaviorCounts.addWidget(self.label_drink_count)
        self.behaviorLayout.addLayout(self.behaviorCounts)

        self.sideLayout.addWidget(self.behaviorCard)

        self.runtimeCard = QFrame(self.sidePanel)
        self.runtimeCard.setObjectName("runtimeCard")
        self.runtimeLayout = QVBoxLayout(self.runtimeCard)
        self.runtimeLayout.setContentsMargins(12, 12, 12, 12)
        self.runtimeLayout.setSpacing(10)

        self.label_runtime_title = QLabel(self.runtimeCard)
        self.label_runtime_title.setObjectName("label_runtime_title")
        self.runtimeLayout.addWidget(self.label_runtime_title)

        self.runtimeInfoRow = QHBoxLayout()
        self.label_fps = QLabel(self.runtimeCard)
        self.label_fps.setObjectName("label_fps")
        self.runtimeInfoRow.addWidget(self.label_fps)
        self.label_frame_count = QLabel(self.runtimeCard)
        self.label_frame_count.setObjectName("label_frame_count")
        self.runtimeInfoRow.addWidget(self.label_frame_count)
        self.runtimeLayout.addLayout(self.runtimeInfoRow)

        self.label_runtime = QLabel(self.runtimeCard)
        self.label_runtime.setObjectName("label_runtime")
        self.runtimeLayout.addWidget(self.label_runtime)

        self.sideLayout.addWidget(self.runtimeCard)

        self.logCard = QFrame(self.sidePanel)
        self.logCard.setObjectName("logCard")
        self.logLayout = QVBoxLayout(self.logCard)
        self.logLayout.setContentsMargins(12, 12, 12, 12)
        self.logLayout.setSpacing(10)

        self.label_log_title = QLabel(self.logCard)
        self.label_log_title.setObjectName("label_log_title")
        self.logLayout.addWidget(self.label_log_title)

        self.textBrowser = QTextBrowser(self.logCard)
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser.setMinimumHeight(240)
        self.logLayout.addWidget(self.textBrowser)

        self.sideLayout.addWidget(self.logCard, 1)
        self.contentLayout.addWidget(self.sidePanel, 1)

        self.rootLayout.addLayout(self.contentLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 1560, 28))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu.menuAction())
        self.menu.addAction(self.actionOpen_camera)

        MainWindow.setStyleSheet(
            "QMainWindow{background:#0b1220;color:#e2e8f0;font-family:'Microsoft YaHei','PingFang SC';}"
            "QFrame#headerFrame,QFrame#controlFrame,QFrame#videoFrame,QFrame#fatigueCard,QFrame#behaviorCard,QFrame#runtimeCard,QFrame#logCard{background:#111a2d;border:1px solid #233453;border-radius:12px;}"
            "QMenuBar{background:#0f172a;color:#dbeafe;padding:4px 8px;}"
            "QMenuBar::item{padding:5px 10px;border-radius:6px;}"
            "QMenuBar::item:selected{background:#1d4ed8;}"
            "QMenu{background:#111a2d;border:1px solid #233453;}"
            "QLabel#label_title{font-size:28px;font-weight:700;color:#e2e8f0;}"
            "QLabel#label_subtitle{font-size:15px;color:#93a4bf;}"
            "QLabel#label_header_state{font-size:15px;font-weight:700;color:#bbf7d0;background:#133320;border:1px solid #1c6f3f;border-radius:14px;padding:6px 10px;}"
            "QLabel#label_clock{font-size:14px;color:#9db1cf;}"
            "QLabel#label{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0a1326,stop:1 #132848);border:2px solid #2d5bd6;border-radius:12px;color:#8aa0c4;font-size:22px;}"
            "QLabel#label_2,QLabel#label_5,QLabel#label_runtime_title,QLabel#label_log_title{font-size:18px;font-weight:700;color:#dbeafe;}"
            "QLabel#label_10,QLabel#label_9{font-size:14px;color:#bfdbfe;}"
            "QLabel#label_3,QLabel#label_4,QLabel#label_6,QLabel#label_7,QLabel#label_8,QLabel#label_phone_count,QLabel#label_smoke_count,QLabel#label_drink_count,QLabel#label_fps,QLabel#label_frame_count,QLabel#label_runtime{background:#16243d;border:1px solid #2a3d61;border-radius:9px;padding:8px 10px;font-size:14px;color:#d6e3f8;}"
            "QLabel#label_source{font-size:15px;color:#c9d7ee;font-weight:600;}"
            "QLineEdit,QComboBox{background:#16243d;border:1px solid #2a3d61;border-radius:9px;padding:8px 10px;color:#e2e8f0;font-size:14px;}"
            "QComboBox QAbstractItemView{background:#16243d;border:1px solid #2a3d61;color:#e2e8f0;}"
            "QPushButton{background:#2563eb;border:none;border-radius:10px;color:white;padding:10px 18px;font-size:15px;font-weight:700;min-height:42px;}"
            "QPushButton:hover{background:#1d4ed8;}"
            "QPushButton:disabled{background:#435b8a;color:#adc0e2;}"
            "QCheckBox{font-size:14px;color:#cbd5e1;spacing:8px;}"
            "QProgressBar{background:#16243d;border:1px solid #2a3d61;border-radius:9px;text-align:center;color:#dbeafe;font-size:14px;font-weight:700;min-height:24px;}"
            "QProgressBar::chunk{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #22c55e,stop:1 #0ea5e9);border-radius:9px;}"
            "QTextBrowser{background:#0f1b32;border:1px solid #2a3d61;border-radius:9px;padding:8px;color:#d6e3f8;font-size:14px;}"
            "QStatusBar{background:#111a2d;border-top:1px solid #233453;color:#9db1cf;font-size:13px;min-height:24px;}"
        )

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("智驾行为监测控制台")
        self.actionOpen_camera.setText("启动")
        self.label_title.setText("驾驶行为检测系统")
        self.label_subtitle.setText("支持摄像头、图片、视频三种信号源")
        self.label_header_state.setText("系统待机")
        self.label_clock.setText("--:--:--")
        self.label_source.setText("信号源")
        self.source_combo.setItemText(0, "摄像头")
        self.source_combo.setItemText(1, "图片")
        self.source_combo.setItemText(2, "视频")
        self.source_path.setPlaceholderText("当前未选择文件")
        self.btn_select_source.setText("选择文件")
        self.chk_video_loop.setText("视频循环")
        self.btn_start.setText("开始检测")
        self.btn_stop.setText("停止")
        self.btn_pause.setText("暂停")
        self.btn_snapshot.setText("保存截图")
        self.btn_clear_log.setText("清空日志")
        self.label.setText("实时画面")
        self.label_2.setText("疲劳评估")
        self.label_10.setText("状态：正常")
        self.label_3.setText("眨眼：0 次")
        self.label_4.setText("哈欠：0 次")
        self.label_fatigue_meter_title.setText("疲劳等级")
        self.progress_fatigue.setFormat("低风险 0%")
        self.label_5.setText("分心识别")
        self.label_9.setText("提示：未发现异常")
        self.label_6.setText("手机")
        self.label_7.setText("吸烟")
        self.label_8.setText("饮水")
        self.label_phone_count.setText("手机 0")
        self.label_smoke_count.setText("吸烟 0")
        self.label_drink_count.setText("饮水 0")
        self.label_runtime_title.setText("运行信息")
        self.label_fps.setText("FPS：0.0")
        self.label_frame_count.setText("帧数：0")
        self.label_runtime.setText("时长：00:00")
        self.label_log_title.setText("事件日志")
        self.menu.setTitle("设备")

    def printf(self, mes):
        self.textBrowser.append(mes)
        self.cursot = self.textBrowser.textCursor()
        self.textBrowser.moveCursor(self.cursot.End)

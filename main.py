import os
import sys
import time
from datetime import datetime

import cv2
import myframe
import numpy as np
from PySide2 import QtWidgets
from PySide2.QtCore import QTimer
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtWidgets import QFileDialog, QMainWindow

from ui_mainwindow import Ui_MainWindow

EYE_AR_THRESH = 0.15
EYE_AR_CONSEC_FRAMES = 2
MAR_THRESH = 0.65
MOUTH_AR_CONSEC_FRAMES = 3


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.capture = None
        self.mode = "摄像头"
        self.source_file = ""
        self.is_running = False
        self.is_paused = False
        self.current_frame = None
        self.session_start_ts = None
        self.last_frame_ts = None
        self.frame_count = 0
        self.last_behavior_signature = tuple()
        self.eye_counter = 0
        self.blink_total = 0
        self.mouth_counter = 0
        self.yawn_total = 0
        self.action_idle_frames = 0
        self.roll_frames = 0
        self.roll_eye = 0
        self.roll_mouth = 0
        self.phone_count = 0
        self.smoke_count = 0
        self.drink_count = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer)

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

        self.source_combo.currentIndexChanged.connect(self.on_source_type_changed)
        self.btn_select_source.clicked.connect(self.choose_source_file)
        self.btn_start.clicked.connect(self.start_detection)
        self.btn_stop.clicked.connect(self.stop_detection)
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_snapshot.clicked.connect(self.save_snapshot)
        self.btn_clear_log.clicked.connect(self.textBrowser.clear)
        self.actionOpen_camera.triggered.connect(self.start_detection)

        self.update_clock()
        self.reset_ui_state()

    def reset_ui_state(self):
        self.label.setScaledContents(True)
        self.label_header_state.setText("系统待机")
        self.label_10.setText("状态：正常")
        self.label_3.setText("眨眼：0 次")
        self.label_4.setText("哈欠：0 次")
        self.label_6.setText("手机")
        self.label_7.setText("吸烟")
        self.label_8.setText("饮水")
        self.label_9.setText("提示：未发现异常")
        self.label_phone_count.setText("手机 0")
        self.label_smoke_count.setText("吸烟 0")
        self.label_drink_count.setText("饮水 0")
        self.label_fps.setText("FPS：0.0")
        self.label_frame_count.setText("帧数：0")
        self.label_runtime.setText("时长：00:00")
        self.progress_fatigue.setValue(0)
        self.progress_fatigue.setFormat("低风险 0%")
        self.btn_stop.setEnabled(False)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setText("暂停")
        self.btn_snapshot.setEnabled(False)
        self.on_source_type_changed()

    def reset_detection_stats(self):
        self.eye_counter = 0
        self.blink_total = 0
        self.mouth_counter = 0
        self.yawn_total = 0
        self.action_idle_frames = 0
        self.roll_frames = 0
        self.roll_eye = 0
        self.roll_mouth = 0
        self.phone_count = 0
        self.smoke_count = 0
        self.drink_count = 0
        self.frame_count = 0
        self.last_frame_ts = None
        self.session_start_ts = time.time()
        self.last_behavior_signature = tuple()
        self.label_3.setText("眨眼：0 次")
        self.label_4.setText("哈欠：0 次")
        self.label_6.setText("手机")
        self.label_7.setText("吸烟")
        self.label_8.setText("饮水")
        self.label_9.setText("提示：未发现异常")
        self.label_phone_count.setText("手机 0")
        self.label_smoke_count.setText("吸烟 0")
        self.label_drink_count.setText("饮水 0")
        self.label_fps.setText("FPS：0.0")
        self.label_frame_count.setText("帧数：0")
        self.label_runtime.setText("时长：00:00")
        self.progress_fatigue.setValue(0)
        self.progress_fatigue.setFormat("低风险 0%")
        self.label_10.setText("状态：正常")

    def update_clock(self):
        self.label_clock.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def append_log(self, message):
        self.printf(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def on_source_type_changed(self):
        source_type = self.source_combo.currentText()
        self.mode = source_type
        need_file = source_type in ("图片", "视频")
        self.btn_select_source.setEnabled(need_file)
        self.source_path.setEnabled(need_file)
        self.chk_video_loop.setEnabled(source_type == "视频")
        if source_type != "视频":
            self.chk_video_loop.setChecked(False)
        if not need_file:
            self.source_file = ""
            self.source_path.clear()
            self.source_path.setPlaceholderText("当前无需选择文件")
        elif source_type == "图片":
            self.source_path.setPlaceholderText("请选择图片文件")
        else:
            self.source_path.setPlaceholderText("请选择视频文件")

    def choose_source_file(self):
        source_type = self.source_combo.currentText()
        if source_type == "图片":
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择图片文件",
                "",
                "Image Files (*.png *.jpg *.jpeg *.bmp *.webp)"
            )
        elif source_type == "视频":
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择视频文件",
                "",
                "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv)"
            )
        else:
            return

        if file_path:
            self.source_file = file_path
            self.source_path.setText(file_path)
            self.append_log(f"已选择{source_type}源：{os.path.basename(file_path)}")

    @staticmethod
    def load_image_file(path):
        if not path or not os.path.isfile(path):
            return None
        data = np.fromfile(path, dtype=np.uint8)
        if data.size == 0:
            return None
        return cv2.imdecode(data, cv2.IMREAD_COLOR)

    @staticmethod
    def fatigue_level(perclos_score):
        if perclos_score >= 0.38:
            return "高风险", "#ef4444", "状态：疲劳预警"
        if perclos_score >= 0.20:
            return "需关注", "#f59e0b", "状态：需关注"
        return "低风险", "#22c55e", "状态：正常"

    def set_fatigue_progress(self, perclos_score):
        value = int(max(0, min(100, perclos_score * 220)))
        level, color, status_text = self.fatigue_level(perclos_score)
        self.progress_fatigue.setValue(value)
        self.progress_fatigue.setFormat(f"{level} {value}%")
        self.label_10.setText(f"<font color='{color}'>{status_text}</font>")

    def format_elapsed(self, seconds_value):
        s = int(max(0, seconds_value))
        return f"{s // 60:02d}:{s % 60:02d}"

    def start_detection(self):
        self.stop_detection(log_message=False)
        source_type = self.source_combo.currentText()
        self.mode = source_type
        self.reset_detection_stats()

        if source_type in ("图片", "视频") and not self.source_file:
            self.append_log("请先选择输入文件。")
            self.label_header_state.setText("等待文件")
            return

        if source_type == "摄像头":
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                self.capture = None
                self.append_log("摄像头打开失败，请检查设备占用。")
                self.label_header_state.setText("设备异常")
                return
            self.is_running = True
            self.is_paused = False
            self.timer.start(20)
            self.btn_stop.setEnabled(True)
            self.btn_pause.setEnabled(True)
            self.btn_pause.setText("暂停")
            self.btn_snapshot.setEnabled(True)
            self.label_header_state.setText("摄像头检测中")
            self.statusbar.showMessage("摄像头运行中")
            self.append_log("已启动摄像头实时检测。")
            return

        if source_type == "视频":
            self.capture = cv2.VideoCapture(self.source_file)
            if not self.capture.isOpened():
                self.capture = None
                self.append_log("视频打开失败，请更换文件后重试。")
                self.label_header_state.setText("文件异常")
                return
            self.is_running = True
            self.is_paused = False
            self.timer.start(20)
            self.btn_stop.setEnabled(True)
            self.btn_pause.setEnabled(True)
            self.btn_pause.setText("暂停")
            self.btn_snapshot.setEnabled(True)
            self.label_header_state.setText("视频检测中")
            self.statusbar.showMessage("视频播放检测中")
            self.append_log(f"已载入视频：{os.path.basename(self.source_file)}")
            return

        frame = self.load_image_file(self.source_file)
        if frame is None:
            self.append_log("图片读取失败，请更换文件后重试。")
            self.append_log(f"文件检查：{'存在' if os.path.isfile(self.source_file) else '不存在'}")
            self.label_header_state.setText("文件异常")
            return

        self.process_frame(frame)
        self.is_running = False
        self.is_paused = False
        self.btn_stop.setEnabled(False)
        self.btn_pause.setEnabled(False)
        self.btn_snapshot.setEnabled(True)
        self.label_header_state.setText("图片分析完成")
        self.statusbar.showMessage("单帧分析完成")
        self.append_log(f"已完成图片分析：{os.path.basename(self.source_file)}")

    def stop_detection(self, log_message=True):
        if self.timer.isActive():
            self.timer.stop()
        if self.capture is not None:
            if self.capture.isOpened():
                self.capture.release()
            self.capture = None
        was_running = self.is_running or self.is_paused
        self.is_running = False
        self.is_paused = False
        self.btn_stop.setEnabled(False)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setText("暂停")
        self.btn_snapshot.setEnabled(self.current_frame is not None)
        if was_running:
            self.label_header_state.setText("系统待机")
            self.statusbar.showMessage("检测已停止")
            if log_message:
                self.append_log("检测已停止。")

    def toggle_pause(self):
        if not self.is_running:
            self.append_log("当前没有运行中的检测任务。")
            return

        if self.is_paused:
            self.is_paused = False
            self.timer.start(20)
            self.btn_pause.setText("暂停")
            if self.mode == "摄像头":
                self.label_header_state.setText("摄像头检测中")
            else:
                self.label_header_state.setText("视频检测中")
            self.statusbar.showMessage("检测继续运行")
            self.append_log("检测已继续。")
        else:
            self.is_paused = True
            self.timer.stop()
            self.btn_pause.setText("继续")
            self.label_header_state.setText("检测暂停")
            self.statusbar.showMessage("检测已暂停")
            self.append_log("检测已暂停。")

    def save_snapshot(self):
        if self.current_frame is None:
            self.append_log("当前没有可保存的画面。")
            return
        os.makedirs("captures", exist_ok=True)
        prefix = "camera"
        if self.mode == "视频":
            prefix = "video"
        elif self.mode == "图片":
            prefix = "image"
        filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        output_path = os.path.join("captures", filename)
        cv2.imwrite(output_path, self.current_frame)
        self.append_log(f"截图已保存：{output_path}")

    def update_runtime_metrics(self):
        now = time.time()
        self.frame_count += 1
        if self.last_frame_ts is not None:
            fps = 1.0 / max(1e-6, now - self.last_frame_ts)
            self.label_fps.setText(f"FPS：{fps:.1f}")
        self.last_frame_ts = now
        elapsed = now - self.session_start_ts if self.session_start_ts else 0
        self.label_frame_count.setText(f"帧数：{self.frame_count}")
        self.label_runtime.setText(f"时长：{self.format_elapsed(elapsed)}")

    def update_behavior_ui(self, detected):
        if "phone" in detected:
            self.phone_count += 1
            self.label_6.setText("<font color='#ef4444'>手机（检测到）</font>")
        if "smoke" in detected:
            self.smoke_count += 1
            self.label_7.setText("<font color='#ef4444'>吸烟（检测到）</font>")
        if "drink" in detected:
            self.drink_count += 1
            self.label_8.setText("<font color='#ef4444'>饮水（检测到）</font>")

        if detected:
            if "phone" in detected:
                self.label_9.setText("<font color='#ef4444'>提示：请勿使用手机</font>")
            elif "smoke" in detected:
                self.label_9.setText("<font color='#ef4444'>提示：请勿吸烟分心</font>")
            elif "drink" in detected:
                self.label_9.setText("<font color='#f59e0b'>提示：请关注前方路况</font>")

        self.label_phone_count.setText(f"手机 {self.phone_count}")
        self.label_smoke_count.setText(f"吸烟 {self.smoke_count}")
        self.label_drink_count.setText(f"饮水 {self.drink_count}")

    def reset_behavior_ui(self):
        self.label_6.setText("手机")
        self.label_7.setText("吸烟")
        self.label_8.setText("饮水")
        self.label_9.setText("提示：未发现异常")

    def update_fatigue_metrics(self, eye_value, mouth_value):
        if eye_value < EYE_AR_THRESH:
            self.eye_counter += 1
            self.roll_eye += 1
        else:
            if self.eye_counter >= EYE_AR_CONSEC_FRAMES:
                self.blink_total += 1
            self.eye_counter = 0

        if mouth_value > MAR_THRESH:
            self.mouth_counter += 1
            self.roll_mouth += 1
        else:
            if self.mouth_counter >= MOUTH_AR_CONSEC_FRAMES:
                self.yawn_total += 1
            self.mouth_counter = 0

        self.label_3.setText(f"眨眼：{self.blink_total} 次")
        self.label_4.setText(f"哈欠：{self.yawn_total} 次")

        self.roll_frames += 1
        perclos_value = (self.roll_eye / max(1, self.roll_frames)) + (self.roll_mouth / max(1, self.roll_frames)) * 0.2
        level, _, _ = self.fatigue_level(perclos_value)
        self.set_fatigue_progress(perclos_value)

        if self.roll_frames >= 150:
            if level == "高风险":
                self.append_log("疲劳评估：高风险，建议立即休息。")
                if self.is_running:
                    self.label_header_state.setText("疲劳预警")
            elif level == "需关注":
                self.append_log("疲劳评估：需关注，建议短暂放松。")
            else:
                self.append_log("疲劳评估：低风险，状态稳定。")
            self.roll_frames = 0
            self.roll_eye = 0
            self.roll_mouth = 0

    def process_frame(self, frame):
        ret, output_frame = myframe.frametest(frame)
        detected_labels, eye_value, mouth_value = ret
        detected = tuple(sorted(set(detected_labels)))

        self.update_runtime_metrics()
        self.update_fatigue_metrics(eye_value, mouth_value)

        self.action_idle_frames += 1
        if detected:
            self.action_idle_frames = 0
            self.update_behavior_ui(detected)
            if detected != self.last_behavior_signature:
                self.append_log("检测到分心行为：" + " / ".join(detected))
        elif self.action_idle_frames >= 15:
            self.reset_behavior_ui()
            self.action_idle_frames = 0

        self.last_behavior_signature = detected

        rgb = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb.data, rgb.shape[1], rgb.shape[0], QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qimg))
        self.current_frame = output_frame.copy()

    def on_timer(self):
        if not self.is_running or self.is_paused or self.capture is None:
            return

        ok, frame = self.capture.read()
        if not ok:
            if self.mode == "视频" and self.chk_video_loop.isChecked():
                self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.append_log("视频已循环播放。")
                return

            if self.mode == "视频":
                self.append_log("视频播放结束。")
            else:
                self.append_log("摄像头读取失败，检测停止。")
            self.stop_detection(log_message=False)
            return

        self.process_frame(frame)

    def closeEvent(self, event):
        self.stop_detection(log_message=False)
        event.accept()


def CamConfig_init():
    window.start_detection()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

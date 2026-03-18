import base64
import threading
import time
import uuid
from collections import deque

import cv2
import numpy as np

import mydetect
import myframe

EYE_AR_THRESH = 0.15
EYE_AR_CONSEC_FRAMES = 2
MAR_THRESH = 0.65
MOUTH_AR_CONSEC_FRAMES = 3


class MonitorSession:
    def __init__(self, session_id=None):
        self.session_id = session_id or uuid.uuid4().hex
        self.logs = deque(maxlen=12)
        self.reset()

    def reset(self):
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
        self.current_hint = "提示：未发现异常"
        self.current_state = "状态：正常"

    @staticmethod
    def fatigue_level(perclos_score):
        if perclos_score >= 0.38:
            return "高风险", "状态：疲劳预警"
        if perclos_score >= 0.20:
            return "需关注", "状态：需关注"
        return "低风险", "状态：正常"

    @staticmethod
    def format_elapsed(seconds_value):
        seconds_value = int(max(0, seconds_value))
        return f"{seconds_value // 60:02d}:{seconds_value % 60:02d}"

    def append_log(self, message):
        stamp = time.strftime("%H:%M:%S")
        self.logs.appendleft(f"[{stamp}] {message}")

    def update_runtime_metrics(self):
        now = time.time()
        self.frame_count += 1
        fps = 0.0
        if self.last_frame_ts is not None:
            fps = 1.0 / max(1e-6, now - self.last_frame_ts)
        self.last_frame_ts = now
        elapsed = now - self.session_start_ts
        return {
            "fps": round(fps, 2),
            "frame_count": self.frame_count,
            "runtime_seconds": round(elapsed, 2),
            "runtime_text": self.format_elapsed(elapsed),
        }

    def update_behavior(self, detected):
        behavior_state = {
            "phone_active": False,
            "smoke_active": False,
            "drink_active": False,
        }
        if "phone" in detected:
            self.phone_count += 1
            behavior_state["phone_active"] = True
        if "smoke" in detected:
            self.smoke_count += 1
            behavior_state["smoke_active"] = True
        if "drink" in detected:
            self.drink_count += 1
            behavior_state["drink_active"] = True

        if detected:
            if "phone" in detected:
                self.current_hint = "提示：请勿使用手机"
            elif "smoke" in detected:
                self.current_hint = "提示：请勿吸烟分心"
            elif "drink" in detected:
                self.current_hint = "提示：请关注前方路况"
        elif self.action_idle_frames >= 15:
            self.current_hint = "提示：未发现异常"

        behavior_state["phone_count"] = self.phone_count
        behavior_state["smoke_count"] = self.smoke_count
        behavior_state["drink_count"] = self.drink_count
        behavior_state["hint"] = self.current_hint
        return behavior_state

    def update_fatigue(self, eye_value, mouth_value):
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

        self.roll_frames += 1
        perclos_value = (
            (self.roll_eye / max(1, self.roll_frames))
            + (self.roll_mouth / max(1, self.roll_frames)) * 0.2
        )
        level, state_text = self.fatigue_level(perclos_value)
        self.current_state = state_text

        if self.roll_frames >= 150:
            if level == "高风险":
                self.append_log("疲劳评估：高风险，建议立即休息。")
            elif level == "需关注":
                self.append_log("疲劳评估：需关注，建议短暂放松。")
            else:
                self.append_log("疲劳评估：低风险，状态稳定。")
            self.roll_frames = 0
            self.roll_eye = 0
            self.roll_mouth = 0

        return {
            "eye_value": eye_value,
            "mouth_value": mouth_value,
            "blink_total": self.blink_total,
            "yawn_total": self.yawn_total,
            "perclos_value": round(perclos_value, 4),
            "fatigue_level": level,
            "fatigue_percent": int(max(0, min(100, perclos_value * 220))),
            "state_text": self.current_state,
        }


class InferenceEngine:
    def __init__(self):
        self._lock = threading.Lock()

    @staticmethod
    def decode_image(image_data):
        payload = image_data.split(",", 1)[1] if image_data.startswith("data:") else image_data
        image_bytes = base64.b64decode(payload)
        array = np.frombuffer(image_bytes, dtype=np.uint8)
        frame = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("无法解析上传图像")
        return frame

    @staticmethod
    def encode_jpeg(frame, quality=75):
        ok, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        if not ok:
            raise ValueError("无法编码标注图像")
        return base64.b64encode(buffer.tobytes()).decode("ascii")

    def process_frame(self, frame, session, include_preview=False):
        with self._lock:
            ret, annotated = myframe.frametest(frame.copy())

        detected_labels, eye_value, mouth_value = ret
        detected = tuple(sorted(set(detected_labels)))

        runtime = session.update_runtime_metrics()
        fatigue = session.update_fatigue(eye_value, mouth_value)

        session.action_idle_frames += 1
        if detected:
            session.action_idle_frames = 0
            if detected != session.last_behavior_signature:
                session.append_log("检测到分心行为：" + " / ".join(detected))
        behavior = session.update_behavior(detected)
        session.last_behavior_signature = detected

        payload = {
            "session_id": session.session_id,
            "labels": list(detected),
            "runtime": runtime,
            "fatigue": fatigue,
            "behavior": behavior,
            "logs": list(session.logs),
            "runtime_info": mydetect.runtime_info(),
        }
        if include_preview:
            payload["preview_jpeg"] = self.encode_jpeg(annotated)
        return payload


class SessionStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._sessions = {}

    def get(self, session_id=None):
        with self._lock:
            if session_id and session_id in self._sessions:
                return self._sessions[session_id]
            session = MonitorSession(session_id=session_id)
            self._sessions[session.session_id] = session
            return session

    def drop(self, session_id):
        with self._lock:
            self._sessions.pop(session_id, None)

import base64
import time
from typing import Any

import cv2
import mediapipe as mp
import numpy as np


class MediaAnalysisService:
    def __init__(self) -> None:
        self.mp_face = mp.solutions.face_mesh.FaceMesh(
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.mp_face_detection = mp.solutions.face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.5,
        )
        self._looking_away_started_at: float | None = None

    def _empty_result(self, warning: str, camera_disconnected: bool = False) -> dict[str, Any]:
        return {
            "timestamp": time.time(),
            "face_detected": False,
            "eye_contact_percentage": 0,
            "head_pose": "Straight",
            "looking_away": True,
            "looking_away_duration": 0.0,
            "warnings": [warning] if warning else [],
            "camera_disconnected": camera_disconnected,
            "face_landmarks": {},
            "eye_landmarks": {},
            "iris_landmarks": {},
            "face_count": 0,
            "filler_words": 0,
            "speaking_speed": 0.0,
        }

    def analyze_frame(self, frame: Any) -> dict[str, Any]:
        if frame is None:
            return self._empty_result("Camera disconnected", camera_disconnected=True)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detection_results = self.mp_face_detection.process(rgb)
        mesh_results = self.mp_face.process(rgb)

        detections = detection_results.detections if detection_results else []
        landmarks = mesh_results.multi_face_landmarks if mesh_results else []
        face_count = len(detections) if detections else len(landmarks)
        if face_count == 0:
            return self._empty_result("Face disappeared")

        face_landmarks = landmarks[0].landmark if landmarks else None
        if face_landmarks is None:
            return self._empty_result("Face landmarks unavailable")

        height, width = frame.shape[:2]
        eye_points = self._extract_eye_and_iris_points(face_landmarks, width, height)
        eye_contact = self._estimate_eye_contact(eye_points)
        head_pose = self._estimate_head_pose(eye_points)
        looking_away = eye_contact < 60 or head_pose in {"Head Left", "Head Right", "Head Down"}

        now = time.time()
        if looking_away:
            if self._looking_away_started_at is None:
                self._looking_away_started_at = now
            away_duration = round(now - self._looking_away_started_at, 2)
        else:
            self._looking_away_started_at = None
            away_duration = 0.0

        warnings: list[str] = []
        if face_count > 1:
            warnings.append("Multiple faces detected")
        if away_duration > 5:
            warnings.append("Candidate looks away for more than 5 seconds")

        return {
            "timestamp": now,
            "face_detected": True,
            "eye_contact_percentage": max(0, min(100, eye_contact)),
            "head_pose": head_pose,
            "looking_away": looking_away,
            "looking_away_duration": away_duration,
            "warnings": warnings,
            "camera_disconnected": False,
            "face_landmarks": {
                "nose_tip": self._point_to_dict(face_landmarks[1], width, height),
                "left_eye": self._point_to_dict(face_landmarks[159], width, height),
                "right_eye": self._point_to_dict(face_landmarks[386], width, height),
                "mouth_center": self._point_to_dict(face_landmarks[13], width, height),
            },
            "eye_landmarks": eye_points["eye_landmarks"],
            "iris_landmarks": eye_points["iris_landmarks"],
            "face_count": face_count,
            "filler_words": 0,
            "speaking_speed": 0.0,
        }

    def analyze_image_data(self, image_data: str | bytes | None) -> dict[str, Any]:
        if not image_data:
            return self._empty_result("Camera disconnected", camera_disconnected=True)

        if isinstance(image_data, str) and image_data.startswith("data:image"):
            header, encoded = image_data.split(",", 1)
            if ";base64" not in header:
                return self._empty_result("Unsupported image payload", camera_disconnected=True)
            image_bytes = base64.b64decode(encoded)
        elif isinstance(image_data, str):
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data

        try:
            array = np.frombuffer(image_bytes, dtype=np.uint8)
            frame = cv2.imdecode(array, cv2.IMREAD_COLOR)
        except Exception:
            return self._empty_result("Failed to decode uploaded frame", camera_disconnected=True)

        if frame is None:
            return self._empty_result("Failed to decode uploaded frame", camera_disconnected=True)
        return self.analyze_frame(frame)

    def _extract_eye_and_iris_points(self, landmarks: list[Any], width: int, height: int) -> dict[str, Any]:
        left_eye = [
            landmarks[159] if len(landmarks) > 159 else landmarks[0],
            landmarks[145] if len(landmarks) > 145 else landmarks[0],
            landmarks[133] if len(landmarks) > 133 else landmarks[0],
        ]
        right_eye = [
            landmarks[386] if len(landmarks) > 386 else landmarks[0],
            landmarks[374] if len(landmarks) > 374 else landmarks[0],
            landmarks[362] if len(landmarks) > 362 else landmarks[0],
        ]
        left_iris = landmarks[468] if len(landmarks) > 468 else landmarks[0]
        right_iris = landmarks[473] if len(landmarks) > 473 else landmarks[0]

        eye_landmarks = {
            "left": [self._point_to_dict(point, width, height) for point in left_eye],
            "right": [self._point_to_dict(point, width, height) for point in right_eye],
        }
        iris_landmarks = {
            "left": self._point_to_dict(left_iris, width, height),
            "right": self._point_to_dict(right_iris, width, height),
        }
        return {"eye_landmarks": eye_landmarks, "iris_landmarks": iris_landmarks}

    def _estimate_eye_contact(self, eye_points: dict[str, Any]) -> int:
        left_iris = eye_points["iris_landmarks"]["left"]
        right_iris = eye_points["iris_landmarks"]["right"]
        avg_x = (left_iris["x"] + right_iris["x"]) / 2
        avg_y = (left_iris["y"] + right_iris["y"]) / 2
        deviation = abs(avg_x - 0.5) * 100 + abs(avg_y - 0.5) * 100
        return int(max(0, min(100, 100 - deviation)))

    def _estimate_head_pose(self, eye_points: dict[str, Any]) -> str:
        left_iris = eye_points["iris_landmarks"]["left"]
        right_iris = eye_points["iris_landmarks"]["right"]
        horizontal = ((left_iris["x"] + right_iris["x"]) / 2) - 0.5
        vertical = ((left_iris["y"] + right_iris["y"]) / 2) - 0.5
        if abs(horizontal) > 0.08:
            return "Head Left" if horizontal < 0 else "Head Right"
        if abs(vertical) > 0.08:
            return "Head Up" if vertical < 0 else "Head Down"
        return "Straight"

    def _point_to_dict(self, point: Any, width: int, height: int) -> dict[str, float]:
        return {
            "x": round(point.x, 4),
            "y": round(point.y, 4),
            "z": round(point.z, 4),
        }

"""
Synthetic Video and Dataset Generator for Road Accident Detection.
Simulates realistic vehicle trajectories, decelerations, orientation changes,
collision impacts, and post-collision immobility under diverse environmental conditions.
"""

import os
import math
import random
import json
import numpy as np
import cv2
from typing import List, Dict, Tuple, Any

class VehicleSim:
    def __init__(
        self,
        vehicle_id: int,
        x: float,
        y: float,
        vx: float,
        vy: float,
        width: int = 40,
        height: int = 70,
        color: Tuple[int, int, int] = (220, 50, 50),
        vehicle_type: str = "car"
    ):
        self.vehicle_id = vehicle_id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.width = width
        self.height = height
        self.color = color
        self.angle = 0.0  # degrees
        self.vehicle_type = vehicle_type
        self.is_immobile = False
        self.immobility_counter = 0
        self.trajectory_history: List[Tuple[float, float]] = [(x, y)]
        self.velocity_history: List[float] = [math.hypot(vx, vy)]
        self.orientation_history: List[float] = [0.0]
        self.deceleration_history: List[float] = [0.0]

    def get_speed(self) -> float:
        return math.hypot(self.vx, self.vy)

    def update(self, ax: float = 0.0, ay: float = 0.0, d_angle: float = 0.0, dt: float = 0.1):
        if not self.is_immobile:
            v_prev = self.get_speed()
            self.vx += ax * dt
            self.vy += ay * dt
            self.x += self.vx * dt
            self.y += self.vy * dt
            self.angle = (self.angle + d_angle) % 360.0
            v_curr = self.get_speed()
            decel = max(0.0, (v_prev - v_curr) / dt)

            # Check if stopped
            if v_curr < 0.5:
                self.is_immobile = True
                self.vx = 0.0
                self.vy = 0.0
                self.immobility_counter += 1
        else:
            self.immobility_counter += 1
            v_curr = 0.0
            decel = 0.0

        self.trajectory_history.append((self.x, self.y))
        if len(self.trajectory_history) > 60:
            self.trajectory_history.pop(0)

        self.velocity_history.append(v_curr)
        if len(self.velocity_history) > 60:
            self.velocity_history.pop(0)

        self.orientation_history.append(self.angle)
        if len(self.orientation_history) > 60:
            self.orientation_history.pop(0)

        self.deceleration_history.append(decel)
        if len(self.deceleration_history) > 60:
            self.deceleration_history.pop(0)


def draw_roadway(frame: np.ndarray, width: int, height: int, weather: str = "clear"):
    # Road surface
    road_left = int(width * 0.18)
    road_right = int(width * 0.82)
    cv2.rectangle(frame, (0, 0), (width, height), (40, 95, 45), -1)  # Green grass roadside
    cv2.rectangle(frame, (road_left, 0), (road_right, height), (45, 45, 48), -1)  # Asphalt

    # Road shoulder lines
    cv2.line(frame, (road_left, 0), (road_left, height), (240, 240, 240), 4)
    cv2.line(frame, (road_right, 0), (road_right, height), (240, 240, 240), 4)

    # Lane markings (dashed white)
    lane_width = (road_right - road_left) / 3.0
    for lane_idx in (1, 2):
        lx = int(road_left + lane_idx * lane_width)
        for y_dash in range(0, height, 40):
            cv2.line(frame, (lx, y_dash), (lx, y_dash + 20), (220, 220, 220), 2)

    # Weather effects
    if weather == "rain":
        # Add rain streaks
        for _ in range(120):
            rx = random.randint(0, width - 1)
            ry = random.randint(0, height - 1)
            cv2.line(frame, (rx, ry), (rx - 2, ry + 8), (190, 205, 220), 1)
    elif weather == "night":
        # Darken entire frame
        frame[:] = (frame * 0.45).astype(np.uint8)
        # Add street lamps illumination pools
        for ly in range(60, height, 180):
            cv2.circle(frame, (road_left - 15, ly), 45, (80, 110, 130), -1)
            cv2.circle(frame, (road_right + 15, ly), 45, (80, 110, 130), -1)


def draw_vehicle(frame: np.ndarray, vehicle: VehicleSim):
    cx, cy = int(vehicle.x), int(vehicle.y)
    w, h = vehicle.width, vehicle.height
    angle = vehicle.angle

    # Compute rotated rectangle
    rect = ((cx, cy), (w, h), angle)
    box = cv2.boxPoints(rect)
    box = np.int32(box)

    # Draw body
    cv2.drawContours(frame, [box], 0, vehicle.color, -1)
    cv2.drawContours(frame, [box], 0, (20, 20, 20), 2)

    # Windshield / Headlights indicator to show orientation
    rad = math.radians(angle)
    # Forward vector
    fx = math.sin(rad) * (h * 0.35)
    fy = -math.cos(rad) * (h * 0.35)
    wx, wy = int(cx + fx), int(cy + fy)
    cv2.circle(frame, (wx, wy), 5, (230, 240, 255), -1)

    # ID label
    cv2.putText(
        frame,
        f"V{vehicle.vehicle_id}",
        (cx - 15, cy - int(h * 0.55)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1
    )


def generate_scenario_video(
    output_path: str,
    scenario_type: str = "normal",
    total_frames: int = 150,
    fps: int = 25,
    width: int = 640,
    height: int = 480,
    weather: str = "clear"
) -> Dict[str, Any]:
    """
    Generates an annotated MP4 video representing normal traffic or accident scenario.
    Returns metadata with frame-by-frame ground truth.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    road_left = int(width * 0.18)
    road_right = int(width * 0.82)
    lane_width = (road_right - road_left) / 3.0
    lane_centers = [
        road_left + lane_width * 0.5,
        road_left + lane_width * 1.5,
        road_left + lane_width * 2.5
    ]

    vehicles: List[VehicleSim] = []
    metadata_frames = []

    # Initialize vehicles based on scenario
    if scenario_type == "normal":
        vehicles.append(VehicleSim(1, lane_centers[0], height * 0.85, 0, -110, color=(50, 100, 220)))
        vehicles.append(VehicleSim(2, lane_centers[1], height * 0.65, 0, -95, color=(50, 180, 70)))
        vehicles.append(VehicleSim(3, lane_centers[2], height * 0.40, 0, -105, color=(200, 140, 30)))
        vehicles.append(VehicleSim(4, lane_centers[1], height * 0.95, 0, -90, color=(140, 50, 180)))
    elif scenario_type == "sudden_brake_normal":
        # Hard braking but recovers, no collision, stays in lane
        vehicles.append(VehicleSim(1, lane_centers[1], height * 0.75, 0, -120, color=(60, 120, 220)))
        vehicles.append(VehicleSim(2, lane_centers[1], height * 0.45, 0, -110, color=(210, 60, 60)))
        vehicles.append(VehicleSim(3, lane_centers[0], height * 0.85, 0, -100, color=(40, 180, 80)))
    elif scenario_type == "high_speed_collision":
        # Vehicle 1 drifts into Vehicle 2, sudden deceleration, spinout, immobility
        vehicles.append(VehicleSim(1, lane_centers[0] + 10, height * 0.75, 25, -135, color=(220, 40, 40)))
        vehicles.append(VehicleSim(2, lane_centers[1] - 10, height * 0.50, 0, -80, color=(40, 100, 220)))
        vehicles.append(VehicleSim(3, lane_centers[2], height * 0.85, 0, -100, color=(50, 180, 60)))
    elif scenario_type == "rollover_spinout":
        # Vehicle 1 loses control, rotates 90 deg, flips sideways, stops in center
        vehicles.append(VehicleSim(1, lane_centers[1], height * 0.80, 0, -140, color=(220, 50, 180)))
        vehicles.append(VehicleSim(2, lane_centers[0], height * 0.90, 0, -90, color=(40, 160, 220)))
        vehicles.append(VehicleSim(3, lane_centers[2], height * 0.35, 0, -85, color=(200, 150, 30)))
    elif scenario_type == "adverse_weather_accident":
        # Wet road, vehicle skids, rotates, hits roadside barrier
        vehicles.append(VehicleSim(1, lane_centers[2], height * 0.80, -30, -130, color=(220, 80, 30)))
        vehicles.append(VehicleSim(2, lane_centers[1], height * 0.60, 0, -75, color=(70, 70, 220)))

    accident_frame_idx = -1
    collision_occurred = False

    dt = 1.0 / fps

    for f_idx in range(total_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        draw_roadway(frame, width, height, weather=weather)

        # Dynamic behavior according to scenario
        if scenario_type == "normal":
            # Flow smoothly, wrap around top
            for v in vehicles:
                v.update(dt=dt)
                if v.y < -50:
                    v.y = height + 30

        elif scenario_type == "sudden_brake_normal":
            for v in vehicles:
                if v.vehicle_id == 1:
                    if 45 <= f_idx <= 75:
                        # Hard deceleration (braking)
                        v.update(ay=80.0, dt=dt)
                    elif f_idx > 75:
                        # Accelerate back to normal flow
                        v.update(ay=-40.0 if v.vy > -100 else 0.0, dt=dt)
                    else:
                        v.update(dt=dt)
                else:
                    v.update(dt=dt)
                if v.y < -50:
                    v.y = height + 30

        elif scenario_type == "high_speed_collision":
            v1 = vehicles[0]
            v2 = vehicles[1]
            dist = math.hypot(v1.x - v2.x, v1.y - v2.y)

            if dist < 45 and not collision_occurred:
                collision_occurred = True
                accident_frame_idx = f_idx

            if collision_occurred:
                # Impact reaction
                v1.update(ax=-15.0, ay=180.0, d_angle=18.0, dt=dt)
                v2.update(ax=25.0, ay=150.0, d_angle=-12.0, dt=dt)
            else:
                # Move closer
                v1.update(ax=12.0, dt=dt)
                v2.update(dt=dt)

            # Background traffic
            vehicles[2].update(dt=dt)

        elif scenario_type == "rollover_spinout":
            v1 = vehicles[0]
            if f_idx >= 35 and not collision_occurred:
                collision_occurred = True
                accident_frame_idx = f_idx

            if collision_occurred:
                # Spin and flip
                if abs(v1.angle - 90.0) > 5.0 and v1.get_speed() > 5.0:
                    v1.update(ax=-10.0, ay=190.0, d_angle=22.0, dt=dt)
                else:
                    v1.update(ay=220.0, dt=dt)
            else:
                v1.update(dt=dt)

            for v in vehicles[1:]:
                v.update(dt=dt)
                if v.y < -50:
                    v.y = height + 30

        elif scenario_type == "adverse_weather_accident":
            v1 = vehicles[0]
            if f_idx >= 30:
                collision_occurred = True
                if accident_frame_idx == -1:
                    accident_frame_idx = f_idx
                # Skid towards left barrier
                v1.update(ax=-45.0, ay=140.0, d_angle=14.0, dt=dt)
            else:
                v1.update(dt=dt)

            vehicles[1].update(dt=dt)

        # Draw all vehicles on frame
        frame_boxes = []
        frame_cues = []
        for v in vehicles:
            draw_vehicle(frame, v)
            # Box [x1, y1, x2, y2]
            w_half = v.width * 0.6
            h_half = v.height * 0.6
            box = [
                max(0.0, v.x - w_half),
                max(0.0, v.y - h_half),
                min(float(width), v.x + w_half),
                min(float(height), v.y + h_half)
            ]
            frame_boxes.append({
                "vehicle_id": v.vehicle_id,
                "box": box,
                "speed": round(v.get_speed(), 2),
                "deceleration": round(v.deceleration_history[-1], 2),
                "angle": round(v.angle, 2),
                "is_immobile": v.is_immobile,
                "immobility_sec": round(v.immobility_counter * dt, 2)
            })

        # Save frame
        out.write(frame)

        is_accident_active = collision_occurred and (f_idx >= accident_frame_idx)
        metadata_frames.append({
            "frame_idx": f_idx,
            "timestamp_sec": round(f_idx * dt, 2),
            "is_accident": is_accident_active,
            "vehicles": frame_boxes
        })

    out.release()

    meta = {
        "scenario_type": scenario_type,
        "video_path": output_path,
        "weather": weather,
        "total_frames": total_frames,
        "fps": fps,
        "accident_frame_idx": accident_frame_idx,
        "frames": metadata_frames
    }

    meta_path = output_path.replace(".mp4", "_meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    return meta


def build_default_dataset_suite(base_dir: str = "data"):
    """
    Builds the standard test and benchmark suite covering:
    - Normal Traffic
    - Hard Braking Non-Accident (False Alarm Test)
    - High-Speed Collision
    - Vehicle Rollover & Spinout
    - Adverse Weather (Rain & Wet Skid)
    """
    samples_dir = os.path.join(base_dir, "sample_videos")
    os.makedirs(samples_dir, exist_ok=True)

    suite_configs = [
        ("normal_traffic.mp4", "normal", "clear", 150),
        ("sudden_brake_normal.mp4", "sudden_brake_normal", "clear", 150),
        ("high_speed_collision.mp4", "high_speed_collision", "clear", 150),
        ("rollover_spinout.mp4", "rollover_spinout", "clear", 150),
        ("adverse_weather_accident.mp4", "adverse_weather_accident", "rain", 150),
    ]

    manifest = []
    print("Generating synthetic validation video suite...")
    for filename, scenario, weather, frames in suite_configs:
        path = os.path.join(samples_dir, filename)
        meta = generate_scenario_video(path, scenario_type=scenario, total_frames=frames, weather=weather)
        manifest.append({
            "filename": filename,
            "scenario": scenario,
            "weather": weather,
            "frames": frames,
            "has_accident": meta["accident_frame_idx"] != -1,
            "meta_path": path.replace(".mp4", "_meta.json")
        })
        print(f"Generated: {filename} (Scenario: {scenario}, Weather: {weather}, Has Accident: {meta['accident_frame_idx'] != -1})")

    manifest_path = os.path.join(samples_dir, "dataset_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    return manifest

if __name__ == "__main__":
    build_default_dataset_suite()

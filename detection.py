import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import os
import numpy as np
import cv2
import hailo
import time
from hailo_apps_infra.hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
    app_callback_class,
)
from hailo_apps_infra.detection_pipeline import GStreamerDetectionApp

# -----------------------------------------------------------------------------------------------
# CONFIGURABLE PARAMETERS - Adjust these to optimize tracking
# -----------------------------------------------------------------------------------------------
# Tracking parameters
TRACK_ALL_CLASSES = True         # Set to True to track all object classes, False for specific classes
SPECIFIC_CLASS_ID = -1            # If TRACK_ALL_CLASSES is False, specify which class ID to track

# Tracker algorithm parameters
KALMAN_DIST_THR = 0.8             # Threshold for Kalman filter (0.5-1.0, higher is more lenient)
IOU_THR = 0.5                     # IoU threshold for tracking (0.3-0.9, higher is more lenient)
INIT_IOU_THR = 0.5                # Initial IoU threshold (0.3-0.9, higher is more lenient)

# Object persistence parameters
KEEP_NEW_FRAMES = 3               # Frames to keep "new" objects (1-5)
KEEP_TRACKED_FRAMES = 15          # Frames to keep tracked objects (10-60)
KEEP_LOST_FRAMES = 5             # Frames to keep lost objects (5-30)

# Detection confidence threshold
MIN_CONFIDENCE = 0.3              # Minimum confidence to count detections (0.1-0.9)

# -----------------------------------------------------------------------------------------------
# User-defined class to be used in the callback function
# -----------------------------------------------------------------------------------------------
# Inheritance from the app_callback_class
class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        # Add counters for bees and varroa
        self.bee_count = 0
        self.varroa_count = 0
        # Simple unique ID tracking
        self.unique_bee_ids = set()
        self.unique_varroa_ids = set()
        # Count per frame
        self.current_frame_bees = 0
        self.current_frame_varroa = 0
        # Start time for FPS calculation
        self.start_time = time.time()
        
    def increment_bee(self):
        self.bee_count += 1
        
    def increment_varroa(self):
        self.varroa_count += 1
        
    def get_bee_count(self):
        return self.bee_count
        
    def get_varroa_count(self):
        return self.varroa_count
        
    def get_unique_bee_count(self):
        return len(self.unique_bee_ids)
        
    def get_unique_varroa_count(self):
        return len(self.unique_varroa_ids)
    
    def reset_frame_counts(self):
        self.current_frame_bees = 0
        self.current_frame_varroa = 0
        
    def set_start_time(self, start_time):
        self.start_time = start_time
        
    def get_start_time(self):
        return self.start_time

# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------
# This is the callback function that will be called when data is available from the pipeline
def app_callback(pad, info, user_data):
    # Get the GstBuffer from the probe info
    buffer = info.get_buffer()
    # Check if the buffer is valid
    if buffer is None:
        return Gst.PadProbeReturn.OK
    # Using the user_data to count the number of frames
    user_data.increment()
    string_to_print = f"Frame count: {user_data.get_count()}\n"
    # Get the caps from the pad
    format, width, height = get_caps_from_pad(pad)
    # If the user_data.use_frame is set to True, we can get the video frame from the buffer
    frame = None
    if user_data.use_frame and format is not None and width is not None and height is not None:
        # Get video frame
        frame = get_numpy_from_buffer(buffer, format, width, height)
    # Get the detections from the buffer
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)
    
    # Reset frame counts
    user_data.reset_frame_counts()
    
    # Parse the detections
    for detection in detections:
        label = detection.get_label()
        bbox = detection.get_bbox()
        confidence = detection.get_confidence()
        
        # Skip low confidence detections
        if confidence < MIN_CONFIDENCE:
            continue
        
        # Get track ID (if available)
        track_id = 0
        track = detection.get_objects_typed(hailo.HAILO_UNIQUE_ID)
        if len(track) == 1:
            track_id = track[0].get_id()
        
        # Check for bee detections
        if label == "bee":
            user_data.increment_bee()
            user_data.current_frame_bees += 1
            if track_id > 0:  # Only add valid track IDs
                user_data.unique_bee_ids.add(track_id)
            string_to_print += (f"Label: {label} Track ID: {track_id} Confidence: {confidence:.2f}\n")
            
        # Check for varroa detections
        elif label == "varroa":
            user_data.increment_varroa()
            user_data.current_frame_varroa += 1
            if track_id > 0:  # Only add valid track IDs
                user_data.unique_varroa_ids.add(track_id)
            string_to_print += (f"Label: {label} Track ID: {track_id} Confidence: {confidence:.2f}\n")
    
    # Add total counts to the output
    string_to_print += f"Current frame bees: {user_data.current_frame_bees}\n"
    string_to_print += f"Current frame varroa: {user_data.current_frame_varroa}\n"
    string_to_print += f"Total bees: {user_data.get_bee_count()}\n"
    string_to_print += f"Total varroa: {user_data.get_varroa_count()}\n"
    string_to_print += f"Unique bees: {user_data.get_unique_bee_count()}\n"
    string_to_print += f"Unique varroa: {user_data.get_unique_varroa_count()}\n"
            
    if user_data.use_frame:
        # Note: using imshow will not work here, as the callback function is not running in the main thread
        # Let's print the detection counts to the frame
        cv2.putText(frame, f"Bees: {user_data.get_bee_count()}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Varroa: {user_data.get_varroa_count()}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, f"Unique Bees: {user_data.get_unique_bee_count()}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Unique Varroa: {user_data.get_unique_varroa_count()}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Calculate FPS
        elapsed_time = time.time() - user_data.get_start_time()
        if elapsed_time > 0:
            fps = user_data.get_count() / elapsed_time
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        
        # Draw bounding boxes
        for detection in detections:
            label = detection.get_label()
            bbox = detection.get_bbox()
            confidence = detection.get_confidence()
            
            # Skip low confidence detections for visualization
            if confidence < MIN_CONFIDENCE:
                continue
            
            x1, y1, x2, y2 = int(bbox.xmin() * width), int(bbox.ymin() * height), int(bbox.xmax() * width), int(bbox.ymax() * height)
            
            # Different colors for different classes
            if label == "bee":
                color = (0, 255, 0)  # Green for bees
            elif label == "varroa":
                color = (0, 0, 255)  # Red for varroa
            else:
                color = (255, 255, 0)  # Yellow for other
                
            # Draw rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Add label text
            track_id = 0
            track = detection.get_objects_typed(hailo.HAILO_UNIQUE_ID)
            if len(track) == 1:
                track_id = track[0].get_id()
                
            if track_id > 0:
                label_text = f"{label} #{track_id}: {confidence:.2f}"
            else:
                label_text = f"{label}: {confidence:.2f}"
                
            cv2.putText(frame, label_text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Convert the frame to BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        user_data.set_frame(frame)
        
    print(string_to_print)
    return Gst.PadProbeReturn.OK

if __name__ == "__main__":
    # Create an instance of the user app callback class
    user_data = user_app_callback_class()
    # Store start time for FPS calculation
    user_data.set_start_time(time.time())
    
    # Create the app
    app = GStreamerDetectionApp(app_callback, user_data)
    
    # Configure the tracker to track based on settings
    hailotracker = app.pipeline.get_by_name("hailo_tracker")
    if hailotracker:
        # Set what to track based on configuration
        class_id = -1 if TRACK_ALL_CLASSES else SPECIFIC_CLASS_ID
        hailotracker.set_property("class-id", class_id)
        
        # Configure tracker algorithm parameters
        hailotracker.set_property("kalman-dist-thr", KALMAN_DIST_THR)
        hailotracker.set_property("iou-thr", IOU_THR)
        hailotracker.set_property("init-iou-thr", INIT_IOU_THR)
        
        # Configure object persistence parameters
        hailotracker.set_property("keep-new-frames", KEEP_NEW_FRAMES)
        hailotracker.set_property("keep-tracked-frames", KEEP_TRACKED_FRAMES)
        hailotracker.set_property("keep-lost-frames", KEEP_LOST_FRAMES)
        
        print(f"Configured hailotracker with: class-id={class_id}, kalman-dist-thr={KALMAN_DIST_THR}, " +
              f"iou-thr={IOU_THR}, init-iou-thr={INIT_IOU_THR}, keep-tracked-frames={KEEP_TRACKED_FRAMES}")
    else:
        print("Warning: Could not find hailo_tracker element in the pipeline!")
    
    # Run the application
    app.run()

from flask import Flask, render_template, Response, request, jsonify
import threading
import time
import subprocess
import os
import shlex
import json
import signal
import sys
from collections import deque
import datetime
from bee_health_db import BeeHealthDatabase

app = Flask(__name__)

# Configuration
DETECTION_COMMAND = "python /home/ergi/hailo-rpi5-examples/detection.py -i /dev/video0   --hef /home/ergi/hailo-rpi5-examples/first_15k.hef --labels-json /home/ergi/hailo-rpi5-examples/labels.json"
DEBUG = True  # Enable debugging for troubleshooting
MAX_DATA_POINTS = 100  # For time-series data

# Initialize database connection
db = BeeHealthDatabase(os.path.join(os.path.dirname(__file__), "bee_health.db"))

# Global variables
detection_active = False
detection_thread = None
detection_process = None

# Time series data for charting
time_series_data = {
    "timestamps": deque(maxlen=MAX_DATA_POINTS),
    "bee_counts": deque(maxlen=MAX_DATA_POINTS),
    "varroa_counts": deque(maxlen=MAX_DATA_POINTS),
    "infestation_ratio": deque(maxlen=MAX_DATA_POINTS),
}

# Current statistics
detection_stats = {
    "total_frames": 0,
    "total_bees": 0,
    "total_varroa": 0,
    "unique_bees": 0,
    "unique_varroa": 0,
    "current_bees": 0,
    "current_varroa": 0,
    "fps": 0,
    "infestation_ratio": 0,
    "infestation_risk_level": "Unknown",
    "last_update": time.time()
}

# Risk level thresholds (varroa:bee ratio)
RISK_THRESHOLDS = {
    "low": 0.05,       # <5% - healthy colony
    "moderate": 0.10,  # 5-10% - monitor closely
    "high": 0.15,      # 10-15% - intervention recommended
    "critical": 0.20   # >15% - immediate action required
}

def update_time_series():
    """Update time series data for charts and save to database"""
    global time_series_data, detection_stats
    
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    time_series_data["timestamps"].append(current_time)
    time_series_data["bee_counts"].append(detection_stats["current_bees"])
    time_series_data["varroa_counts"].append(detection_stats["current_varroa"])
    
    # Calculate infestation ratio based on unique objects (avoid division by zero)
    if detection_stats["unique_bees"] > 0:
        ratio = detection_stats["unique_varroa"] / detection_stats["unique_bees"]
    else:
        ratio = 0
    
    # Store ratio in time series and detection stats
    time_series_data["infestation_ratio"].append(ratio)
    detection_stats["infestation_ratio"] = ratio
    
    # Update Colony Health Status based on unique object ratio
    if ratio < RISK_THRESHOLDS["low"]:
        detection_stats["infestation_risk_level"] = "Low"
    elif ratio < RISK_THRESHOLDS["moderate"]:
        detection_stats["infestation_risk_level"] = "Moderate"
    elif ratio < RISK_THRESHOLDS["high"]:
        detection_stats["infestation_risk_level"] = "High"
    else:
        detection_stats["infestation_risk_level"] = "Critical"
    
    # Save metrics to database (every 100 frames to avoid excessive database writes)
    if detection_stats["total_frames"] % 100 == 0:
        db.save_metrics(
            unique_bee_count=detection_stats["unique_bees"],
            unique_varroa_count=detection_stats["unique_varroa"],
            frame_count=detection_stats["total_frames"],
            fps=detection_stats["fps"]
        )

def parse_detection_output(line):
    """Parse detection output lines for bee and varroa counts"""
    global detection_stats
    
    if DEBUG:
        print(f"Parsing line: {line}")
    
    # Parse unique bee and varroa counts for Cumulative Statistics, 
    # Infestation Ratio, and Colony Health Status
    if "Unique bees:" in line:
        try:
            unique_bee_count = int(line.split("Unique bees:")[1].strip())
            detection_stats["unique_bees"] = unique_bee_count
            
            # Use unique bees for Total Bees in Cumulative Statistics
            detection_stats["total_bees"] = unique_bee_count
            
        except (ValueError, IndexError) as e:
            if DEBUG:
                print(f"Error parsing unique bee count: {e}")
    
    if "Unique varroa:" in line:
        try:
            unique_varroa_count = int(line.split("Unique varroa:")[1].strip())
            detection_stats["unique_varroa"] = unique_varroa_count
            
            # Use unique varroa for Total Varroa in Cumulative Statistics
            detection_stats["total_varroa"] = unique_varroa_count
            
        except (ValueError, IndexError) as e:
            if DEBUG:
                print(f"Error parsing unique varroa count: {e}")
    
    # Parse current frame bee and varroa counts for Real-time Detection Trends
    # and Key Detection Metrics
    if "Current frame bees:" in line:
        try:
            current_bee_count = int(line.split("Current frame bees:")[1].strip())
            detection_stats["current_bees"] = current_bee_count
        except (ValueError, IndexError) as e:
            if DEBUG:
                print(f"Error parsing current frame bee count: {e}")
    
    if "Current frame varroa:" in line:
        try:
            current_varroa_count = int(line.split("Current frame varroa:")[1].strip())
            detection_stats["current_varroa"] = current_varroa_count
        except (ValueError, IndexError) as e:
            if DEBUG:
                print(f"Error parsing current frame varroa count: {e}")
    
    # Use individual detections to update current bee/varroa counts
    if "Label: bee" in line:
        # Optional: Process individual bee detections if needed
        pass
    
    if "Label: varroa" in line:
        # Optional: Process individual varroa detections if needed
        pass
    
    # Frame count
    if "Frame count:" in line:
        try:
            frame_count = int(line.split("Frame count:")[1].strip())
            detection_stats["total_frames"] = frame_count
            
            # Calculate FPS
            current_time = time.time()
            time_diff = current_time - detection_stats["last_update"]
            if time_diff > 0:
                frame_diff = frame_count - detection_stats.get("last_frame", 0)
                if frame_diff > 0 and time_diff > 0.5:  # Update FPS every half second
                    detection_stats["fps"] = frame_diff / time_diff
                    detection_stats["last_frame"] = frame_count
                    detection_stats["last_update"] = current_time
            
            # Update time series data every 10 frames
            if frame_count % 10 == 0:
                update_time_series()
                
        except (ValueError, IndexError) as e:
            if DEBUG:
                print(f"Error parsing frame count: {e}")

def find_and_kill_processes_by_name(process_name):
    """Find and kill all processes matching the given name"""
    try:
        # Get the list of all running processes
        output = subprocess.check_output(["ps", "-ef"]).decode()
        
        # Find PIDs of processes matching the name
        pids = []
        for line in output.split('\n'):
            if process_name in line and 'grep' not in line:
                # Extract PID (second column in ps output)
                parts = line.split()
                if len(parts) > 1:
                    try:
                        pid = int(parts[1])
                        pids.append(pid)
                    except ValueError:
                        pass
        
        # Kill each process
        for pid in pids:
            try:
                print(f"Killing process with PID {pid}")
                os.kill(pid, signal.SIGTERM)
                # Wait a bit to see if it terminates
                time.sleep(0.5)
                # Check if the process is still running
                try:
                    os.kill(pid, 0)  # Signal 0 is used to check if a process exists
                    # Process still exists, try SIGKILL
                    print(f"Process {pid} didn't terminate with SIGTERM, using SIGKILL")
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    # Process no longer exists
                    pass
            except OSError as e:
                print(f"Error killing process {pid}: {e}")
                
        return len(pids)
    except Exception as e:
        print(f"Error finding and killing processes: {e}")
        return 0

def find_and_kill_processes_by_partial_command(partial_command):
    """Find and kill processes by partial command string"""
    try:
        # Get the list of all running processes with full command
        output = subprocess.check_output(["ps", "-eo", "pid,cmd"]).decode()
        
        # Find PIDs of processes matching the partial command
        pids = []
        for line in output.split('\n'):
            if partial_command in line and 'grep' not in line:
                # Extract PID (first column in ps output)
                parts = line.strip().split()
                if parts:
                    try:
                        pid = int(parts[0])
                        pids.append(pid)
                    except ValueError:
                        pass
        
        # Kill each process
        for pid in pids:
            try:
                print(f"Killing process with PID {pid} (matches '{partial_command}')")
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.5)
                try:
                    os.kill(pid, 0)
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass
            except OSError as e:
                if e.errno != 3:  # Ignore "no such process" errors
                    print(f"Error killing process {pid}: {e}")
                
        return len(pids)
    except Exception as e:
        print(f"Error finding and killing processes: {e}")
        return 0

def clean_gstreamer_resources():
    """Clean up orphaned GStreamer resources"""
    try:
        # Clean up any stray shared memory segments (often left by GStreamer)
        subprocess.run(["ipcrm", "-a"], stderr=subprocess.PIPE, shell=True)
        
        # Clean up any stray semaphores
        subprocess.run("for i in `ipcs -s | grep $(whoami) | awk '{print $2}'`; do ipcrm -s $i; done", 
                      shell=True, stderr=subprocess.PIPE)
    except Exception as e:
        print(f"Error cleaning GStreamer resources: {e}")

def terminate_detection():
    """Terminate the detection process and ensure all related processes are stopped"""
    global detection_process
    
    print("Terminating detection processes...")
    
    # First attempt to terminate our subprocess if it exists
    if detection_process:
        try:
            pid = detection_process.pid
            print(f"Terminating main detection process (PID: {pid})")
            
            # Send SIGINT to allow graceful GStreamer pipeline shutdown
            # This is important! SIGINT allows GStreamer to clean up properly
            try:
                os.kill(pid, signal.SIGINT)
            
                # Give more time for GStreamer pipeline to clean up
                time.sleep(2)
                
                # Check if process is still running
                try:
                    os.kill(pid, 0)  # Signal 0 is used to check if a process exists
                    print(f"Process {pid} still exists, using SIGTERM")
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(1)
                    
                    # Check again and use SIGKILL as last resort
                    try:
                        os.kill(pid, 0)
                        print(f"Process {pid} still exists, using SIGKILL")
                        os.kill(pid, signal.SIGKILL)
                    except OSError:
                        pass
                except OSError:
                    # Process no longer exists
                    pass
            except OSError:
                # Process may already be gone
                pass
                
        except Exception as e:
            print(f"Error terminating process: {e}")
            
        detection_process = None
    
    # Kill all related processes
    process_names = ["detection.py", "GStreamerDetectionApp", "Hailo Detection App"]
    for name in process_names:
        find_and_kill_processes_by_name(name)
    
    # Kill any GStreamer processes that might be related
    killed_count = find_and_kill_processes_by_name("gst-launch")
    if killed_count > 0:
        print(f"Killed {killed_count} GStreamer processes")
        
    # Also kill any orphaned GStreamer elements by partial command
    for gst_element in ["hailonet", "hailotracker", "hailofilter", "hailooverlay", "autovideosink"]:
        find_and_kill_processes_by_partial_command(gst_element)
        
    # Give some time for processes to clean up
    time.sleep(0.1)

def detection_loop():
    """Thread function for the detection process"""
    global detection_active, detection_stats, detection_process
    
    try:
        # Reset statistics
        detection_stats["total_frames"] = 0
        detection_stats["total_bees"] = 0
        detection_stats["total_varroa"] = 0
        detection_stats["unique_bees"] = 0
        detection_stats["unique_varroa"] = 0
        detection_stats["current_bees"] = 0
        detection_stats["current_varroa"] = 0
        detection_stats["fps"] = 0
        detection_stats["infestation_ratio"] = 0
        detection_stats["infestation_risk_level"] = "Unknown"
        detection_stats["last_update"] = time.time()
        detection_stats["last_frame"] = 0
        
        # Start a new database session
        source_file = DETECTION_COMMAND.split(" ")[3]  # Extract video file name
        db.start_new_session(source=source_file, notes="Automatic detection")
        
        # Clear time series data
        time_series_data["timestamps"].clear()
        time_series_data["bee_counts"].clear()
        time_series_data["varroa_counts"].clear()
        time_series_data["infestation_ratio"].clear()
        
        # Set environment variables for display
        env = os.environ.copy()
        env["DISPLAY"] = ":0"  # Use the main display
        
        # Ensure any leftover detection processes are terminated
        terminate_detection()
        clean_gstreamer_resources()
        
        # Small delay to ensure cleanup is complete
        time.sleep(0.1)
        
        # Launch the detection command as a subprocess
        if DEBUG:
            print(f"Starting detection process with command: {DETECTION_COMMAND}")
        
        # Use shell=True for more reliable execution
        detection_process = subprocess.Popen(
            DETECTION_COMMAND,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True,
            env=env,  # Pass the environment with DISPLAY set
            cwd="/home/ergi/hailo-rpi5-examples"  # Set working directory
        )
        
        print(f"Started detection process with PID: {detection_process.pid}")
        
        # Process stdout in real-time
        while detection_active and detection_process and detection_process.poll() is None:
            # Read a line from stdout with timeout
            line = detection_process.stdout.readline()
            if not line:
                # No more output but process is still running
                time.sleep(0.1)
                continue
                
            line = line.strip()
            if line:
                print(f"Detection output: {line}")
                parse_detection_output(line)
                
    except Exception as e:
        print(f"Error in detection loop: {e}")
    finally:
        # End the database session
        db.end_session()
        
        # Make sure to terminate the detection process and any child processes
        terminate_detection()
        clean_gstreamer_resources()
        
        detection_active = False
        print("Detection thread exiting")

def signal_handler(sig, frame):
    """Handle termination signals"""
    print(f"Received signal {sig}, cleaning up and exiting...")
    db.end_session()  # Make sure to end any active database session
    terminate_detection()
    clean_gstreamer_resources()
    sys.exit(0)

@app.route('/')
def index():
    """Render the dashboard page"""
    return render_template('index.html')

@app.route('/start_detection', methods=['POST'])
def start_detection():
    """Start the detection process"""
    global detection_active, detection_thread
    
    if not detection_active:
        # First, make sure any existing processes are terminated
        terminate_detection()
        clean_gstreamer_resources()
        
        # Small delay to ensure cleanup is complete
        time.sleep(0.1)
        
        # Now start a new detection process
        detection_active = True
        detection_thread = threading.Thread(target=detection_loop)
        detection_thread.daemon = True
        detection_thread.start()
        
        # Give it a moment to start up
        time.sleep(1)
        
        return jsonify({"status": "started"})
    
    return jsonify({"status": "already_running"})

@app.route('/stop_detection', methods=['POST'])
def stop_detection():
    """Stop the detection process"""
    global detection_active
    
    if detection_active:
        print("Stopping detection...")
        
        # Set flag to stop the thread
        detection_active = False
        
        # Terminate all detection processes
        terminate_detection()
        
        # Clean up GStreamer resources
        clean_gstreamer_resources()
        
        # Wait for thread to finish - give it more time
        if detection_thread:
            detection_thread.join(timeout=5.0)
            
        print("Detection stopped")
        return jsonify({"status": "stopped"})
    
    return jsonify({"status": "already_stopped"})

@app.route('/get_stats')
def get_stats():
    """Return the current detection statistics"""
    if DEBUG:
        print(f"Sending stats to client: {detection_stats}")
    return jsonify(detection_stats)

@app.route('/get_time_series')
def get_time_series():
    """Return time series data for charts"""
    result = {
        "timestamps": list(time_series_data["timestamps"]),
        "bee_counts": list(time_series_data["bee_counts"]),
        "varroa_counts": list(time_series_data["varroa_counts"]),
        "infestation_ratio": list(time_series_data["infestation_ratio"]),
    }
    return jsonify(result)

# Database access routes
@app.route('/api/sessions')
def get_sessions():
    """Get list of recording sessions"""
    limit = request.args.get('limit', 10, type=int)
    sessions = db.get_sessions(limit=limit)
    return jsonify(sessions)

@app.route('/api/metrics')
def get_metrics():
    """Get stored metrics"""
    limit = request.args.get('limit', 100, type=int)
    session_id = request.args.get('session_id', None, type=int)
    metrics = db.get_latest_metrics(limit=limit, session_id=session_id)
    return jsonify(metrics)

# Email testing endpoint - kept for functionality
@app.route('/test-email')
def test_email():
    """Test email functionality with timeout and better error handling"""
    result = {
        "status": "unknown",
        "message": "",
        "error_details": ""
    }
    
    try:
        # Get the most recent session
        sessions = db.get_sessions(limit=1)
        if not sessions:
            result["status"] = "error"
            result["message"] = "No sessions found to send test email."
            return jsonify(result)
            
        session_id = sessions[0]['session_id']
        
        # Check if email credentials exist
        email_service = db.email_service
        if not email_service.username or not email_service.password:
            result["status"] = "error"
            result["message"] = "Missing email credentials. Check BEE_MONITOR_EMAIL and BEE_MONITOR_EMAIL_PASSWORD environment variables."
            result["error_details"] = f"Username available: {'Yes' if email_service.username else 'No'}, Password available: {'Yes' if email_service.password else 'No'}"
            return jsonify(result)
        
        # Check recipient
        if not email_service.recipient:
            result["status"] = "error"
            result["message"] = "No recipient email address configured."
            return jsonify(result)
        
        # Add a timeout for the email sending
        import threading
        import queue

        # Use a queue to get the result from the thread
        q = queue.Queue()
        
        def send_email_with_timeout():
            try:
                success = email_service.send_session_summary(session_id, db.db_path)
                q.put(("success" if success else "error", 
                      f"Email {'sent successfully' if success else 'failed to send'} for session {session_id}"))
            except Exception as e:
                q.put(("error", f"Exception while sending email: {str(e)}"))
        
        # Start email sending in a separate thread
        email_thread = threading.Thread(target=send_email_with_timeout)
        email_thread.daemon = True
        email_thread.start()
        
        # Wait for result with a timeout
        try:
            status, message = q.get(timeout=10)  # 10 second timeout
            result["status"] = status
            result["message"] = message
        except queue.Empty:
            result["status"] = "error"
            result["message"] = "Email sending timed out after 10 seconds. Check SMTP server settings."
        
        return jsonify(result)
        
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Error in test-email route"
        result["error_details"] = str(e)
        return jsonify(result)

if __name__ == '__main__':
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Ensure no detection processes are running when we start
    terminate_detection()
    clean_gstreamer_resources()
    
    # Small delay to ensure cleanup is complete
    time.sleep(0.1)
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)

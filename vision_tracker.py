# vision_tracker.py
# FollowFly vision system for person detection and tracking

import cv2
import numpy as np
import time
import logging
import threading

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisionTracker:
    """Computer vision system for person detection and tracking"""
    
    def __init__(self, camera_source=0, detection_interval=0.5, 
                 focal_length=800, real_width=0.5):
        """
        Initialize the vision tracker
        
        Args:
            camera_source: Camera source (0 for default camera, file path for video)
            detection_interval: How often to run detection (seconds)
            focal_length: Camera focal length in pixels
            real_width: Approximate width of a person in meters (for distance estimation)
        """
        self.camera_source = camera_source
        self.detection_interval = detection_interval
        self.focal_length = focal_length
        self.real_width = real_width
        
        self.cap = None
        self.frame_width = 0
        self.frame_height = 0
        self.frame_center = (0, 0)
        
        # Tracking variables
        self.target_position = None  # 3D position (x, y, z) in local coordinates
        self.target_bbox = None      # 2D bounding box (x, y, w, h) in image
        self.last_detection_time = 0
        
        # Thread control
        self.is_running = False
        self.stop_event = threading.Event()
        self.tracker_thread = None
        
        # Initialize HOG detector
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        # Initialize tracker
        self.tracker = cv2.TrackerKCF_create()
        
        logger.info("Vision tracker initialized")
    
    def start(self):
        """Start the vision tracking system"""
        if self.is_running:
            logger.warning("Vision tracker is already running")
            return
            
        # Open camera
        self.cap = cv2.VideoCapture(self.camera_source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera source: {self.camera_source}")
            
        # Get camera properties
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_center = (self.frame_width // 2, self.frame_height // 2)
        
        logger.info(f"Camera opened: {self.frame_width}x{self.frame_height}")
        
        # Start tracking in separate thread
        self.is_running = True
        self.stop_event.clear()
        self.tracker_thread = threading.Thread(target=self._tracking_loop)
        self.tracker_thread.daemon = True
        self.tracker_thread.start()
        
        logger.info("Vision tracker started")
    
    def stop(self):
        """Stop the vision tracking system"""
        if not self.is_running:
            logger.warning("Vision tracker is not running")
            return
            
        logger.info("Stopping vision tracker...")
        self.stop_event.set()
        
        if self.tracker_thread:
            self.tracker_thread.join(timeout=5.0)
            self.tracker_thread = None
            
        if self.cap:
            self.cap.release()
            self.cap = None
            
        self.is_running = False
        logger.info("Vision tracker stopped")
    
    def _tracking_loop(self):
        """Main tracking loop (runs in separate thread)"""
        logger.info("Starting tracking loop")
        tracking_initialized = False
        
        while not self.stop_event.is_set():
            # Read frame from camera
            ret, frame = self.cap.read()
            if not ret:
                logger.error("Failed to read frame from camera")
                time.sleep(0.1)
                continue
                
            # Check if we need to run detection
            current_time = time.time()
            run_detection = (current_time - self.last_detection_time) >= self.detection_interval
            
            if run_detection or self.target_bbox is None:
                # Run person detection
                self.target_bbox = self._detect_person(frame)
                
                if self.target_bbox is not None:
                    # Initialize tracker with new detection
                    self.tracker = cv2.TrackerKCF_create()
                    self.tracker.init(frame, self.target_bbox)
                    tracking_initialized = True
                    
                    # Update target position
                    self._update_target_position(frame, self.target_bbox)
                    self.last_detection_time = current_time
            elif tracking_initialized:
                # Update tracker with new frame
                success, bbox = self.tracker.update(frame)
                
                if success:
                    self.target_bbox = bbox
                    # Update target position
                    self._update_target_position(frame, bbox)
                else:
                    # Tracking failed, force detection in next iteration
                    self.last_detection_time = 0
            
            # Control loop frequency
            time.sleep(0.03)  # ~30fps
    
    def _detect_person(self, frame):
        """
        Detect person in frame using HOG detector
        
        Returns:
            tuple: (x, y, w, h) bounding box or None if no person detected
        """
        # Resize frame for faster processing
        frame_resized = cv2.resize(frame, (min(frame.shape[1], 640), 
                                         min(frame.shape[0], 480)))
        scale_factor = frame.shape[1] / frame_resized.shape[1]
        
        # Detect people
        boxes, weights = self.hog.detectMultiScale(
            frame_resized,
            winStride=(8, 8),
            padding=(8, 8),
            scale=1.05
        )
        
        if len(boxes) == 0:
            return None
            
        # Get the largest box (assuming it's the closest person)
        largest_box = max(boxes, key=lambda box: box[2] * box[3])
        
        # Scale box back to original frame size
        x, y, w, h = largest_box
        box_rescaled = (
            int(x * scale_factor),
            int(y * scale_factor),
            int(w * scale_factor),
            int(h * scale_factor)
        )
        
        logger.debug(f"Person detected: {box_rescaled}")
        return box_rescaled
    
    def _update_target_position(self, frame, bbox):
        """
        Update 3D target position based on bounding box
        
        This converts the 2D image position to a 3D position in
        local NED coordinates (North-East-Down)
        """
        if bbox is None:
            self.target_position = None
            return
            
        x, y, w, h = bbox
        
        # Calculate center of bounding box
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Calculate distance based on apparent size
        # Using simple pinhole camera model: 
        # distance = (real_width * focal_length) / apparent_width
        distance_z = (self.real_width * self.focal_length) / w
        
        # Calculate horizontal position (x, y) relative to camera
        # Convert from pixel coordinates to meters using similar triangle
        pixel_to_meter = self.real_width / w
        pos_x = (center_x - self.frame_center[0]) * pixel_to_meter
        pos_y = (center_y - self.frame_center[1]) * pixel_to_meter
        
        # Convert to NED coordinates (assuming camera pointing north)
        # In NED: x=North, y=East, z=Down
        # This is a simplified conversion and would need to be adjusted
        # based on actual drone orientation and camera mounting
        ned_x = distance_z  # Person is in front of drone (North)
        ned_y = -pos_x      # Positive pixel x is right, negative NED y is right (East)
        ned_z = -1.7        # Assuming person height, camera pointing horizontally
        
        self.target_position = (ned_x, ned_y, ned_z)
        logger.debug(f"Target position updated: {self.target_position}")
    
    def get_target_position(self):
        """Get the current target position in local NED coordinates"""
        return self.target_position
    
    def get_target_distance(self):
        """Get estimated distance to target in meters"""
        if self.target_position is None:
            return None
            
        # Calculate Euclidean distance
        x, y, z = self.target_position
        return np.sqrt(x**2 + y**2)
    
    def capture_frame(self):
        """Capture a frame for display/debugging"""
        if not self.cap or not self.cap.isOpened():
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        # Draw target bounding box if available
        if self.target_bbox is not None:
            x, y, w, h = [int(v) for v in self.target_bbox]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw distance
            distance = self.get_target_distance()
            if distance is not None:
                cv2.putText(frame, f"Distance: {distance:.2f}m", (x, y - 10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame
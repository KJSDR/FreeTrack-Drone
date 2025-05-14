# follow_controller.py
# FollowFly main controller for person tracking and autonomous following

import time
import threading
import logging
import numpy as np
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
from tracking_profiles import get_profile

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FollowController:
    """Main controller for FollowFly drone"""
    
    def __init__(self, connection_string='udp:127.0.0.1:14550', 
                 tracking_distance=5.0, home_location=None):
        """
        Initialize the Follow Controller
        
        Args:
            connection_string (str): Connection string for vehicle
            tracking_distance (float): Initial tracking distance in meters
            home_location (tuple): Optional home location (lat, lon, alt)
        """
        self.connection_string = connection_string
        self.vehicle = None
        self.is_following = False
        self.tracking_thread = None
        self.stop_event = threading.Event()
        
        # Initialize tracking profile
        self.tracking_profile = get_profile(tracking_distance)
        
        # Home location for return-to-home
        self.home_location = home_location
        
        logger.info(f"Initialized FollowController with {tracking_distance}m tracking distance")
    
    def connect(self):
        """Connect to the drone"""
        logger.info(f"Connecting to drone on {self.connection_string}...")
        self.vehicle = connect(self.connection_string, wait_ready=True)
        
        # Set home location if not provided
        if self.home_location is None:
            self.home_location = (self.vehicle.location.global_frame.lat,
                                 self.vehicle.location.global_frame.lon,
                                 self.vehicle.location.global_frame.alt)
            logger.info(f"Set home location to current position: {self.home_location}")
        
        logger.info("Connected to drone successfully")
        return self.vehicle
    
    def disconnect(self):
        """Disconnect from the drone"""
        if self.vehicle:
            self.vehicle.close()
            logger.info("Disconnected from drone")
    
    def arm_and_takeoff(self, target_altitude):
        """Arm the drone and take off to target altitude"""
        logger.info("Basic pre-arm checks...")
        while not self.vehicle.is_armable:
            logger.info("Waiting for drone to initialize...")
            time.sleep(1)
            
        logger.info("Arming motors")
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True
        
        while not self.vehicle.armed:
            logger.info("Waiting for arming...")
            time.sleep(1)
            
        logger.info(f"Taking off to {target_altitude}m")
        self.vehicle.simple_takeoff(target_altitude)
        
        # Wait until the drone reaches desired altitude
        while True:
            current_altitude = self.vehicle.location.global_relative_frame.alt
            logger.info(f"Altitude: {current_altitude:.1f}m")
            
            if current_altitude >= target_altitude * 0.95:
                logger.info("Reached target altitude")
                break
                
            time.sleep(1)
    
    def change_tracking_distance(self, new_distance):
        """Change the tracking distance profile"""
        logger.info(f"Changing tracking distance to {new_distance}m")
        self.tracking_profile = get_profile(new_distance)
        return self.tracking_profile
    
    def get_current_position(self):
        """Get current drone position in local NED coordinates"""
        # In a real implementation, this would convert GPS to local coordinates
        # This is a simplified placeholder
        return (0, 0, -self.vehicle.location.global_relative_frame.alt)
    
    def send_velocity_command(self, velocity_x, velocity_y, velocity_z):
        """
        Send velocity command to the drone in local NED frame
        
        Args:
            velocity_x (float): Velocity in North direction (m/s)
            velocity_y (float): Velocity in East direction (m/s)
            velocity_z (float): Velocity in Down direction (m/s)
        """
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0,       # time_boot_ms (not used)
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
            0b0000111111000111, # type_mask (only speeds enabled)
            0, 0, 0, # x, y, z positions (not used)
            velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
            0, 0, 0, # x, y, z acceleration 
            0, 0)    # yaw, yaw_rate
        
        self.vehicle.send_mavlink(msg)
        self.vehicle.flush()
    
    def start_following(self, target_tracker):
        """
        Start following the target
        
        Args:
            target_tracker: Object that implements get_target_position() method
        """
        if self.is_following:
            logger.warning("Already following target")
            return
            
        self.is_following = True
        self.stop_event.clear()
        
        def follow_loop():
            logger.info("Starting follow loop")
            
            while not self.stop_event.is_set():
                try:
                    # Get target position from vision system
                    target_position = target_tracker.get_target_position()
                    
                    # Skip if no target detected
                    if target_position is None:
                        logger.warning("No target detected")
                        # Send hover command (zero velocity)
                        self.send_velocity_command(0, 0, 0)
                        time.sleep(0.1)
                        continue
                    
                    # Current drone position
                    current_position = self.get_current_position()
                    
                    # Calculate movement vector
                    movement_vector = self.tracking_profile.calculate_movement_vector(
                        current_position, target_position)
                    
                    # Send velocity command to drone
                    self.send_velocity_command(*movement_vector)
                    
                except Exception as e:
                    logger.error(f"Error in follow loop: {e}")
                
                # Control frequency
                time.sleep(0.1)
            
            # Stop moving when follow loop ends
            self.send_velocity_command(0, 0, 0)
            logger.info("Follow loop ended")
        
        # Start following in a separate thread
        self.tracking_thread = threading.Thread(target=follow_loop)
        self.tracking_thread.daemon = True
        self.tracking_thread.start()
        logger.info("Started following target")
    
    def stop_following(self):
        """Stop following the target"""
        if not self.is_following:
            logger.warning("Not currently following target")
            return
            
        logger.info("Stopping follow mode...")
        self.stop_event.set()
        
        if self.tracking_thread:
            self.tracking_thread.join(timeout=5.0)
            self.tracking_thread = None
            
        self.is_following = False
        logger.info("Stopped following target")
    
    def return_to_home(self):
        """Return to home location"""
        logger.info("Returning to home location")
        self.stop_following()
        
        self.vehicle.mode = VehicleMode("RTL")
        logger.info("Return to home initiated")
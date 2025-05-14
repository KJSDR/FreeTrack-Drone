import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DistanceProfile:
    """Base class for drone tracking distance profiles"""
    
    def __init__(self, target_distance, altitude=None, horizontal_offset=0, 
                 distance_tolerance=0.5, max_speed=2.0):
        """
        Initialize tracking distance profile
        
        Args:
            target_distance (float): Target following distance in meters
            altitude (float, optional): Target altitude in meters (if None, uses current altitude)
            horizontal_offset (float): Horizontal offset from target (0=directly behind, 
                                      negative=left, positive=right) in meters
            distance_tolerance (float): Acceptable distance error in meters
            max_speed (float): Maximum movement speed in m/s
        """
        self.target_distance = target_distance
        self.altitude = altitude
        self.horizontal_offset = horizontal_offset
        self.distance_tolerance = distance_tolerance
        self.max_speed = max_speed
        
        logger.info(f"Initialized {self.__class__.__name__} with target distance {target_distance}m")
    
    def calculate_movement_vector(self, current_position, target_position):
        """
        Calculate movement vector to maintain target distance
        
        Args:
            current_position (tuple): Current drone position (x, y, z) in meters
            target_position (tuple): Current target position (x, y, z) in meters
            
        Returns:
            tuple: Movement vector (vx, vy, vz) in m/s
        """
        # Calculate current distance to target
        dx = target_position[0] - current_position[0]
        dy = target_position[1] - current_position[1]
        dz = 0 if self.altitude is None else self.altitude - current_position[2]
        
        # Calculate horizontal distance
        current_distance = np.sqrt(dx**2 + dy**2)
        
        # Calculate angle to target
        angle_to_target = np.arctan2(dy, dx)
        
        # Calculate desired position 
        offset_angle = angle_to_target + np.pi  # Behind target
        desired_x = target_position[0] + np.cos(offset_angle) * self.target_distance
        desired_y = target_position[1] + np.sin(offset_angle) * self.target_distance
        
        # Add horizontal offset
        perpendicular_angle = angle_to_target + np.pi/2  # 90 degrees to the right
        desired_x += np.cos(perpendicular_angle) * self.horizontal_offset
        desired_y += np.sin(perpendicular_angle) * self.horizontal_offset
        
        move_x = desired_x - current_position[0]
        move_y = desired_y - current_position[1]
        move_z = dz
        
        move_magnitude = np.sqrt(move_x**2 + move_y**2 + move_z**2)
        if move_magnitude > 0:
            scale_factor = min(self.max_speed, move_magnitude) / move_magnitude
            move_x *= scale_factor
            move_y *= scale_factor
            move_z *= scale_factor
        
        logger.debug(f"Current distance: {current_distance:.2f}m, Target: {self.target_distance:.2f}m")
        logger.debug(f"Movement vector: ({move_x:.2f}, {move_y:.2f}, {move_z:.2f}) m/s")
        
        return (move_x, move_y, move_z)
    
    def is_at_desired_distance(self, current_position, target_position):
        """Check if drone is at the desired distance from target"""
        dx = target_position[0] - current_position[0]
        dy = target_position[1] - current_position[1]
        current_distance = np.sqrt(dx**2 + dy**2)
        
        return abs(current_distance - self.target_distance) <= self.distance_tolerance


class CloseProfile(DistanceProfile):
    """Close following profile (3 meters)"""
    def __init__(self):
        super().__init__(target_distance=3.0, altitude=2.5, 
                        distance_tolerance=0.3, max_speed=1.5)


class MediumProfile(DistanceProfile):
    """Medium following profile (5 meters)"""
    def __init__(self):
        super().__init__(target_distance=5.0, altitude=3.0, 
                        distance_tolerance=0.5, max_speed=2.0)


class FarProfile(DistanceProfile):
    """Far following profile (10 meters)"""
    def __init__(self):
        super().__init__(target_distance=10.0, altitude=4.0, 
                        distance_tolerance=1.0, max_speed=3.0)


class VeryFarProfile(DistanceProfile):
    """Very far following profile (20 meters)"""
    def __init__(self):
        super().__init__(target_distance=20.0, altitude=8.0, 
                        distance_tolerance=2.0, max_speed=5.0)


def get_profile(distance):
    """Get appropriate tracking profile based on desired distance"""
    if distance <= 3:
        return CloseProfile()
    elif distance <= 5:
        return MediumProfile()
    elif distance <= 10:
        return FarProfile()
    else:
        return VeryFarProfile()
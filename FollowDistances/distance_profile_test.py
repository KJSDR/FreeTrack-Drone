# distance_profile_test.py
# Test script to visualize different tracking distance profiles

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from tracking_profiles import (
    CloseProfile, 
    MediumProfile, 
    FarProfile, 
    VeryFarProfile
)

def visualize_tracking_profiles():
    """Visualize the different tracking distance profiles"""
    # Create profiles
    profiles = [
        CloseProfile(),
        MediumProfile(),
        FarProfile(),
        VeryFarProfile()
    ]
    
    # Create figure
    fig = plt.figure(figsize=(15, 10))
    
    # ---- Top-down view (2D) ----
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.set_title('Top-down View (X-Y Plane)')
    ax1.set_xlabel('X (meters) - Forward/Backward')
    ax1.set_ylabel('Y (meters) - Left/Right')
    ax1.grid(True)
    
    # Target position (origin)
    ax1.scatter(0, 0, color='red', s=100, marker='*', label='Target')
    
    # Plot different profiles
    colors = ['blue', 'green', 'purple', 'orange']
    for i, profile in enumerate(profiles):
        # Get desired drone position for this profile
        distance = profile.target_distance
        h_offset = profile.horizontal_offset
        
        # Calculate drone position (behind target)
        drone_x = -distance
        drone_y = h_offset
        
        # Plot drone position
        ax1.scatter(drone_x, drone_y, color=colors[i], s=80, 
                  marker='o', label=f'{profile.__class__.__name__} ({distance}m)')
        
        # Draw connection line
        ax1.plot([0, drone_x], [0, drone_y], color=colors[i], linestyle='--', alpha=0.7)
        
        # Draw distance circle
        circle = plt.Circle((0, 0), distance, color=colors[i], fill=False, alpha=0.3)
        ax1.add_patch(circle)
    
    # Set equal aspect ratio
    ax1.set_aspect('equal')
    ax1.legend()
    
    # ---- 3D view ----
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    ax2.set_title('3D View')
    ax2.set_xlabel('X (meters) - Forward/Backward')
    ax2.set_ylabel('Y (meters) - Left/Right')
    ax2.set_zlabel('Z (meters) - Altitude')
    
    # Target position (origin, at ground level)
    ax2.scatter(0, 0, 0, color='red', s=100, marker='*', label='Target')
    
    # Plot different profiles
    for i, profile in enumerate(profiles):
        # Get desired drone position for this profile
        distance = profile.target_distance
        h_offset = profile.horizontal_offset
        altitude = profile.altitude if profile.altitude is not None else 3.0
        
        # Calculate drone position (behind target)
        drone_x = -distance
        drone_y = h_offset
        drone_z = altitude
        
        # Plot drone position
        ax2.scatter(drone_x, drone_y, drone_z, color=colors[i], s=80,
                  marker='o', label=f'{profile.__class__.__name__} ({distance}m, {altitude}m alt)')
        
        # Draw connection line
        ax2.plot([0, drone_x], [0, drone_y], [0, drone_z], color=colors[i], linestyle='--', alpha=0.7)
    
    # Draw ground plane
    x_range = np.linspace(-25, 5, 10)
    y_range = np.linspace(-10, 10, 10)
    X, Y = np.meshgrid(x_range, y_range)
    Z = np.zeros_like(X)
    ax2.plot_surface(X, Y, Z, alpha=0.1, color='gray')
    
    # Set equal aspect ratio
    ax2.set_box_aspect([1, 1, 1])
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('tracking_profiles_visualization.png', dpi=300)
    plt.show()

if __name__ == "__main__":
    visualize_tracking_profiles()
    print("Visualization of tracking profiles generated.")
    print("See 'tracking_profiles_visualization.png' for the output.")
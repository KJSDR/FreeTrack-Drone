import time
import argparse
import logging
import signal
import sys
from vision_tracker import VisionTracker
from follow_controller import FollowController
from tracking_profiles import get_profile

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('followfly.log')
    ]
)
logger = logging.getLogger(__name__)

# Global variables for clean shutdown
vision_tracker = None
follow_controller = None
running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C and other termination signals"""
    global running
    logger.info("Shutdown signal received")
    running = False

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='FollowFly Autonomous Tracking Drone')
    
    parser.add_argument('--connect', default='udp:127.0.0.1:14550',
                      help='Vehicle connection string')
    parser.add_argument('--camera', type=int, default=0,
                      help='Camera index (default: 0)')
    parser.add_argument('--distance', type=float, default=5.0,
                      help='Initial tracking distance in meters (default: 5.0)')
    parser.add_argument('--altitude', type=float, default=3.0,
                      help='Target altitude in meters (default: 3.0)')
    parser.add_argument('--simulate', action='store_true',
                      help='Run in simulation mode (no actual drone commands)')
    
    return parser.parse_args()

def setup_system(args):
    """Set up vision tracking and drone control systems"""
    global vision_tracker, follow_controller
    
    # Initialize vision system
    logger.info("Initializing vision tracking system...")
    vision_tracker = VisionTracker(camera_source=args.camera)
    
    # Initialize drone controller
    if not args.simulate:
        logger.info(f"Connecting to drone on {args.connect}...")
        follow_controller = FollowController(
            connection_string=args.connect,
            tracking_distance=args.distance
        )
        follow_controller.connect()
    else:
        logger.info("Running in simulation mode (no drone connection)")
        # Create a mock controller for simulation
        follow_controller = None
    
    return vision_tracker, follow_controller

def run_interactive_mode():
    """Run interactive command mode"""
    global running, vision_tracker, follow_controller
    
    print("\nFollowFly Interactive Command Mode")
    print("----------------------------------")
    print("Commands:")
    print("  start          - Start following")
    print("  stop           - Stop following")
    print("  distance <n>   - Set tracking distance to n meters")
    print("  takeoff <n>    - Take off to n meters altitude")
    print("  land           - Return to launch and land")
    print("  status         - Show current status")
    print("  quit           - Quit application")
    print("----------------------------------")
    
    while running:
        try:
            command = input("\nCommand: ").strip().lower()
            
            if command == "start":
                if vision_tracker and follow_controller:
                    vision_tracker.start()
                    follow_controller.start_following(vision_tracker)
                    print("Started following target")
                else:
                    print("System not fully initialized")
                    
            elif command == "stop":
                if follow_controller:
                    follow_controller.stop_following()
                    print("Stopped following")
                
            elif command.startswith("distance "):
                try:
                    distance = float(command.split()[1])
                    if follow_controller:
                        profile = follow_controller.change_tracking_distance(distance)
                        print(f"Changed tracking distance to {distance}m")
                    else:
                        print("Drone controller not available")
                except (IndexError, ValueError):
                    print("Invalid distance value")
                    
            elif command.startswith("takeoff "):
                try:
                    altitude = float(command.split()[1])
                    if follow_controller:
                        follow_controller.arm_and_takeoff(altitude)
                        print(f"Taking off to {altitude}m")
                    else:
                        print("Drone controller not available")
                except (IndexError, ValueError):
                    print("Invalid altitude value")
                    
            elif command == "land":
                if follow_controller:
                    follow_controller.stop_following()
                    follow_controller.return_to_home()
                    print("Returning to launch point")
                else:
                    print("Drone controller not available")
                    
            elif command == "status":
                if vision_tracker:
                    target_pos = vision_tracker.get_target_position()
                    distance = vision_tracker.get_target_distance()
                    
                    print("\nSystem Status:")
                    print(f"Vision tracking: {'Running' if vision_tracker.is_running else 'Stopped'}")
                    print(f"Target detected: {'Yes' if target_pos else 'No'}")
                    
                    if distance:
                        print(f"Target distance: {distance:.2f}m")
                        
                    if follow_controller:
                        print(f"Following mode: {'Active' if follow_controller.is_following else 'Inactive'}")
                        print(f"Tracking distance: {follow_controller.tracking_profile.target_distance}m")
                    
            elif command == "quit":
                print("Shutting down...")
                running = False
                
            else:
                print("Unknown command")
                
        except KeyboardInterrupt:
            running = False
        except Exception as e:
            logger.error(f"Error in command processing: {e}")

def shutdown():
    """Perform clean shutdown"""
    global vision_tracker, follow_controller
    
    logger.info("Shutting down FollowFly...")
    
    # Stop vision system
    if vision_tracker and vision_tracker.is_running:
        vision_tracker.stop()
    
    # Land drone if following
    if follow_controller and follow_controller.is_following:
        follow_controller.stop_following()
        follow_controller.return_to_home()
        
    # Disconnect from drone
    if follow_controller:
        follow_controller.disconnect()
        
    logger.info("Shutdown complete")

def main():
    """Main application entry point"""
    # Set up signal handler for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse command line arguments
    args = parse_arguments()
    
    try:
        # Initialize systems
        logger.info("Initializing FollowFly...")
        vision_tracker, follow_controller = setup_system(args)
        
        # If not simulating and altitude specified, take off
        if follow_controller and not args.simulate and args.altitude > 0:
            logger.info(f"Taking off to {args.altitude}m...")
            follow_controller.arm_and_takeoff(args.altitude)
        
        # Run interactive mode
        run_interactive_mode()
        
    except Exception as e:
        logger.error(f"Error in main application: {e}")
    finally:
        # Ensure clean shutdown
        shutdown()

if __name__ == "__main__":
    main()
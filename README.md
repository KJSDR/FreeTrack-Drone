# (Work in Progess) 

# Using Raspberry Pi 5 + S500 V2

## Autonomous Person-Tracking Drone

### Project Overview

This project combines hardware assembly with software development to create a drone that can:
- Autonomously identify and track a person using computer vision
- Maintain appropriate following distance and angle
- Navigate around basic obstacles
- Operate without manual controller input

### Hardware Components

- **Frame:** F450/S500 quadcopter kit
- **Processing:** Raspberry Pi 4 (4GB+ RAM recommended)
- **Flight Controller:** Navio2 or PXFmini (Raspberry Pi HAT)
- **Camera:** GoPro (or Raspberry Pi Camera V2 for prototyping)
- **Positioning:** GPS module for location tracking
- **Power:** 3000mAh+ LiPo battery (higher capacity = longer flight time)
- **Optional:** Gimbal, additional sensors, video transmitter

### Software Architecture

FollowFly uses a multi-layered software architecture:

1. **Base Layer**: ArduPilot/PX4 for flight control and stabilization
2. **Vision Layer**: OpenCV-based person detection and tracking
3. **Navigation Layer**: Custom algorithms for path planning and obstacle avoidance
4. **Interface Layer**: Simple mobile app to configure following parameters

### Key Technologies

- **Computer Vision**: Python + OpenCV for real-time person detection
- **Flight Control**: DroneKit-Python for interfacing with ArduPilot
- **Navigation**: Custom algorithms for maintaining optimal distance and angle

### Getting Started

1. Assemble the drone hardware according to kit instructions
2. Install Raspberry Pi OS and required software dependencies
3. Configure the flight controller with ArduPilot
4. Install and test the FollowFly software
5. Calibrate sensors and test in a controlled environment

### Future

This is a estimated plan, once finished and in production will update with images and build for handmade drone, S500 + 3D printed components like wings and carbon frame.


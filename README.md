# (Work in Progess)

## Autonomous Person-Tracking Drone

FollowFly is an open-source DIY drone project that implements computer vision-based person tracking and autonomous following capabilities.

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

### Development Phases

1. **Phase 1**: Basic drone assembly and manual flight testing
2. **Phase 2**: Computer vision implementation for person detection
3. **Phase 3**: Tracking algorithm development
4. **Phase 4**: Autonomous navigation integration
5. **Phase 5**: Testing and refinement

### Getting Started

1. Assemble the drone hardware according to kit instructions
2. Install Raspberry Pi OS and required software dependencies
3. Configure the flight controller with ArduPilot
4. Install and test the FollowFly software
5. Calibrate sensors and test in a controlled environment

### Repository Structure

```
/
├── docs/               # Documentation
├── hardware/           # Hardware configuration files and notes
├── src/                # Source code
│   ├── vision/         # Computer vision modules
│   ├── navigation/     # Navigation algorithms
│   ├── flight/         # Flight control interface
│   └── main.py         # Main application
├── tests/              # Test scripts
└── tools/              # Utility scripts
```

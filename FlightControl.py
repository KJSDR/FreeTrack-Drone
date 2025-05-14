from dronekit import connect, VehicleMode, LocationGlobalRelative

vehicle = connect('udp:127.0.0.1:14550', wait_ready=True)

def follow_target(movement_commands):
    
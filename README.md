This is a repo for project in Robotics and AI 2025.

Readme contains instructions on how to interact with our setup.

1. You can interract with RPI5 by connecting it to your periferals.
2. (optional) Yet a better alternative is to use RealVNC viewer to access it remotely. Install it on your PC, connect RPI to your router or PC with a lan cable and use team1.local as an address. username and password are team1:team1
3. Our RPI5 already has Docker installed on top of RaspberryPI OS and has a container named "ros2-microros-wsbridge". You can check the container list by running "docker ps" in your terminal.
4. As for now, we use ROS WebSocket bridge to send commands from our RPI. From a terminal, go inside a docker container with command "docker exec -it ros2-microros-wsbridge bash"
5. Inside docker, run  "ros2 launch rosbridge_server rosbridge_websocket_launch.xml"
6. 

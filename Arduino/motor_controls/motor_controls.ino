#include <WiFi.h>
#include <ESPmDNS.h>
#include <micro_ros_arduino.h>
#include <stdio.h>
#include <rcl/rcl.h>
#include <rcl/error_handling.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>
#include <std_msgs/msg/int32.h>
#include <Arduino.h>

rcl_subscription_t subscriber;
std_msgs__msg__Int32 msg;
rclc_executor_t executor;
rclc_support_t support;
rcl_allocator_t allocator;
rcl_node_t node;
rcl_timer_t timer;

#define LED_PIN 13
#define TIMEOUT_INTERVAL 500 // 500 milliseconds
 
#define IN1 32
#define IN2 33
#define IN3 25
#define IN4 26
#define ENA 5
#define ENB 4

// Pwm settings
#define PWM_CHANNEL_A 0
#define PWM_CHANNEL_B 1
#define PWM_FREQ 5000
#define PWM_RESOLUTION 8

#define MAX_SPEED 255
#define MIN_SPEED 0

int motor_speed = MAX_SPEED;  // Default to max speed
 
unsigned long last_received_time = 0;
 
#define RCCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){error_loop();}}
#define RCSOFTCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){}}
 
void error_loop(){
    Serial.println("Error in Micro-ROS, restarting");
    delay(1000);
    ESP.restart();
}
 
void subscription_callback(const void * msgin)
{  
  const std_msgs__msg__Int32 * msg = (const std_msgs__msg__Int32 *)msgin;
  last_received_time = millis();
 
  Serial.print("Received data: ");
  Serial.println(msg->data);
 
  int32_t command = msg->data;
  Serial.print("Received command: ");
  Serial.println(command);
 
  if (command == 1) { moveForward(); }
  else if (command == 2) { moveBackward(); }
  else if (command == 3) { stopMotors(); }
  else if (command == 4) { turnLeft(); }
  else if (command == 5) { turnRight(); }
 
  digitalWrite(LED_PIN, (msg->data == 0) ? LOW : HIGH);
}
 
void setup() {

  // Configure PWM channels
  ledcAttach(ENA, PWM_FREQ, PWM_RESOLUTION);
  ledcAttach(ENB, PWM_FREQ, PWM_RESOLUTION);

  // Set motor control pins as output
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
 
  // Set motor enable pins as output
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
 
  // Set motors to be enabled
  digitalWrite(ENA, HIGH);
  digitalWrite(ENB, HIGH);

  Serial.begin(115200);
  WiFi.begin("team1", "team1pass");
 
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting...");
  }
 
  Serial.println("Connected to WiFi");
 
  if (!MDNS.begin("esp32")) {
    Serial.println("Error setting up MDNS responder!");
    return;
  }
 
  Serial.println("mDNS responder started");
 
  // Resolve Micro-ROS Agent's IP dynamically
  IPAddress agentIP = MDNS.queryHost("team1"); // Resolving team1.local
 
  if (agentIP) {
    Serial.print("Resolved Micro-ROS Agent IP: ");
    Serial.println(agentIP);
 
    // Convert IP to a mutable char array
    char ipStr[16];  // Buffer to store the IP as a string
    snprintf(ipStr, sizeof(ipStr), "%s", agentIP.toString().c_str());
 
    // Pass the mutable string to set_microros_wifi_transports()
    set_microros_wifi_transports("team1", "team1pass", ipStr, 8888);
 
  } else {
    Serial.println("Micro-ROS Agent not found!");
    return;
  }
 
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);
 
  allocator = rcl_get_default_allocator();
  RCCHECK(rclc_support_init(&support, 0, NULL, &allocator));
  RCCHECK(rclc_node_init_default(&node, "micro_ros_arduino_node", "", &support));
  RCCHECK(rclc_subscription_init_default(
    &subscriber,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
    "motor_control"));
 
  RCCHECK(rclc_executor_init(&executor, &support.context, 1, &allocator));
  RCCHECK(rclc_executor_add_subscription(&executor, &subscriber, &msg, &subscription_callback, ON_NEW_DATA));
}
 
void loop() {
  delay(100);
  rcl_ret_t ret = rclc_executor_spin_some(&executor, RCL_MS_TO_NS(100));
  if (ret != RCL_RET_OK) {
    Serial.println("Error in executor. Reinitializing...");
    reset_micro_ros();
  }
 
  if (millis() - last_received_time > TIMEOUT_INTERVAL) {
    stopMotors();
  }
}

void reset_micro_ros() {
  stopMotors();
  digitalWrite(LED_PIN, LOW);
  rclc_executor_fini(&executor);
 
  allocator = rcl_get_default_allocator();
  rclc_support_init(&support, 0, NULL, &allocator);
  rclc_node_init_default(&node, "micro_ros_arduino_node", "", &support);
  rclc_subscription_init_default(
    &subscriber,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
    "motor_control");
  rclc_executor_init(&executor, &support.context, 1, &allocator);
  rclc_executor_add_subscription(&executor, &subscriber, &msg, &subscription_callback, ON_NEW_DATA);
  delay(2000);
  digitalWrite(LED_PIN, HIGH);
  Serial.println("Micro-ROS reinitialized successfully.");
}

void setMotorSpeed(int speed = -1) {
    if (speed == -1) speed = motor_speed;  // Use default speed if not specified
    ledcWrite(ENA, speed);
    ledcWrite(ENB, speed);
}

void moveForward() {
  setMotorSpeed();
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  Serial.println("Motors moving forward");
}
 
void moveBackward() {
  setMotorSpeed();
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  Serial.println("Motors moving backward");
}
 
void stopMotors() {
  setMotorSpeed(0);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  Serial.println("Motors stopped");
}
 
void turnLeft() {
  setMotorSpeed();
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  Serial.println("Turning left");
}
 
void turnRight() {
  setMotorSpeed();
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  Serial.println("Turning right");
}
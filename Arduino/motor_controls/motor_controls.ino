#include <micro_ros_arduino.h>
 
#include <stdio.h>
#include <rcl/rcl.h>
#include <rcl/error_handling.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>
 
#include <std_msgs/msg/int32.h>
 
rcl_subscription_t subscriber;
std_msgs__msg__Int32 msg;
rclc_executor_t executor;
rclc_support_t support;
rcl_allocator_t allocator;
rcl_node_t node;
rcl_timer_t timer;
 
#define LED_PIN 13
 
#define RCCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){error_loop();}}
#define RCSOFTCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){}}
 
// Define motor driver control pins
#define IN1 32
#define IN2 33
#define IN3 25
#define IN4 26
 
// Define motor PWM control pins (if you want to control speed)
#define ENA 5    // Motor 1 Enable Pin
#define ENB 4    // Motor 2 Enable Pin
 
 
void error_loop(){
  while(1){
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    delay(100);
  }
}
 
void subscription_callback(const void * msgin)
{  
  const std_msgs__msg__Int32 * msg = (const std_msgs__msg__Int32 *)msgin;
 
  // Print the received data to the Serial Monitor
  Serial.print("Received data: ");
  Serial.println(msg->data);
 
  int32_t command = msg->data;  // Read the incoming int32 command
 
  // Debugging output
  Serial.print("Received command from Micro-ROS: ");
  Serial.println(command);
 
  // Control motors based on received Micro-ROS command
  if (command == 1) { // Forward
    moveForward();
  }
  else if (command == 2) { // Backward
    moveBackward();
  }
  else if (command == 3) { // Stop
    stopMotors();
  }
  else if (command == 4) { // Left
    turnLeft();
  }
  else if (command == 5) { // Right
    turnRight();
  }
 
  // Example: Control the LED based on the received data
  digitalWrite(LED_PIN, (msg->data == 0) ? LOW : HIGH);
}
 
 
void setup() {
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
 
 
    // Start Serial Monitor
  Serial.begin(115200);
  set_microros_wifi_transports("IOTLABRA", "iotlabra2020", "172.16.200.11", 8888);
 
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);  
 
  delay(2000);
 
  allocator = rcl_get_default_allocator();
 
  //create init_options
  RCCHECK(rclc_support_init(&support, 0, NULL, &allocator));
 
  // create node
  RCCHECK(rclc_node_init_default(&node, "micro_ros_arduino_node", "", &support));
 
  // create subscriber
  RCCHECK(rclc_subscription_init_default(
    &subscriber,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
    "motor_control"));
 
  // create executor
  RCCHECK(rclc_executor_init(&executor, &support.context, 1, &allocator));
  RCCHECK(rclc_executor_add_subscription(&executor, &subscriber, &msg, &subscription_callback, ON_NEW_DATA));
}
 
void loop() {
  delay(100);
  RCCHECK(rclc_executor_spin_some(&executor, RCL_MS_TO_NS(100)));
}
 
void moveForward() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  Serial.println("Motors moving forward");
}
 
void moveBackward() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  Serial.println("Motors moving backward");
}
 
void stopMotors() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  Serial.println("Motors stopped");
}
 
void turnLeft() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  Serial.println("Turning left");
}
 
void turnRight() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  Serial.println("Turning right");
}
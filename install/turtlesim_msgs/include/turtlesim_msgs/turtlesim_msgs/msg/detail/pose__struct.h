// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from turtlesim_msgs:msg/Pose.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "turtlesim_msgs/msg/pose.h"


#ifndef TURTLESIM_MSGS__MSG__DETAIL__POSE__STRUCT_H_
#define TURTLESIM_MSGS__MSG__DETAIL__POSE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Struct defined in msg/Pose in the package turtlesim_msgs.
typedef struct turtlesim_msgs__msg__Pose
{
  float x;
  float y;
  float theta;
  float linear_velocity;
  float angular_velocity;
} turtlesim_msgs__msg__Pose;

// Struct for a sequence of turtlesim_msgs__msg__Pose.
typedef struct turtlesim_msgs__msg__Pose__Sequence
{
  turtlesim_msgs__msg__Pose * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} turtlesim_msgs__msg__Pose__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // TURTLESIM_MSGS__MSG__DETAIL__POSE__STRUCT_H_

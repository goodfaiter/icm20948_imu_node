#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, MagneticField, Temperature
from std_msgs.msg import Header
import qwiic_icm20948


class ICM20948Node(Node):
    def __init__(self):
        super().__init__("icm20948_node")

        # Hard-coded parameters
        self.i2c_address = 0x69  # Default I2C address
        
        self.poll_rate = 100.0  # Hz

        # Initialize the IMU
        self.imu = qwiic_icm20948.QwiicIcm20948(address=self.i2c_address)

        if not self.imu.isConnected():
            self.get_logger().error("IMU not connected!")
            raise RuntimeError("IMU not connected")

        if not self.imu.begin():
            self.get_logger().error("IMU initialization failed!")
            raise RuntimeError("IMU initialization failed")

        self.get_logger().info("IMU initialized successfully")

        # Create publishers
        self.imu_pub = self.create_publisher(Imu, "imu/data_raw", 10)
        self.mag_pub = self.create_publisher(MagneticField, "imu/mag", 10)
        self.temp_pub = self.create_publisher(Temperature, "imu/temperature", 10)

        # Create timer for polling
        timer_period = 1.0 / self.poll_rate
        self.timer = self.create_timer(timer_period, self.poll_imu)

        self.get_logger().info(f"Publishing IMU data at {self.poll_rate} Hz")

    def poll_imu(self):
        # Check if data is ready
        if not self.imu.dataReady():
            return

        # Read all sensor data
        if not self.imu.getAgmt():
            self.get_logger().warn("Failed to read IMU data")
            return

        # Get current timestamp
        timestamp = self.get_clock().now().to_msg()

        # Publish IMU data (accel + gyro)
        imu_msg = Imu()
        imu_msg.header = Header()
        imu_msg.header.stamp = timestamp
        imu_msg.header.frame_id = "imu_link"

        # Angular velocity (gyroscope) - convert to rad/s
        # Raw values need to be scaled based on full scale range (250 dps)
        gyro_scale = 250.0 / 32768.0 * (3.14159265 / 180.0)  # Convert to rad/s
        imu_msg.angular_velocity.x = self.imu.gxRaw * gyro_scale
        imu_msg.angular_velocity.y = self.imu.gyRaw * gyro_scale
        imu_msg.angular_velocity.z = self.imu.gzRaw * gyro_scale

        # Linear acceleration - convert to m/s^2
        # Raw values need to be scaled based on full scale range (2g)
        accel_scale = 2.0 / 32768.0 * 9.80665  # Convert to m/s^2
        imu_msg.linear_acceleration.x = self.imu.axRaw * accel_scale
        imu_msg.linear_acceleration.y = self.imu.ayRaw * accel_scale
        imu_msg.linear_acceleration.z = self.imu.azRaw * accel_scale

        # Covariances unknown, set to -1
        imu_msg.orientation_covariance[0] = -1.0
        imu_msg.angular_velocity_covariance[0] = -1.0
        imu_msg.linear_acceleration_covariance[0] = -1.0

        self.imu_pub.publish(imu_msg)

        # Publish magnetometer data
        mag_msg = MagneticField()
        mag_msg.header = Header()
        mag_msg.header.stamp = timestamp
        mag_msg.header.frame_id = "imu_link"

        # Convert raw magnetometer values to Tesla
        # AK09916 has 0.15 µT/LSB sensitivity
        mag_scale = 0.15e-6  # Convert to Tesla
        mag_msg.magnetic_field.x = self.imu.mxRaw * mag_scale
        mag_msg.magnetic_field.y = self.imu.myRaw * mag_scale
        mag_msg.magnetic_field.z = self.imu.mzRaw * mag_scale

        # Covariance unknown
        mag_msg.magnetic_field_covariance[0] = -1.0

        self.mag_pub.publish(mag_msg)

        # Publish temperature data
        temp_msg = Temperature()
        temp_msg.header = Header()
        temp_msg.header.stamp = timestamp
        temp_msg.header.frame_id = "imu_link"

        # Convert raw temperature to Celsius
        # Formula: Temperature in °C = (TEMP_OUT / 333.87) + 21.0
        temp_msg.temperature = (self.imu.tmpRaw / 333.87) + 21.0
        temp_msg.variance = 0.0  # Unknown

        self.temp_pub.publish(temp_msg)


def main(args=None):
    rclpy.init(args=args)

    try:
        node = ICM20948Node()
        rclpy.spin(node)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        rclpy.shutdown()


if __name__ == "__main__":
    main()

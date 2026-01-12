from setuptools import setup

package_name = 'icm20948_imu_node'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Valentin Yuryev',
    maintainer_email='valentin.yuryev@epfl.ch',
    description='ICM20948 IMU ROS2 node.',
    license='MIT',
    entry_points={
        'console_scripts': [
                'icm20948_imu_node = icm20948_imu_node.icm20948_imu_node:main',
        ],
    },
)

import os
from glob import glob
from setuptools import setup, find_packages

package_name = 'panda'

data_files = [
    ('share/ament_index/resource_index/packages',
     ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    (os.path.join('share', package_name, 'launch'),
 glob('launch/*.launch.py')),
]

for folder in ['launch', 'urdf', 'config']:
    data_files.append((
        os.path.join('share', package_name, folder),
        glob(os.path.join(folder, '*'))
    ))

for root, dirs, files in os.walk('meshes'):
    for filename in files:
        source = os.path.join(root, filename)
        destination = os.path.join('share', package_name, root)
        data_files.append((destination, [source]))

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=data_files,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ossama',
    maintainer_email='',
    description='Franka Panda ROS 2 simulation',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [],
    },
)


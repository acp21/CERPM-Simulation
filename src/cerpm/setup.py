from setuptools import find_packages, setup

package_name = 'cerpm'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools',
                      'pandas'],
    zip_safe=True,
    maintainer='acp',
    maintainer_email='acp@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
                'talker = cerpm.publisher_member_function:main',
                'listener = py_pubsub.subscriber_member_function:main',
                'cerpm = cerpm.cerpm:main',
                'cerpm_listener = cerpm.cerpm_listener:main',
                'cerpm_detector = cerpm.cerpm_detector:main'
        ],
    },
)

from setuptools import find_packages
from setuptools import setup

REQUIRED_PACKAGES = [
  'tensorflow >=1.15'
]

EXTENSION_NAME = 'fl_comm_libs/fl_rpc_bridge.so'

setup(name='fl_comm_libs',
    version='0.1',
    description='comm libs for jdfl',
    author='JD Inc.',
    packages=find_packages('fl_comm_libs'),
    install_requires=REQUIRED_PACKAGES,
    include_package_data=True,
    package_data={
        'fl_comm_libs': [
            EXTENSION_NAME,
            'fl_comm_libs/*.sh'
        ],
    },
    license='Apache 2.0',
)

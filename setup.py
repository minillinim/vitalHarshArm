from distutils.core import setup

setup(
    name='vitalHarshArm',
    version='0.0.1',
    author='Michael Imelfort',
    author_email='mike@mikeimelfort.com',
    packages=['vitalharsharm', 'vitalharsharm.test'],
    scripts=['bin/vitalHarshArm'],
    url='http://pypi.python.org/pypi/vitalHarshArm/',
    license='GPLv3',
    description='vitalHarshArm',
    long_description=open('README.rst').read(),
    install_requires=[],
    package_data={'vitalharsharm': ['inc/MemManager.h', 'inc/IdTypeDefs.h', 'inc/intdef.h']}
)

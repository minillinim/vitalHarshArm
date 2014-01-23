from distutils.core import setup

setup(
    name='vitalHarshArm',
    version='0.1.0',
    author='Michael Imelfort',
    author_email='mike@mikeimelfort.com',
    packages=['vitalharsharm'],
    scripts=['bin/vitalHarshArm'],
    url='http://pypi.python.org/pypi/vitalHarshArm/',
    license='LGPLv2.1',
    description='vitalHarshArm',
    long_description=open('README.md').read(),
    install_requires=[],
    package_data={'vitalharsharm': ['inc/memManager.h', 'inc/idTypeDefs.h', 'inc/intdef.h', 'inc/paranoid.cpp', 'inc/paranoid.h', 'inc/h_template', 'inc/Makefile', 'inc/test.cpp']}
)

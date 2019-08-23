from distutils.core import setup

setup(
    name='Chia Proof of Space',
    version='0.2',
    packages=['src/python'],
    license='Apache License',
    install_requires=['pytest', 'cppimport', 'bitstring'],
    long_description=open('README.md').read(),
)

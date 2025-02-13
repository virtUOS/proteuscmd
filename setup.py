from setuptools import setup
import os

description_text = 'A command line interface to modify DNS entries in Proteus.'


def read(filename):
    path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(path, filename), encoding='utf-8') as f:
        return f.read()


setup(
    name='proteuscmd',
    version='1.0',
    description=description_text,
    url='https://github.com/virtUOS/proteuscmd',
    author='Lars Kiesow',
    author_email='lkiesow@uos.de',
    license='MIT',
    packages=['proteuscmd'],
    license_files=('LICENSE'),
    include_package_data=True,
    install_requires=read('requirements.txt').split(),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': ['proteuscmd = proteuscmd.__main__:main'],
    })

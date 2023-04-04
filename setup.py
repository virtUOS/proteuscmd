'''
Copyright 2022, ELAN e.V. <kontakt-elan@elan-ev.de>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from setuptools import setup
import os

description_text = 'A command line interface to modify DNS entries in Proteus.'


def read(filename):
    path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(path, filename), encoding='utf-8') as f:
        return f.read()


setup(
    name='proteus-cli',
    version='0.1',
    description=description_text,
    url='https://github.com/virtUOS/proteus-cli',
    author='Lars Kiesow',
    author_email='lkiesow@uos.de',
    license='MIT',
    packages=['proteuscli'],
    license_files=('LICENSE'),
    include_package_data=True,
    install_requires=read('requirements.txt').split(),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': ['proteus-cli = proteuscli.__main__:main'],
    })

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fp:
    long_description = fp.read()

setup(
    name='easy_ass',
    version='1.0.0beta.1',
    keywords=['ass', 'subtitle'],
    description='An ass subtitle parsing library. ',
    license='MIT Licence',
    long_description=long_description,

    url='https://github.com/hihkm/easyAss',
    author='tikm',
    author_email='hkm@tikm.org',

    packages=find_packages(where='easy_ass'),
    include_package_data=True,
    platforms='all',
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'easy_ass'},
    python_requires='>=3.7',
)

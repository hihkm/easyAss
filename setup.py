from setuptools import setup

with open(r'README.md', 'r', encoding='utf-8') as fp:
    long_description = fp.read()

setup(
    name='easyass',
    version='1.0.0b7',
    keywords=['ass', 'subtitle'],
    description='An ass subtitle parsing library',
    license='MIT Licence',
    long_description=long_description,
    long_description_content_type="text/markdown",

    url='https://github.com/hihkm/easyAss',
    author='tikm',
    author_email='hkm@tikm.org',

    include_package_data=True,
    platforms='all',
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'easyass'},
    python_requires='>=3.7',
)

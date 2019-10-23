from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

long_description = """An online disk server compatible with Apple's Remote Disc service.
Providing a server side component allowing Linux servers to share disk images and optical
drives to remote Mac OS clients."""


setup(
    name='pyods',
    version='0.1',
    author='Karl Lattimer',
    author_email='karl@qdh.org.uk',
    url='https://github.com/klattimer/pyods',
    description='Remote disc server for macos clients',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pyods=pyods:main'
        ]
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",
    ),
    data_files=[
        ('config', ['data/config.json'])
    ],
    keywords='remote disc cd dvd macos',
    install_requires=requirements,
    zip_safe=False
)

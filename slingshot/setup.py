"""Setup script for Slingshot."""
from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='slingshot-scanner',
    version='0.1.0',
    author='Your Name',
    description='Stock scanner for high-probability slingshot setups',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/slingshot',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial :: Investment',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    install_requires=[
        'yfinance>=0.2.32',
        'pandas>=2.0.0',
        'numpy>=1.24.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'slingshot=slingshot.__main__:main',
        ],
    },
)

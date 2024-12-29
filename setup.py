from setuptools import setup, find_packages

setup(
    name="messaging_app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'pillow',
        'requests',
        'typing',
        'dataclasses',
        'python-dateutil',
        'pyheif'
    ],
    python_requires='>=3.7',
)
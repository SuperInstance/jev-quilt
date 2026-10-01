from setuptools import setup, find_packages
setup(
    name='jev-quilt',
    version='0.0.1',
    description='JEV for quilt as understood output: cellular-first decision substrate',
    long_description='JEV (Joint Embedding Validator) as understood output for the Quilt project. Pins the fleet canary: fnv1a-64("café Δ 日本語") = 0x024a555471370b18d. Includes backends, bookkeeper, cell, q16, and typesafe_client.',
    long_description_content_type='text/markdown',
    readme='README.md',
    packages=find_packages(exclude=['tests', 'docs', 'ports']),
    python_requires='>=3.10',
    install_requires=[],
    license='MIT',
)

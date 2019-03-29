from setuptools import setup

microlib_name = 'metasub_utils.packet_parse'

requirements = [
    'capalyzer',
    'pandas',
]

setup(
    name=microlib_name,
    version='0.1.0',
    author='David Danko',
    author_email='dcdanko@gmail.com',
    license='MIT license',
    entry_points={
        'console_scripts': [
        ]
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    namespace_packages=['packet_parse'],
    packages=[microlib_name],
    install_requires=requirements,
)

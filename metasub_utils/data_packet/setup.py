from setuptools import setup

microlib_name = 'metasub_utils.data_packet'

requirements = [
    'click',
    'metasub_utils.metadata'
]

setup(
    name=microlib_name,
    version='0.2.0',
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
    namespace_packages=['metasub_utils'],
    packages=[microlib_name],
    install_requires=requirements,
)

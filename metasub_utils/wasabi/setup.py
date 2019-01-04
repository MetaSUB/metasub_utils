from setuptools import setup

microlib_name = 'metasub_utils.wasabi'

requirements = [
    'metasub_utils.metadata',
    'boto3',
    'awscli',
    'click',
]

setup(
    name=microlib_name,
    version='0.4.0',
    author='David Danko',
    author_email='dcdanko@gmail.com',
    license='MIT license',
    entry_points={
        'console_scripts': [
            'metasub-wasabi=metasub_utils.wasabi.cli:wasabi'
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

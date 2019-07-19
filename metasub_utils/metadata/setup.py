from setuptools import setup

microlib_name = 'metasub_utils.metadata'

requirements = [
    'pandas',
    'click',
]

setup(
    name=microlib_name,
    version='0.4.0',
    author='David Danko',
    author_email='dcdanko@gmail.com',
    license='MIT license',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': [
            'metasub-metadata=metasub_utils.metadata.cli:metadata'
        ]
    },
    namespace_packages=['metasub_utils'],
    packages=[microlib_name],
    install_requires=requirements,
)

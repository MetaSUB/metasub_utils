from setuptools import setup

microlib_name = 'metasub_utils.pangea'

requirements = [
    'pandas',
    'click',
    'requests',
]

setup(
    name=microlib_name,
    version='0.1.0',
    author='David Danko',
    author_email='dcdanko@gmail.com',
    license='MIT license',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
    },
    namespace_packages=['metasub_utils'],
    packages=[microlib_name],
    install_requires=requirements,
)

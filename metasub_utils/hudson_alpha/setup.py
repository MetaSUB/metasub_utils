from setuptools import setup

microlib_name = 'metasub_utils.hudson_alpha'

requirements = [
    'requests',
]

setup(
    name=microlib_name,
    version='0.3.1',
    author='David Danko',
    author_email='dcdanko@gmail.com',
    license='MIT license',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    namespace_packages=['metasub_utils'],
    packages=[microlib_name],
    install_requires=requirements,
    package_data={microlib_name: [
        'hudson_alpha_flowcells.csv',
    ]},
)

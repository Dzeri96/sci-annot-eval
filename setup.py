from setuptools import setup, find_packages

setup(
    name='sci_annot_eval',
    version='0.0.4',
    description='The evaluation component of the sci-annot framework',
    author='Dzeri96',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9'
    ],
    keywords=['sci-annot', 'object', 'detection', 'evaluation'],
    python_requires='>=3.9, <4',
    install_requires=['numpy>=1.21', 'lapsolver>=1.1'],
    packages=find_packages()
)
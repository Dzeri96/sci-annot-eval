from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='sci_annot_eval',
    version='0.0.7',
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
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'sci_annot_eval=cli_entrypoint:main'
        ]
    },
    url='https://github.com/Dzeri96/sci-annot-eval',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
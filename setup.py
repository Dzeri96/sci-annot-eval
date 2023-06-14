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
    install_requires=['coloredlogs==15.0.1', "humanfriendly==10.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'", 'lapsolver==1.1.0', 'mypy==1.3.0', "mypy-extensions==1.0.0; python_version >= '3.5'", 'numpy==1.22.3', 'opencv-python==4.5.5.64', 'pandas==1.4.2', 'pdf2image==1.16.0', "pillow==9.3.0; python_version >= '3.7'", 'pyarrow==7.0.0', "python-dateutil==2.8.2; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'", 'pytz==2022.1', "six==1.16.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'", "tomli==2.0.1; python_version < '3.11'", "typing-extensions==4.6.3; python_version >= '3.7'"],
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
# ![logo](./README_assets/logo-tiny.webp)Sci-Annot Evaluation Component
[![PyPI version](https://badge.fury.io/py/sci-annot-eval.svg)](https://badge.fury.io/py/sci-annot-eval)
![Build & Test Pipeline](https://github.com/dzeri96/sci-annot-eval/actions/workflows/build-test-publish.yaml/badge.svg)

This package was developed as part of my master's thesis and used in the evaluation stage.

Its main purpose is to produce per-page confusion matrices with multiple classes for predictions in the field of Page Object Detection, with inter-object dependencies also supported.
To be more precise, it was used to compare predictions in the task of figure, table and caption extraction, but the project can somewhat easily be extended to other object types.

## Features
This tool currently supports the following commands:
- `rasterize` - Rasterize all pdfs in input folder and additionally produce a summary parquet file called render_summary.parquet in the output folder.
- `split-pdffigures2` - Take original pdffigures2 output and split it into validator-friendly per-page files.
- `benchmark` - Evaluate predictions against a ground truth and produce TP, FP, and FN metrics for each page.
- `deepfigures-predict` - Use deepfigures to detect elements from each pdf in the input folder.
- `transpile` - Take a folder of predictions in one format and output them in another.

Currently, the following prediction formats are supported:
- [Sci-Annot](https://github.com/Dzeri96/sci-annot) - The corresponding annotation front-end.
- [PDFFigures 2.0](https://github.com/allenai/pdffigures2)
- [DeepFigures](https://github.com/allenai/deepfigures-open)

_Consider contributing a parser/exporter for your system of choice!_

### How the Validation Works
The comparison of two sets of bounding boxes is modelled as an optimal assignment problem,
with the cost function being the distance between the centres of bounding boxes.
The matching algorithm runs inside each class (Figues, Tables, Captions) individually,
and uses the Intersection over Union (IoU) to decide if two bounding boxes match.
This means that if two bounding boxes look the same, but have different classes,
no True Positives will be counted towards either of those classes.
This is in contrast to some other validation schemes which award partial points in such cases.

The reference validation runs for all referenced classes at the same time (Figures and Tables in our case),
and does not take the bounding boxes' shape or class into account,
only if its reference matches the closest bounding box in the corresponding prediction set.
For more information on how this works, refer to the thesis which spawned this project.

## Installation & Usage
This tool is packaged under the name [sci-annot-eval](https://pypi.org/project/sci-annot-eval/).

You can install it like `pip install sci-annot-eval`, or `conda install sci-annot-eval`.

Once installed, call the package from your cli `sci-annot-eval COMMAND`, or use it as a library in your python project.

## Development Setup
If you wish to work on this project locally, you'll need:
- python3.9+
- pipenv

To set up the dependencies, just run `pipenv install` in the project root.
From that point on, you can do `pipenv shell`, which will launch your custom python environment with all of the dependencies installed.

When developing, you can call `python3 cli.py` in the project root to execute the local version of sci-annot-eval, instead of the installed one. 

## TODO
- Fix logging
- Add more tests
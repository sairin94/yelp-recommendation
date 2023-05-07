# Yelp Data Analysis

Provide a brief introduction to your project here.

## Directory Structure

The project directory is structured as follows:

```
├── README.md
├── notebooks
│   └── explore_dataset.ipynb
├── requirements.txt
├── setup.py
└── src
    ├── components
    │   ├── data_ingestion.py
    │   ├── data_transformation.py
    │   └── model_trainer.py
    ├── exception.py
    ├── logger.py
    ├── pipeline
    │   ├── predict_pipeline.py
    │   └── train_pipeline.py
    └── utils.py
```

- **README.md**: This file provides an overview of the project and instructions for use.
- **requirements.txt**: This file lists the Python packages required to run the project.
- **setup.py**: This file is used to install the project as a Python package.
- **src**: This directory contains the source code for the project.
- **notebooks**: This directory contains the Jupyter Notebooks used to explore the dataset.

## Installation

To install the project, follow these steps:

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Create and activate a virtual environment for the project (recommended).
4. Install the required Python packages using `pip install -r requirements.txt`.
5. Install the project as a package using `pip install .`.

## Usage

To use the project, follow these steps:

1. Ensure that the virtual environment is activated (if you created one).
2. Import the project package into your Python code using `import <package_name>`.
3. Use the package functions and classes as desired.
4. To run the Jupyter Notebook, navigate to `notebooks/` and run `jupyter notebook explore_dataset.ipynb`.
5. To access AWS server you need to run from root directory `cp access_keys.cfg.template access_keys.cfg` and then populate with your keys
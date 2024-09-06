# Django Flow Viz Toolkit

![Flowchart Example](https://raw.githubusercontent.com/arifbd2221/django-flow-viz/main/flowcharts/project_flowchart.png)

A Django management command that generates flowcharts for your Django project, including models, URLs, middleware, and signals.

You can find this package on [PyPI](https://pypi.org/project/django-flow-viz-toolkit/).

## Features
- Generates project-wide or app-wise flowcharts.
- Visualizes Django models, URLs, middleware, and signals.
- Uses PyGraphviz to render flowcharts.

## Installation

1. We will use pygraphviz to generate the flowcharts. Install it via pip:
   ```
   pip install pygraphviz
   ```
   If you face any issues, you might need to install Graphviz on your system first. For example, on Ubuntu, you can run:
   ```
   sudo apt-get install graphviz
   ```

2. Install the package using pip:
   ```
   pip install django-flow-viz-toolkit
   ```

## Configuration
After installation, include `django-flow-viz-toolkit` in the `INSTALLED_APPS` in your Django project's `settings.py`:

```
INSTALLED_APPS = [
    ...
    'flowchart_visualizer',
    ...
]
```

## Usage
Run the management command to generate the flowchart:
```
python manage.py generate_flowchart
```

To generate app-wise flowcharts:
```
python manage.py generate_flowchart --app-wise
```

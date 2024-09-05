from setuptools import setup, find_packages

setup(
    name='django-flow-viz-toolkit',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=3.0,<5.2',  # Support Django 3.0 to 5.1
        'pygraphviz>=1.13',  # Specifying the tested version of pygraphviz
        'tqdm>=4.66.5',      # Specifying the tested version of tqdm
    ],
    entry_points={
        'console_scripts': [
            'generate-flowchart = flowchart_visualizer.management.commands.generate_flowchart:Command',
        ],
    },
    license='MIT',       # Choose an appropriate license
    description='A tool to generate flowcharts for Django projects',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Mohidul Hoque Arif',
    author_email='mohidulhoque216@gmail.com',
    url='https://github.com/arifbd2221/django-flow-viz-toolkit',  # Your GitHub URL
    keywords=[
        'django',
        'flowchart',
        'visualization',
        'model relationships',
        'django models',
        'URL mapping',
        'middleware visualization',
        'signal visualization',
        'graph generation',
        'pygraphviz',
        'Django management commands',
        'process visualization',
        'Django package',
        'project visualization',
        'Django tools',
        'developer tools'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Intended Audience :: Developers',
    ],
    python_requires='>=3.7',
)

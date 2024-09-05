import os
import pygraphviz as pgv
from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings
from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver
from tqdm import tqdm  # For the progress bar
from flowchart_visualizer.utils import check_model_signals



class Command(BaseCommand):
    help = "Generate flowchart for Django models, views, URLs, middleware, and signals"

    def add_arguments(self, parser):
        # Add a command-line option to choose between project-wide and app-wise flowchart
        parser.add_argument(
            '--app-wise',
            action='store_true',
            help="Generate app-wise flowcharts for each Django app separately",
        )
        parser.add_argument(
            '--project-wide',
            action='store_true',
            help="Generate a single flowchart for the entire Django project (default)",
        )
    
    def get_view_name(self, pattern):
        """ Get a proper name for the view, handle class-based views """
        try:
            # Function-based views have a callback with a __name__
            if hasattr(pattern.callback, '__name__') and pattern.callback.__name__ != 'view':
                return pattern.callback.__name__

            # Class-based views wrapped in as_view() (Django uses __self__ to hold the class)
            if hasattr(pattern.callback, 'view_class'):
                return pattern.callback.view_class.__name__

            # Fallback for unusual or custom views
            return str(pattern.callback)

        except Exception as e:
            #print(f"Error resolving view for pattern: {pattern.pattern}: {e}")
            return str(pattern.callback)

    def handle(self, *args, **options):
        # Check whether to generate app-wise or project-wide flowchart
        if options['app_wise']:
            self.stdout.write("Generating app-wise flowcharts...")
            self.generate_app_wise_flowcharts()
        else:
            self.stdout.write("Generating project-wide flowchart...")
            self.generate_project_wide_flowchart()
    
    
    def generate_project_wide_flowchart(self):
        """ Generate a single flowchart for the entire Django project """
        graph = pgv.AGraph(directed=True)

        # Generate flowcharts
        self.generate_model_flowchart(graph)
        self.generate_url_flowchart(graph)
        self.generate_middleware_flowchart(graph)
        self.generate_signal_flowchart(graph)

        # Output directory and file
        output_dir = os.path.join(settings.BASE_DIR, 'flowcharts')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'project_flowchart.png')

        # Render and save the flowchart
        graph.layout(prog='dot')
        graph.draw(output_file)

        self.stdout.write(self.style.SUCCESS(f'Project-wide flowchart generated at {output_file}'))

    def generate_app_wise_flowcharts(self):
        """ Generate individual flowcharts for each Django app """
        developer_apps = [app for app in apps.get_app_configs() if not app.name.startswith('django.contrib')]
        
        for app_config in developer_apps:
            app_name = app_config.name
            graph = pgv.AGraph(directed=True)

            self.stdout.write(f"Generating flowchart for app: {app_name}")

            # Generate flowcharts for this specific app
            self.generate_model_flowchart(graph, app_name=app_name)
            self.generate_url_flowchart(graph, app_config=app_config)
            self.generate_signal_flowchart(graph, app_name=app_name)

            # Output directory and file
            output_dir = os.path.join(settings.BASE_DIR, 'flowcharts', app_name)
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f'{app_name}_flowchart.png')

            # Render and save the flowchart
            graph.layout(prog='dot')
            graph.draw(output_file)

            self.stdout.write(self.style.SUCCESS(f'Flowchart for app {app_name} generated at {output_file}'))
    
    

    def generate_model_flowchart(self, graph, app_name=None):
        """ Add model relationships to the graph """
        models = apps.get_models()
        total_models = len(models)
        
        if app_name:
            models = [model for model in models if model._meta.app_label == app_name]
        
        self.stdout.write("Generating model flowchart...")
        
        for model in tqdm(models, desc="Models", unit="model"):
            graph.add_node(model.__name__)
            for field in model._meta.get_fields():
                if field.is_relation and field.related_model:
                    graph.add_edge(model.__name__, field.related_model.__name__)
        
        self.stdout.write(self.style.SUCCESS(f"Model flowchart generated for {total_models} models"))

    def generate_url_flowchart(self, graph, app_config=None):
        """ Add URL and view relationships to the graph """
        resolver = get_resolver()
        url_patterns = resolver.url_patterns
        
        self.stdout.write("Generating URL flowchart...")
        
        def view_belongs_to_app(pattern, app_config):
            """ Check if a view belongs to a specific app based on its module path """
            try:
                # Get the module where the view is defined
                if hasattr(pattern.callback, '__module__'):
                    view_module = pattern.callback.__module__
                    # Check if the view's module starts with the app's name
                    return view_module.startswith(app_config.name)
                else:
                    return False
            except Exception as e:
                print(f"Error processing view {pattern.callback}: {e}")
                return False

        def process_urlpatterns(patterns, parent="ROOT"):
            for pattern in tqdm(patterns, desc="URLs", unit="url"):
                if isinstance(pattern, URLPattern):
                    # Handle function-based or class-based views
                    view_name = self.get_view_name(pattern)
                    url_path = str(pattern.pattern)
                    # print(f"Processing URLPattern: {url_path} -> {view_name}")
                    
                    # If app_config is passed, only process URLs related to the app
                    if app_config and not view_belongs_to_app(pattern, app_config):
                        continue
                    # else:
                    #     # Skip views that don't belong to any developer-created apps
                    #     if not is_developer_view(view_name):
                    #         continue
                    
                    graph.add_node(view_name, label=f"View: {view_name}\nPath: {url_path}")
                    graph.add_edge(parent, view_name)

                elif isinstance(pattern, URLResolver):
                    # Handle included URL configurations
                    url_path = str(pattern.pattern)
                    
                    # Skip global URLs like admin for app-wise generation
                    if app_config and ('admin' in url_path or 'auth' in url_path):
                        continue
                    
                    # print(f"Processing URLResolver: {url_path}")
                    graph.add_node(url_path, label=f"URL: {url_path}")
                    graph.add_edge(parent, url_path)
                    
                    # Recursively process the included URLs
                    included_patterns = pattern.url_patterns
                    process_urlpatterns(included_patterns, url_path)

        process_urlpatterns(url_patterns)
        self.stdout.write(self.style.SUCCESS("URL flowchart generation completed"))
    
    def generate_middleware_flowchart(self, graph):
        """ Visualize middleware flow """
        middleware_list = settings.MIDDLEWARE
        prev_middleware = "Request Start"
        
        self.stdout.write("Generating middleware flowchart...")

        for middleware in tqdm(middleware_list, desc="Middleware", unit="mw"):
            graph.add_node(middleware, label=f"Middleware: {middleware}")
            graph.add_edge(prev_middleware, middleware)
            prev_middleware = middleware

        graph.add_edge(prev_middleware, "Request End")
        self.stdout.write(self.style.SUCCESS(f"Middleware flowchart generated for {len(middleware_list)} middleware"))
    
    
    def generate_signal_flowchart(self, graph, app_name=None):
        """ Add model signals and their receivers to the graph """
        models = apps.get_models()
        
        if app_name:
            models = [model for model in models if model._meta.app_label == app_name]
        
        self.stdout.write("Generating signals flowchart...")
        
        for model in tqdm(models, desc="Signals", unit="signal"):
            check_model_signals(graph, model)
        
        self.stdout.write(self.style.SUCCESS(f"Signals flowchart generated for {len(models)} models"))

import os
import importlib
import inspect
from kurisu.core.database.methods import create_or_update_plugin

def has_decorator(func, decorator_name):
    """
    Check if a function has the given decorator.
    """
    return any(decorator_name in str(dec) for dec in func.__decorators__)

def get_py_files_recursive(directory):
    py_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    return py_files

def get_cogs_info():
    result = []

    # Get the list of all Python files in the cogs directory and its subdirectories
    cogs_dir = 'kurisu/cogs'
    py_files = get_py_files_recursive(cogs_dir)
    for file_path in py_files:
        module_path = os.path.splitext(file_path)[0]
        module_name = module_path.replace('/', '.').replace('\\', '.')

        module = importlib.import_module(module_name)

        # Iterate through all the items in the module
        for name, obj in inspect.getmembers(module):
            if (inspect.iscoroutinefunction(obj)):
                group = module.__name__.split('.')[2] if len(module.__name__.split('.')) > 2 else None
                version = "v1"
                description = obj.__doc__ if obj.__doc__ else None
                handlers = obj.handlers
                result.append({
                    "group": group,
                    "handler": handlers,
                    "name": name,
                    "description": description,
                    "version": version
                })

    return result

def initalize_plugins():
    cogs_info = get_cogs_info()
    for cog in cogs_info:
        create_or_update_plugin(
            name=cog["name"],
            version=cog["version"],
            description=cog["description"],
            group=cog["group"],
        )
        

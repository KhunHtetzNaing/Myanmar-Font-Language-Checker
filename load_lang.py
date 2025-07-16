import os, sys


def load_language_data(lang_package_name="lang"):
    """
    Loads all language character data from Python modules within the specified package.
    Each module is expected to define a dictionary named 'LANGUAGE_DATA'.
    Returns a dictionary where keys are language names and values are lists of character code points.
    """
    languages_data = {}

    # Ensure the parent directory of 'lang' is in sys.path
    # This assumes 'lang' is a sibling to check_fonts.py
    script_dir = os.path.dirname(__file__)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    try:
        # Dynamically import the 'lang' package
        lang_package = __import__(lang_package_name)

        # Iterate through files in the 'lang' directory (package)
        # This is a bit of a hack to discover modules within the package
        # For a more robust solution with dynamic module discovery,
        # you might still fall back to os.listdir or explore pkgutil.iter_modules
        lang_dir_path = os.path.join(script_dir, lang_package_name)
        if not os.path.exists(lang_dir_path):
            print(f"Error: Language directory '{lang_dir_path}' not found.")
            return languages_data

        for filename in os.listdir(lang_dir_path):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]  # Remove .py extension
                full_module_path = f"{lang_package_name}.{module_name}"

                try:
                    # Import the specific language module from the package
                    # This will execute the module and make LANGUAGE_DATA available
                    lang_module = __import__(full_module_path, fromlist=['LANGUAGE_DATA'])

                    if hasattr(lang_module, 'LANGUAGE_DATA'):
                        data = lang_module.LANGUAGE_DATA
                        lang_name = data.get("name")
                        char_codes = data.get("characters", [])

                        if lang_name and char_codes is not None:
                            languages_data[lang_name] = char_codes
                        else:
                            print(
                                f"Warning: '{filename}' in '{lang_package_name}' is missing 'name' or 'characters' key in LANGUAGE_DATA.")
                    else:
                        print(
                            f"Warning: '{filename}' in '{lang_package_name}' does not contain 'LANGUAGE_DATA'. Skipping.")

                except ImportError as e:
                    print(f"Error importing language module '{full_module_path}': {e}")
                except Exception as e:
                    print(f"An unexpected error occurred with '{filename}': {e}")

    except ImportError as e:
        print(f"Error importing language package '{lang_package_name}': {e}")
        print("Please ensure the 'lang' directory exists and contains an __init__.py file.")
    finally:
        # Clean up sys.path if we added it
        if script_dir in sys.path:
            sys.path.remove(script_dir)

    return languages_data

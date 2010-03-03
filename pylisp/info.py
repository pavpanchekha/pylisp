import os

package_folder = os.path.abspath(os.path.split(__file__)[0])
lib_folder = os.path.join(package_folder, "stdlib")

def lib(name):
    return open(os.path.join(lib_folder, name + ".lsp")).read()

import_path = [".", lib_folder]

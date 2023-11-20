import ast
import threading
import importlib
import io
import sys
import contextlib
import math
import builtins
import contextlib
import io

class CodeExecutor:
    def __init__(self):
        self.allowed_libraries = set()
        self.data = None
        self.__exec_finished = False
        self.__error_exec = False
        self.original_import = builtins.__import__

    def add_allowed_library(self, *libraries):
        for lib in libraries:
            self.allowed_libraries.add(lib)

    def _is_library_allowed(self, library):
        return library in self.allowed_libraries

    def _custom_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        if self._is_library_allowed(name):
            return self.original_import(name, globals, locals, fromlist, level)
        else:
            raise ImportError(f"Import of '{name}' is not allowed.")

    def execute_code(self, code):
        try:
            with io.StringIO() as buf, contextlib.redirect_stdout(buf):
                # Temporarily replace the built-in import
                builtins.__import__ = self._custom_import
                exec(code)
                self.data = buf.getvalue().strip()
        except Exception as e:
            print("Error while Executing:", e)
            self.__error_exec = True
        finally:
            # Restore the original import
            builtins.__import__ = self.original_import
            self.__exec_finished = True 

    def execute_code_thread(self, code):
        thread = threading.Thread(target=self.execute_code, args=(code,))
        thread.start()

    def exec_finished(self):
        return self.__exec_finished
    
    def success(self):
        return not self.__error_exec and self.__exec_finished

    def float_compare(self, input_value):
        return math.isclose(float(self.data), input_value)

    def bool_compare(self, input_value):
        return bool(self.data) == input_value

    def str_compare(self, input_value):
        return str(self.data).strip() == input_value

    def int_compare(self, input_value):
        return int(self.data) == input_value

    def list_compare(self, input_value, type):
        try:
            data_list = ast.literal_eval(self.data)
            if not isinstance(data_list, list):
                raise ValueError("Data is not a list")
            typed_data_list = [type(item) for item in data_list]
            return typed_data_list == input_value
        except (ValueError, SyntaxError):
            return False

    def get_code(self, file_path):
        with open(file_path, 'r') as file:
            return file.read()



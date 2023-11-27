import unittest
from AITutor_Backend.src.BackendUtils.code_executor import CodeExecutor

class TestCodeExecutor(unittest.TestCase):

    def test_math_library_execution(self):
        executor = CodeExecutor()
        executor.add_allowed_library('math', 'time.sleep')
        code = '''
import math
result = math.sqrt(16)
print(result)
'''
        executor.execute_code(code)
        while not executor.exec_finished():
            pass

        self.assertTrue(executor.exec_finished())
        self.assertEqual(executor.data, '4.0')

    def test_disallowed_library(self):
        executor = CodeExecutor()
        executor.add_allowed_library('math')
        code = '''
import numpy as np
result = np.array([1, 2, 3])
print(list(result))
'''
        executor.execute_code(code)
        while not executor.exec_finished():
            pass
        self.assertFalse(executor.success())

    def test_basic_string_operation(self):
        executor = CodeExecutor()
        code = '''
result = "Hello, World!"
print(result)
'''
        executor.execute_code(code)
        while not executor.exec_finished():
            pass

        self.assertTrue(executor.exec_finished())
        self.assertEqual(executor.data, 'Hello, World!')

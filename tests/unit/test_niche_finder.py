import unittest
from lib.consumers.niche_finder import NicheFinder
import unittest
from aws_cdk import core
from lib.consumers.niche_finder import NicheFinderStack

class TestNicheFinderStack(unittest.TestCase):

    def setUp(self):
        app = core.App()
        self.stack = NicheFinderStack(app, "TestStack")

    def test_stack_creation(self):
        self.assertIsNotNone(self.stack)

    def test_lambda_function_creation(self):
        self.assertIsNotNone(self.stack.lambda_fn)

    def test_cloudwatch_rule_creation(self):
        self.assertIsNotNone(self.stack.cloud_watch_event)

if __name__ == '__main__':
    unittest.main()
import unittest
from lib.consumers.niche_finder import NicheFinderStack

class TestNicheFinderStack(unittest.TestCase):

    def setUp(self):
        self.stack = NicheFinderStack(None, "TestStack", None)

    def test_lambda_role_creation(self):
        self.assertIsNotNone(self.stack._create_lambda_role())

    def test_lambda_function_creation(self):
        lambda_role = self.stack._create_lambda_role()
        self.assertIsNotNone(self.stack._create_lambda_fn(lambda_role, None, None, None, None, None))

    def test_cloudwatch_rule_creation(self):
        lambda_role = self.stack._create_lambda_role()
        lambda_fn = self.stack._create_lambda_fn(lambda_role, None, None, None, None, None)
        self.assertIsNotNone(self.stack._create_cloudwatch_rule_for_lambda(lambda_fn, None))

if __name__ == '__main__':
    unittest.main()
import unittest
from lib.consumers.niche_finder import NicheFinder
import unittest
import aws_cdk as cdk
from lib.consumers.niche_finder import NicheFinderStack

class TestNicheFinderStack(unittest.TestCase):

    def setUp(self):
        app = cdk.App()
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
    
import unittest
import aws_cdk as cdk
from lib.consumers.niche_finder import NicheFinderStack

class TestNicheFinderStack(unittest.TestCase):

    def setUp(self):
        app = cdk.App()
        self.stack = NicheFinderStack(app, "TestStack")

    def test_stack_creation(self):
        self.assertIsNotNone(self.stack)

    def test_lambda_function_creation(self):
        self.assertIsNotNone(self.stack.lambda_fn)

    def test_cloudwatch_rule_creation(self):
        self.assertIsNotNone(self.stack.cloud_watch_event)

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

import unittest
from unittest.mock import patch

from lib.consumers.niche_finder import NicheFinderStack
from aws_cdk import cdk


# class TestNicheFinderStack(unittest.TestCase):

#     @patch('lib.consumers.niche_finder.NicheFinderStack._create_lambda_role')
#     @patch('lib.consumers.niche_finder.NicheFinderStack._create_lambda_fn')
#     @patch('lib.consumers.niche_finder.NicheFinderStack._create_cloudwatch_rule_for_lambda')
#     def test_stack_construction(self, mock_cloudwatch_rule, mock_lambda_fn, mock_lambda_role):
#         # Simulate successful method calls
#         mock_lambda_role.return_value = True
#         mock_lambda_fn.return_value = True
#         mock_cloudwatch_rule.return_value = True

#         app = cdk.App()
#         stack = NicheFinderStack(app, "TestStack")

#         self.assertIsNotNil(stack)

#     def test_lambda_role_creation(self):
#         stack = NicheFinderStack(None, "TestStack", None)
#         role = stack._create_lambda_role()
#         self.assertIsNotNone(role)  # Assert the role object itself

#     def test_lambda_function_creation(self):
#         # Mock dependencies (assuming these are created elsewhere)
#         mock_lambda_role = unittest.mock.MagicMock()
#         mock_shared_config_data = unittest.mock.MagicMock()
#         mock_prompt_data = unittest.mock.MagicMock()
#         mock_niche_finder_s3_bucket = unittest.mock.MagicMock()
#         mock_niche_finder_queue = unittest.mock.MagicMock()
#         mock_niche_finder_topic = unittest.mock.MagicMock()

#         stack = NicheFinderStack(None, "TestStack", None)
#         lambda_fn = stack._create_lambda_fn(
#             mock_lambda_role, mock_shared_config_data, mock_prompt_data,
#             mock_niche_finder_s3_bucket, mock_niche_finder_queue, mock_niche_finder_topic
#         )

#         self.assertIsNotNone(lambda_fn)  # Assert the Lambda function object

#     def test_cloudwatch_rule_creation(self):
#         # Mock dependencies (assuming these are created elsewhere)
#         mock_lambda_fn = unittest.mock.MagicMock()
#         mock_config_data = unittest.mock.MagicMock()

#         stack = NicheFinderStack(None, "TestStack", None)
#         rule = stack._create_cloudwatch_rule_for_lambda(mock_lambda_fn, mock_config_data)

#         self.assertIsNotNone(rule)  # Assert the CloudWatch rule object

# if __name__ == '__main__':
#     unittest.main()
 
import unittest
import aws_cdk as cdk
from lib.main_infrastructure import MainInfrastructureStack
from lib.shared_constructs.mediator import MediatorStack as MediatorStackClass
from lib.consumers.niche_finder import NicheFinderStack
import backend.app as app


class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = cdk.App()

    def test_main_infrastructure_stack_creation(self):
        stack = MainInfrastructureStack(self.app, "TestStack")
        self.assertIsNotNone(stack)

    def test_mediator_stack_creation(self):
        stack = MediatorStackClass(self.app, "TestStack")
        self.assertIsNotNone(stack)

    def test_niche_finder_stack_creation(self):
        mediator_stack = MediatorStackClass(self.app, "TestMediatorStack")
        stack = NicheFinderStack(self.app, "TestStack", mediator_stack=mediator_stack)
        self.assertIsNotNone(stack)


if __name__ == '__main__':
    unittest.main()

# import unittest
# from unittest.mock import patch

# import aws_cdk as cdk
# from lib.main_infrastructure import MainInfrastructureStack
# from lib.shared_constructs.mediator import MediatorStack as MediatorStackClass
# from lib.consumers.niche_finder import NicheFinderStack
# import app


# class TestApp(unittest.TestCase):

#     def setUp(self):
#         self.app = cdk.App()

#     def test_main_infrastructure_stack_creation(self):
#         stack = MainInfrastructureStack(self.app, "TestStack")
#         self.assertIsNotNone(stack)

#     def test_mediator_stack_creation(self):
#         stack = MediatorStackClass(self.app, "TestStack")
#         self.assertIsNotNone(stack)

#     @patch('lib.shared_constructs.mediator.MediatorStack.get_s3_bucket')
#     @patch('lib.shared_constructs.mediator.MediatorStack.get_sqs_queue')
#     @patch('lib.shared_constructs.mediator.MediatorStack.get_sns_topic')
#     def test_niche_finder_stack_creation(self, mock_get_sns_topic, mock_get_sqs_queue, mock_get_s3_bucket):
#         # Mock methods from MediatorStack (if NicheFinderStack uses them)
#         mock_get_s3_bucket.return_value = unittest.mock.MagicMock()
#         mock_get_sqs_queue.return_value = unittest.mock.MagicMock()
#         mock_get_sns_topic.return_value = unittest.mock.MagicMock()

#         mediator_stack = MediatorStackClass(self.app, "TestMediatorStack")
#         stack = NicheFinderStack(self.app, "TestStack", mediator_stack=mediator_stack)
#         self.assertIsNotNone(stack)

#         # Additional assertions to verify interactions with mocked methods
#         stack.get_s3_bucket()  # Assuming NicheFinderStack uses this
#         mock_get_s3_bucket.assert_called_once_with()  # Verify method call

#     def test_niche_finder_lambda_creation(self):
#         # Mock dependencies for NicheFinderStack (if needed)
#         mock_lambda_role = unittest.mock.MagicMock()
#         mock_shared_config_data = unittest.mock.MagicMock()
#         mock_prompt_data = unittest.mock.MagicMock()

#         mediator_stack = MediatorStackClass(self.app, "TestMediatorStack")
#         stack = NicheFinderStack(self.app, "TestStack", mediator_stack=mediator_stack,
#                                  lambda_role=mock_lambda_role,
#                                  shared_config_data=mock_shared_config_data,
#                                  prompt_data=mock_prompt_data)
#         # ... (rest of the test logic)

#         # Assert Lambda function creation (modify based on implementation)
#         lambda_fn = stack.get_lambda_fn()  # Assuming a getter method
#         self.assertIsNotNone(lambda_fn)

#     # Add more specific tests for functionalities within each stack
#     # (e.g., testing resource properties, interactions with services)

# if __name__ == '__main__':
#     unittest.main()

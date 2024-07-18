import unittest
import aws_cdk as cdk
from lib.main_infrastructure import MainInfrastructureStack
from lib.shared_constructs.mediator import MediatorStack as MediatorStackClass
from lib.consumers.niche_finder import NicheFinderStack
import app


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
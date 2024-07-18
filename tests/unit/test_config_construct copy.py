import unittest
from lib.custom_constructs import ConfigConstruct

class TestConfigConstruct(unittest.TestCase):
    def test_load_consumer_niche_finder_config(self):
        config_file = "configs/consumer-niche-finder.yaml"
        config_construct = ConfigConstruct(None, "Test", config_file)
        # Assertions for consumer-niche-finder.yaml specific configurations

    def test_load_main_infrastructure_config(self):
        config_file = "configs/main-infrastructure.yaml"
        config_construct = ConfigConstruct(None, "Test", config_file)
        # Assertions for main-infrastructure.yaml specific configurations

    def test_load_shared_data_config(self):
        config_file = "configs/shared-data.yaml"
        config_construct = ConfigConstruct(None, "Test", config_file)
        # Assertions for shared-data.yaml specific configurations

import unittest
from lib.custom_constructs import ConfigConstruct

class TestConfigConstruct(unittest.TestCase):
    def test_load_consumer_niche_finder_config(self):
        config_file = "configs/consumer-niche-finder.yaml"
        try:
            # Load the config file
            config_construct = ConfigConstruct(None, "Test", config_file)
            # Assertions for consumer-niche-finder.yaml
            self.assertEqual(config_construct.get_value("api_key"), "your-gemini-api-key")
            self.assertEqual(config_construct.get_value("api_endpoint"), "https://<region>.vertexai.google/v1/projects/<project-id>/locations/<location>/models/<model-id>:generate")
        except FileNotFoundError:
            self.fail(f"Config file '{config_file}' should exist.")
        except Exception as e:
            self.fail(f"Loading the config file '{config_file}' should not raise an exception: {e}")

    def test_load_main_infrastructure_config(self):
        config_file = "configs/main-infrastructure.yaml"
        try:
            # Load the config file
            config_construct = ConfigConstruct(None, "Test", config_file)
            # Assertions for main-infrastructure.yaml

            # Bucket Names
            bucket_names = config_construct.get_value("bucket_names")
            self.assertEqual(bucket_names["niche-finder"], "niche-finder")
            self.assertEqual(bucket_names["affiliate-program"], "affiliate-program")
            self.assertEqual(bucket_names["subscription-service-cost"], "subscription-service-cost")
            self.assertEqual(bucket_names["campaign"], "campaign")
            self.assertEqual(bucket_names["campaign-content"], "campaign-content")
            self.assertEqual(bucket_names["campaign-metrics"], "campaign-metrics")

            # Table Names
            table_names = config_construct.get_value("table_names")
            self.assertEqual(table_names["niche-finder"], "niche-finder")
            self.assertEqual(table_names["affiliate-program"], "affiliate-program")
            self.assertEqual(table_names["subscription-service-cost"], "subscription-service-cost")
            self.assertEqual(table_names["campaign"], "campaign")
            self.assertEqual(table_names["campaign-content"], "campaign-content")
            self.assertEqual(table_names["campaign-metrics"], "campaign-metrics")

            # Topic Names
            topic_names = config_construct.get_value("topic_names")
            self.assertEqual(topic_names["niche-finder"], "niche-finder")
            self.assertEqual(topic_names["affiliate-program"], "affiliate-program")
            self.assertEqual(topic_names["campaign"], "campaign")
            self.assertEqual(topic_names["campaign-content"], "campaign-content")
            self.assertEqual(topic_names["campaign-metrics"], "campaign-metrics")

            # Queue Configs
            queue_configs = config_construct.get_value("queue_configs")
            self.assertEqual(queue_configs["niche-finder"]["name"], "niche-finder")
            self.assertEqual(queue_configs["niche-finder"]["visibility_timeout"], 300)
            self.assertEqual(queue_configs["affiliate-program"]["name"], "affiliate-program")
            self.assertEqual(queue_configs["affiliate-program"]["visibility_timeout"], 300)
            self.assertEqual(queue_configs["campaign"]["name"], "campaign")
            self.assertEqual(queue_configs["campaign"]["visibility_timeout"], 300)
            self.assertEqual(queue_configs["campaign-content"]["name"], "campaign-content")
            self.assertEqual(queue_configs["campaign-content"]["visibility_timeout"], 300)
            self.assertEqual(queue_configs["campaign-metrics"]["name"], "campaign-metrics")
            self.assertEqual(queue_configs["campaign-metrics"]["visibility_timeout"], 300)
        except FileNotFoundError:
            self.fail(f"Config file '{config_file}' should exist.")
        except Exception as e:
            self.fail(f"Loading the config file '{config_file}' should not raise an exception: {e}")

        # Data Stream Name
        self.assertEqual(config_construct.get_value("data_stream_name"), "data-stream")

    def test_load_shared_data_config(self):
        config_file = "configs/shared-data.yaml"
        try:
            # Load the config file
            config_construct = ConfigConstruct(None, "Test", config_file)
            # Assertions for shared-data.yaml
            self.assertEqual(config_construct.get_value("subscription-phone-number"), "+610406252420")
            self.assertEqual(config_construct.get_value("subscription-email-address"), "mfawsaibot@gmail.com")
        except FileNotFoundError:
            self.fail(f"Config file '{config_file}' should exist.")
        except Exception as e:
            self.fail(f"Loading the config file '{config_file}' should not raise an exception: {e}")
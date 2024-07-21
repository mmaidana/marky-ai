import unittest
from unittest.mock import patch
import os
from lambda_handler.consumer.niche_finder import nicheFinder

class TestNicheFinder(unittest.TestCase):

    @patch("boto3.client")
    def test_nicheFinder(self, mock_sns_client):
        # Mock environment variables
        os.environ["NICHE_FINDER_S3_BUCKET_NAME"] = "test-bucket"
        os.environ["NICHE_FINDER_SQS_QUEUE_URL"] = "test-queue-url"
        os.environ["NICHE_FINDER_SNS_TOPIC_ARN"] = "test-topic-arn"
        os.environ["NICHE_FINDER_SNS_PHONE_NUMBER"] = "test-phone-number"
        os.environ["NICHE_FINDER_SNS_EMAIL_ADDRESS"] = "test-email-address"
        os.environ["NICHE_FINDER_PROMPT_DATA"] = "test-prompt-data"

        # Mock SNS client
        mock_publish = mock_sns_client.return_value.publish

        # Call the nicheFinder function
        result = nicheFinder({}, {})

        # Assert the SNS notification is sent
        mock_publish.assert_called_once()

        # Assert the function returns the expected result
        self.assertEqual(result["statusCode"], 200)
        self.assertEqual(result["body"], "\"Niche finder processing completed!\"")

if __name__ == "__main__":
    unittest.main()
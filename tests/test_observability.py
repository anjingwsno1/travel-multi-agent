import logging
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.observability import LOGGER_NAME, configure_logging


class ObservabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        logger = logging.getLogger(LOGGER_NAME)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    def tearDown(self) -> None:
        logger = logging.getLogger(LOGGER_NAME)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    @patch("app.observability.logging.FileHandler")
    def test_configures_one_utf8_file_handler(self, mock_file_handler) -> None:
        handler = MagicMock()
        mock_file_handler.return_value = handler
        logger = configure_logging(Path("output/logs/test.log"))

        mock_file_handler.assert_called_once_with(Path("output/logs/test.log"), encoding="utf-8")
        self.assertEqual(logger.level, logging.INFO)
        self.assertFalse(logger.propagate)
        self.assertEqual(logger.handlers, [handler])

    @patch("app.observability.logging.FileHandler")
    def test_does_not_add_duplicate_handlers(self, mock_file_handler) -> None:
        first_handler = MagicMock()
        mock_file_handler.return_value = first_handler
        configure_logging(Path("output/logs/test.log"))
        configure_logging(Path("output/logs/test.log"))

        mock_file_handler.assert_called_once()

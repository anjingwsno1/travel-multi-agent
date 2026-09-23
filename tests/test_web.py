import unittest
from pathlib import Path
from unittest.mock import patch

from app.web import PDF_DIRECTORY, create_app


class WebTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(run_workflow=lambda query: "/tmp/travel-plan.pdf")
        self.client = self.app.test_client()

    def test_serves_frontend_page(self) -> None:
        response = self.client.get("/")
        try:
            self.assertEqual(response.status_code, 200)
            self.assertIn("旅行规划助手", response.get_data(as_text=True))
        finally:
            response.close()

    def test_creates_plan_with_workflow_result(self) -> None:
        response = self.client.post("/api/travel-plans", json={"query": "规划上海三日游"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["download_url"], "/api/reports/travel-plan.pdf")
        self.assertEqual(response.get_json()["preview_url"], "/api/reports/travel-plan.pdf/preview")

    def test_rejects_empty_query(self) -> None:
        response = self.client.post("/api/travel-plans", json={"query": "  "})

        self.assertEqual(response.status_code, 400)

    def test_rejects_report_outside_pdf_directory(self) -> None:
        response = self.client.get("/api/reports/..%2F.env")

        self.assertEqual(response.status_code, 404)

    @patch("app.web.send_from_directory")
    def test_downloads_existing_report(self, mock_send) -> None:
        with patch.object(Path, "is_file", return_value=True):
            response = self.client.get("/api/reports/sample.pdf")

        self.assertEqual(response.status_code, 200)
        mock_send.assert_called_once_with(PDF_DIRECTORY, "sample.pdf", as_attachment=True)

    @patch("app.web.send_from_directory")
    def test_previews_existing_report_inline(self, mock_send) -> None:
        with patch.object(Path, "is_file", return_value=True):
            response = self.client.get("/api/reports/sample.pdf/preview")

        self.assertEqual(response.status_code, 200)
        mock_send.assert_called_once_with(
            PDF_DIRECTORY, "sample.pdf", as_attachment=False, mimetype="application/pdf"
        )

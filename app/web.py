from pathlib import Path
from typing import Callable

from flask import Flask, jsonify, request, send_from_directory

from app.multi_agent import run_multi_agent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PDF_DIRECTORY = PROJECT_ROOT / "output" / "pdf"
WEB_DIRECTORY = PROJECT_ROOT / "web"


def create_app(run_workflow: Callable[[str], str] = run_multi_agent) -> Flask:
    app = Flask(__name__, static_folder=str(WEB_DIRECTORY), static_url_path="")

    @app.get("/")
    def index():
        return app.send_static_file("index.html")

    @app.post("/api/travel-plans")
    def create_travel_plan():
        payload = request.get_json(silent=True) or {}
        query = str(payload.get("query", "")).strip()
        if not query:
            return jsonify({"error": "请输入旅行需求。"}), 400

        pdf_path = Path(run_workflow(query))
        return jsonify(
            {
                "pdf_path": str(pdf_path),
                "download_url": f"/api/reports/{pdf_path.name}",
                "preview_url": f"/api/reports/{pdf_path.name}/preview",
            }
        )

    @app.get("/api/reports/<filename>")
    def download_report(filename: str):
        report_path = PDF_DIRECTORY / filename
        if Path(filename).name != filename or not report_path.is_file():
            return jsonify({"error": "报告不存在。"}), 404
        return send_from_directory(PDF_DIRECTORY, filename, as_attachment=True)

    @app.get("/api/reports/<filename>/preview")
    def preview_report(filename: str):
        report_path = PDF_DIRECTORY / filename
        if Path(filename).name != filename or not report_path.is_file():
            return jsonify({"error": "报告不存在。"}), 404
        return send_from_directory(
            PDF_DIRECTORY, filename, as_attachment=False, mimetype="application/pdf"
        )

    return app

#!/usr/bin/env python3
"""TextTok — Web interface for TikTok text optimizer & UGC generator.

Usage:
    python web.py              # start on port 5000
    python web.py --port 8080  # custom port
"""

import argparse

from flask import Flask, jsonify, render_template, request

from optimizer import TextAnalyzer, TextTransformer, UGCGenerator

app = Flask(__name__)

analyzer = TextAnalyzer()
transformer = TextTransformer()
generator = UGCGenerator()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/optimize", methods=["POST"])
def api_optimize():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data["text"].strip()
    if not text:
        return jsonify({"error": "Text is empty"}), 400

    topic = data.get("topic", "default")

    result = transformer.optimize(text, topic=topic)

    return jsonify({
        "original": result["original"],
        "optimized": result["optimized"],
        "before_report": _report_to_dict(result["before_report"]),
        "after_report": _report_to_dict(result["after_report"]),
    })


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data["text"].strip()
    if not text:
        return jsonify({"error": "Text is empty"}), 400

    report = analyzer.analyze(text)
    return jsonify(_report_to_dict(report))


@app.route("/api/templates", methods=["GET"])
def api_templates():
    return jsonify(generator.list_templates())


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json()
    if not data or "template" not in data:
        return jsonify({"error": "No template specified"}), 400

    template_id = data["template"]
    count = min(data.get("count", 1), 20)  # cap at 20
    style = data.get("style", "full")
    add_hashtags = data.get("add_hashtags", True)
    add_emojis = data.get("add_emojis", True)

    try:
        results = generator.generate(
            template_id=template_id,
            count=count,
            style=style,
            add_hashtags=add_hashtags,
            add_emojis=add_emojis,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "results": [
            {
                "text": r["text"],
                "style": r["style"],
                "template": r["template"],
                "warnings": r["warnings"],
            }
            for r in results
        ]
    })


def _report_to_dict(report) -> dict:
    return {
        "total_length": report.total_length,
        "sentence_count": report.sentence_count,
        "word_count": report.word_count,
        "avg_sentence_length": report.avg_sentence_length,
        "long_sentences_count": len(report.long_sentences),
        "complex_phrases_count": len(report.complex_phrases_found),
        "complex_phrases_found": report.complex_phrases_found,
        "hashtag_count": report.hashtag_count,
        "existing_hashtags": report.existing_hashtags,
        "emoji_count": report.emoji_count,
        "has_hook": report.has_hook,
        "has_cta": report.has_cta,
        "has_line_breaks": report.has_line_breaks,
        "language": report.language,
        "score": report.score,
        "issues": report.issues,
        "suggestions": report.suggestions,
    }


def main():
    parser = argparse.ArgumentParser(description="TextTok web server")
    parser.add_argument("--port", type=int, default=5000, help="Port (default: 5000)")
    parser.add_argument("--host", default="0.0.0.0", help="Host (default: 0.0.0.0)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    print(f"TextTok web server starting on http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()

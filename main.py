#!/usr/bin/env python3
"""TextTok — TikTok text optimizer CLI.

Optimizes text for TikTok while preserving its original meaning.
Analyzes text against TikTok platform requirements and applies transformations.

Usage:
    python main.py                          # interactive mode
    python main.py --file input.txt         # from file
    python main.py --text "your text here"  # from argument
    python main.py --analyze-only           # only analyze, don't optimize
"""

import argparse
import sys

from optimizer import TextAnalyzer, TextTransformer


TOPICS = [
    "education", "motivation", "life", "tech",
    "business", "health", "food", "travel", "default",
]

SEPARATOR = "=" * 60


def print_header():
    print(SEPARATOR)
    print("  TextTok — TikTok Text Optimizer")
    print(SEPARATOR)
    print()


def read_input_interactive() -> str:
    print("Paste your text below (press Enter twice to finish):")
    print()
    lines = []
    empty_count = 0
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "":
            empty_count += 1
            if empty_count >= 2:
                break
            lines.append(line)
        else:
            empty_count = 0
            lines.append(line)
    return "\n".join(lines).strip()


def choose_topic() -> str:
    print("\nChoose a topic for hashtag suggestions:")
    for i, topic in enumerate(TOPICS, 1):
        print(f"  {i}. {topic}")
    print()
    while True:
        try:
            choice = input(f"Topic (1-{len(TOPICS)}) [default: {len(TOPICS)}]: ").strip()
            if not choice:
                return "default"
            idx = int(choice) - 1
            if 0 <= idx < len(TOPICS):
                return TOPICS[idx]
        except (ValueError, EOFError):
            pass
        print(f"  Please enter a number 1-{len(TOPICS)}")


def print_report(title: str, report):
    print(f"\n{title}")
    print("-" * 40)
    print(report.summary())


def print_optimized(result: dict):
    print(f"\n{SEPARATOR}")
    print("  ORIGINAL TEXT")
    print(SEPARATOR)
    print(result["original"])

    print_report("ANALYSIS (Before)", result["before_report"])

    print(f"\n{SEPARATOR}")
    print("  OPTIMIZED TEXT")
    print(SEPARATOR)
    print(result["optimized"])

    print_report("ANALYSIS (After)", result["after_report"])

    delta = result["after_report"].score - result["before_report"].score
    sign = "+" if delta > 0 else ""
    print(f"\n  Score change: {result['before_report'].score} -> {result['after_report'].score} ({sign}{delta})")
    print()


def run_interactive():
    print_header()
    text = read_input_interactive()
    if not text:
        print("No text provided. Exiting.")
        return

    topic = choose_topic()

    analyzer = TextAnalyzer()
    transformer = TextTransformer()

    report = analyzer.analyze(text)
    print_report("INITIAL ANALYSIS", report)

    result = transformer.optimize(text, topic=topic)
    print_optimized(result)


def run_from_args(args):
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read().strip()
    elif args.text:
        text = args.text
    else:
        text = read_input_interactive()

    if not text:
        print("No text provided. Exiting.")
        sys.exit(1)

    analyzer = TextAnalyzer()
    transformer = TextTransformer()

    if args.analyze_only:
        print_header()
        report = analyzer.analyze(text)
        print_report("ANALYSIS", report)
    else:
        result = transformer.optimize(text, topic=args.topic)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result["optimized"])
            print(f"Optimized text written to {args.output}")
        else:
            print_header()
            print_optimized(result)


def main():
    parser = argparse.ArgumentParser(
        description="TextTok — optimize text for TikTok while preserving meaning"
    )
    parser.add_argument(
        "--file", "-f",
        help="Path to input text file",
    )
    parser.add_argument(
        "--text", "-t",
        help="Text string to optimize",
    )
    parser.add_argument(
        "--topic",
        choices=TOPICS,
        default="default",
        help="Topic for hashtag suggestions (default: default)",
    )
    parser.add_argument(
        "--analyze-only", "-a",
        action="store_true",
        help="Only analyze text, don't optimize",
    )
    parser.add_argument(
        "--output", "-o",
        help="Write optimized text to file",
    )

    args = parser.parse_args()

    if args.file or args.text or args.analyze_only:
        run_from_args(args)
    elif len(sys.argv) == 1:
        run_interactive()
    else:
        run_from_args(args)


if __name__ == "__main__":
    main()

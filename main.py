#!/usr/bin/env python3
"""TextTok — TikTok text optimizer and UGC voiceover generator CLI.

Usage:
    python main.py                                          # interactive optimizer
    python main.py optimize --text "your text" --topic life # optimize text
    python main.py optimize --file input.txt                # optimize from file
    python main.py optimize --text "text" --analyze-only    # analyze only
    python main.py generate snell --count 5                 # generate 5 Snell voiceover texts
    python main.py generate tube --count 3 --style short    # generate 3 short Tube texts
    python main.py generate --list                          # list available templates
"""

import argparse
import sys

from optimizer import TextAnalyzer, TextTransformer, UGCGenerator


TOPICS = [
    "education", "motivation", "life", "tech",
    "business", "health", "food", "travel", "default",
]

SEPARATOR = "=" * 60


def print_header():
    print(SEPARATOR)
    print("  TextTok — TikTok Text Optimizer & UGC Generator")
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


# ── Optimize commands ──────────────────────────

def run_optimize_interactive():
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


def run_optimize(args):
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


# ── Generate commands ──────────────────────────

def run_generate(args):
    generator = UGCGenerator()

    if args.list:
        print_header()
        print("Available templates:\n")
        for t in generator.list_templates():
            print(f"  {t['id']:10s}  {t['name']:10s}  ({t['type']}) — {t['description']}")
        print()
        return

    if not args.template:
        print("Error: specify a template name (snell / tube) or use --list")
        sys.exit(1)

    print_header()
    print(f"Generating {args.count} voiceover text(s) for '{args.template}' "
          f"(style: {args.style})...\n")

    results = generator.generate(
        template_id=args.template,
        count=args.count,
        style=args.style,
        add_hashtags=not args.no_hashtags,
        add_emojis=not args.no_emojis,
    )

    output_lines = []

    for i, item in enumerate(results, 1):
        header = f"── Voiceover #{i} ({item['style']}) "
        print(header + "─" * (60 - len(header)))
        print()
        print(item["text"])
        print()

        if item["warnings"]:
            print("  WARNINGS:")
            for w in item["warnings"]:
                print(f"    ! {w}")
            print()

        output_lines.append(item["text"])

    print(f"{'─' * 60}")
    print(f"  Generated {len(results)} voiceover text(s) for '{args.template}'")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n\n---\n\n".join(output_lines))
        print(f"  Written to {args.output}")

    print()


# ── Main ───────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="TextTok — TikTok text optimizer & UGC voiceover generator"
    )
    subparsers = parser.add_subparsers(dest="command")

    # optimize subcommand
    opt_parser = subparsers.add_parser("optimize", help="Optimize existing text for TikTok")
    opt_parser.add_argument("--file", "-f", help="Path to input text file")
    opt_parser.add_argument("--text", "-t", help="Text string to optimize")
    opt_parser.add_argument("--topic", choices=TOPICS, default="default",
                            help="Topic for hashtag suggestions")
    opt_parser.add_argument("--analyze-only", "-a", action="store_true",
                            help="Only analyze, don't optimize")
    opt_parser.add_argument("--output", "-o", help="Write optimized text to file")

    # generate subcommand
    gen_parser = subparsers.add_parser("generate", help="Generate voiceover text for TikTok videos")
    gen_parser.add_argument("template", nargs="?", help="Template name: snell, tube")
    gen_parser.add_argument("--count", "-n", type=int, default=1,
                            help="Number of texts to generate (default: 1)")
    gen_parser.add_argument("--style", "-s", choices=["full", "short", "caption"],
                            default="full",
                            help="Style: full (all sections), short (hook+action+CTA), caption (single paragraph)")
    gen_parser.add_argument("--no-hashtags", action="store_true",
                            help="Don't add hashtags")
    gen_parser.add_argument("--no-emojis", action="store_true",
                            help="Don't add emojis")
    gen_parser.add_argument("--output", "-o", help="Write generated texts to file")
    gen_parser.add_argument("--list", "-l", action="store_true",
                            help="List available templates")

    args = parser.parse_args()

    if args.command == "optimize":
        run_optimize(args)
    elif args.command == "generate":
        run_generate(args)
    elif len(sys.argv) == 1:
        run_optimize_interactive()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

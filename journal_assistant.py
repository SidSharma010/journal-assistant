#!/usr/bin/env python3
"""
Journal Assistant
------------------
A small CLI tool that uses the Claude API to turn a rough note into a
clean, tagged journal entry, and appends it to a running journal file.

Usage:
    python journal_assistant.py "your rough note text here"
    python journal_assistant.py --file path/to/note.txt
    echo "your note" | python journal_assistant.py

Setup:
    1. pip install -r requirements.txt
    2. cp .env.example .env   and add your ANTHROPIC_API_KEY
"""

import argparse
import datetime
import json
import os
import sys

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

JOURNAL_FILE = "journal.md"
MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """You are a journaling assistant. Given a rough, unedited note, \
you will:
1. Clean it up into 2-4 well-written sentences, keeping the author's voice and \
   meaning intact. Do not invent details that are not in the note.
2. Suggest 1-4 short lowercase tags (single words or short phrases) that \
   capture the themes.
3. Write a one-line summary (under 12 words).

Respond ONLY with valid JSON in this exact shape:
{"cleaned": "...", "tags": ["...", "..."], "summary": "..."}
"""


def get_client() -> Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit(
            "Error: ANTHROPIC_API_KEY is not set. Copy .env.example to .env "
            "and add your key, or export it in your shell."
        )
    return Anthropic(api_key=api_key)


def process_note(client: Anthropic, raw_note: str) -> dict:
    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": raw_note}],
    )
    text = response.content[0].text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        sys.exit(f"Error: could not parse Claude's response as JSON:\n{text}")


def append_entry(raw_note: str, result: dict) -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    tags = " ".join(f"#{t}" for t in result.get("tags", []))

    entry = (
        f"\n## {timestamp}\n\n"
        f"**Summary:** {result.get('summary', '')}\n\n"
        f"{result.get('cleaned', raw_note)}\n\n"
        f"*Tags: {tags}*\n\n"
        f"<details><summary>Original note</summary>\n\n{raw_note}\n\n</details>\n"
        f"\n---\n"
    )

    is_new = not os.path.exists(JOURNAL_FILE)
    with open(JOURNAL_FILE, "a", encoding="utf-8") as f:
        if is_new:
            f.write("# Journal\n")
        f.write(entry)


def get_input_text(args: argparse.Namespace) -> str:
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            return f.read().strip()
    if args.note:
        return " ".join(args.note).strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    sys.exit("Error: no note provided. Pass text as an argument, use --file, or pipe input.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Turn a rough note into a clean, tagged journal entry using Claude."
    )
    parser.add_argument("note", nargs="*", help="The rough note text.")
    parser.add_argument("--file", "-f", help="Read the note from a text file instead.")
    args = parser.parse_args()

    raw_note = get_input_text(args)
    client = get_client()

    print("Thinking...")
    result = process_note(client, raw_note)
    append_entry(raw_note, result)

    print(f"\nSummary: {result.get('summary', '')}")
    print(f"Tags: {', '.join(result.get('tags', []))}")
    print(f"\nSaved to {JOURNAL_FILE}")


if __name__ == "__main__":
    main()

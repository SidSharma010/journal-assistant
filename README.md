# journal-assistant

A small CLI tool that uses the Claude API to turn a rough, unedited note into a
clean, tagged journal entry — and appends it to a running `journal.md` file.

## Why

I journal in short, messy bursts. This tool takes that raw text, asks Claude to
clean it up (without inventing details), tag it, and summarize it in one line,
then saves a nicely formatted entry with the original note kept alongside it.

## Setup

```bash
git clone https://github.com/SidSharma010/journal-assistant.git
cd journal-assistant
pip install -r requirements.txt
cp .env.example .env
```

Add your Anthropic API key to `.env`:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Get a key at [console.anthropic.com](https://console.anthropic.com/settings/keys).

## Usage

```bash
# Pass the note directly
python journal_assistant.py "rough draft of what happened today, in my own words"

# Or read it from a file
python journal_assistant.py --file note.txt

# Or pipe it in
echo "today was a mess but I fixed the thing" | python journal_assistant.py
```

Each run appends a new entry to `journal.md`:

```
## 2026-09-20 22:10

**Summary:** Fixed a stuck lock entry after a long debugging session.

Today was rough — spent an hour chasing a stuck lock entry before realizing
the background job behind it had died mid-update. Once I confirmed that in
SM37, releasing it in SM12 was the easy part.

*Tags: #debugging #sap #wins*

<details><summary>Original note</summary>

spent forever on that stuck lock thing turned out the job died mid update lol

</details>

---
```

`journal.md` is gitignored by default, since journal content is personal —
delete that line from `.gitignore` if you want to version it yourself.

## How it works

- `journal_assistant.py` sends your raw note to Claude with a system prompt
  that asks for cleaned text, tags, and a summary, returned as JSON.
- The response is parsed and appended to `journal.md` as a new dated section.
- No note is ever silently dropped: if the API call or JSON parsing fails,
  the script exits with an error instead of guessing.

## Ideas for next steps

- [ ] Add a `--search` flag to grep past entries by tag
- [ ] Weekly summary mode that reads the whole journal and highlights themes
- [ ] Optional voice-to-text input

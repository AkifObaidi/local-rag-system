from pathlib import Path
import re
import json
import tiktoken


DATA_FILE = Path("data/demo_data.md")
OUTPUT_FILE = Path("processed/chunks.json")

MAX_TOKENS = 2000

TOKENIZER = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(TOKENIZER.encode(text))


def split_large_section(text: str, max_tokens: int) -> list[str]:
    paragraphs = re.split(r"\n\s*\n", text.strip())

    chunks = []
    current = []

    for paragraph in paragraphs:
        paragraph_tokens = count_tokens(paragraph)
        current_text = "\n\n".join(current)

        if (
            current
            and count_tokens(current_text + "\n\n" + paragraph) > max_tokens
        ):
            chunks.append(current_text)
            current = []

        if paragraph_tokens > max_tokens:
            lines = paragraph.splitlines()

            for line in lines:
                if not line.strip():
                    continue

                current_text = "\n".join(current)

                if (
                    current
                    and count_tokens(current_text + "\n" + line) > max_tokens
                ):
                    chunks.append(current_text)
                    current = []

                current.append(line)

        else:
            current.append(paragraph)

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def parse_sections(markdown: str) -> list[dict]:
    pattern = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)

    matches = list(pattern.finditer(markdown))
    sections = []

    for index, match in enumerate(matches):
        title = match.group(1).strip()

        start = match.end()

        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(markdown)
        )

        content = markdown[start:end].strip()

        sections.append(
            {
                "title": title,
                "content": content,
            }
        )

    return sections


def create_chunks(sections: list[dict]) -> list[dict]:
    chunks = []

    for section in sections:
        title = section["title"]
        content = section["content"]

        full_text = f"## {title}\n\n{content}"
        token_count = count_tokens(full_text)

        if token_count <= MAX_TOKENS:
            chunks.append(
                {
                    "id": f"chunk_{len(chunks):04d}",
                    "text": full_text,
                    "section": title,
                    "chunk_index": 0,
                    "token_count": token_count,
                }
            )

        else:
            smaller_chunks = split_large_section(
                content,
                MAX_TOKENS - count_tokens(f"## {title}\n\n"),
            )

            for chunk_index, smaller_chunk in enumerate(smaller_chunks):
                text = f"## {title}\n\n{smaller_chunk}"

                chunks.append(
                    {
                        "id": f"chunk_{len(chunks):04d}",
                        "text": text,
                        "section": title,
                        "chunk_index": chunk_index,
                        "token_count": count_tokens(text),
                    }
                )

    return chunks


def main():
    # Read original Markdown
    markdown = DATA_FILE.read_text(encoding="utf-8")

    # Parse sections
    sections = parse_sections(markdown)

    # Create final chunks
    chunks = create_chunks(sections)

    # Create output directory if it doesn't exist
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Save chunks as JSON
    OUTPUT_FILE.write_text(
        json.dumps(chunks, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Sections found: {len(sections)}")
    print(f"Final chunks:   {len(chunks)}")
    print(f"Saved to:       {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

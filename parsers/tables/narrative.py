import re


def parse(table):
    paragraphs = []

    # Narrative starts after title row. Keep paragraph boundaries when present.
    for row in table[1:]:
        if not row:
            continue

        cell_chunks = []
        for cell in row:
            text = str(cell or "").strip()
            if text:
                cell_chunks.append(text)

        if not cell_chunks:
            continue

        paragraph = " ".join(cell_chunks)
        paragraph = re.sub(r"[ \t]+", " ", paragraph).strip()
        if paragraph:
            paragraphs.append(paragraph)

    return {"Narrative": "\n\n".join(paragraphs)}

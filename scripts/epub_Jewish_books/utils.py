import re
from hebrew_numbers import int_to_gematria
import json
import subprocess
from bs4 import BeautifulSoup


def recursive_register_categories(
    index: list | dict,
    data: list[dict[str, str | list[str]]] | None = None,
    tree: list[str] | None = None,
) -> list[dict[str, str | list[str]]]:
    if tree is None:
        tree = []
    if data is None:
        data = []
    if isinstance(index, list):
        for item in index:
            recursive_register_categories(item, data, tree)
    elif isinstance(index, dict):
        if index.get("contents"):
            tree.append(index["heCategory"])
            for item in index["contents"]:
                recursive_register_categories(item, data, tree)
            tree.pop()
        if index.get("title"):
            data.append(
                {
                    "he_title": index["heTitle"],
                    "en_title": index["title"],
                    "path": tree.copy(),
                }
            )
    return data


def sanitize_filename(filename: str) -> str:
    sanitized_filename = re.sub(r'[\\/:*"?<>|]', "", filename)
    sanitized_filename = sanitized_filename.replace("_", " ")
    return sanitized_filename.strip()


def to_daf(i: int) -> str:
    i += 1
    if i % 2 == 0:
        return to_gematria(i//2)+'.'
    else:
        return to_gematria(i//2)+':'


def to_gematria(i: int) -> str:
    s = ''
    i = i % 1000
    j = i / 1000
    if j < 0:
        s = int_to_gematria(j, gershayim=False) + ' '
    s = s + int_to_gematria(i, gershayim=False)
    return s


def to_eng_daf(i) -> str:
    i += 1
    if i % 2 == 0:
        return str(i//2)+'a'
    else:
        return str(i//2)+'b'


def has_value(data: list):
    return any(has_value(item) if isinstance(item, list) else item for item in data)


def read_json(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        content = json.load(f)
    return content


def to_ebook(
    input_file: str,
    output_file: str,
    dict_args: dict[str, str],
    level1_toc: str = "//h:h1",
    level2_toc: str = "//h:h2",
    level3_toc: str = "//h:h3",
):
    args = [
        "ebook-convert",
        input_file,
        output_file,
        f"--level1-toc={level1_toc}",
        f"--level2-toc={level2_toc}",
        f"--level3-toc={level3_toc}",
    ]
    for key, value in dict_args.items():
        args.append(f"--{key}={value}")
    subprocess.run(
        args,
        stdout=subprocess.DEVNULL,  # משתיק את הפלט
        stderr=subprocess.DEVNULL,  # משתיק את השגיאות
        check=True,
    )


def footnotes_to_epub(html_content: str) -> str:
    soup = BeautifulSoup(html_content, 'html.parser')
    notes = []
    for sup_tag in soup.find_all('sup', class_='footnote-marker'):
        next_tag = sup_tag.find_next_sibling() 
        if next_tag and next_tag.name == 'i' and 'footnote' in next_tag.get('class', []):
            note_id = f"note_{len(notes) + 1}"
            back_note_id = f"back_note_{len(notes) + 1}"
            sup_a = soup.new_tag("a", id=back_note_id, href=f"#{note_id}", title=sup_tag.text, class_="noteref", role="doc-noteref")
            sup_a.string = sup_tag.text
            sup_tag.string = "" 
            sup_tag.append(sup_a)
            note_a = soup.new_tag("a", href=f"#{back_note_id}", title=sup_tag.text)
            note_a.string = f"←{sup_tag.text}"
            note_span = soup.new_tag("span", id=note_id)
            note_span.string = next_tag.text
            note_p = soup.new_tag("p")
            note_p.append(note_a)
            note_p.append(note_span)
            notes.append(note_p)
            next_tag.extract()

    if notes:
        h1 = soup.new_tag("h1")
        h1.string = "הערות שוליים"
    body_tag = soup.body
    if body_tag:
        body_tag.append(h1)
        for note in notes:
            body_tag.append(note)

    return str(soup)


def heading_order(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    for i in range(5, 1, -1):
        has_h = soup.find(f'h{i}') is not None
        if not has_h:
            for heading in soup.find_all(re.compile(f'^h[{i + 1}-6]$')):
                current_level = int(heading.name[1])
                new_level = current_level - 1
                heading.name = f'h{new_level}'
    prev_heading = 0
    original_prev_heading = 0
    for heading in soup.find_all(re.compile('^h[1-6]$')):
        heading_level = int(heading.name[1])
        if heading_level == original_prev_heading:
            heading.name = f"h{prev_heading}"
        elif heading_level > prev_heading and heading_level - prev_heading > 1:
            heading.name = f"h{prev_heading + 1}"
        original_prev_heading = heading_level
        prev_heading = int(heading.name[1])
    return str(soup)

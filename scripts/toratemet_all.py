import os
import json

from epub_Jewish_books.utils import sanitize_filename, to_ebook, heading_order


def process_html_file(input_file: str) -> tuple[str, dict] | None:
    replace_dict = {
        "[[": "<b>",
        "]]": "</b>",
        "{{{": "<u><b>",
        "}}}": "</b></u>",
        "(((": '<b style="color:RGB(127,127,127); font-size:25px;">',
        ")))": "</b>"
    }

    with open(input_file, 'rb') as f:
        html_content = f.read()
    html_content = html_content.decode("windows-1255", errors="ignore")

    for key, value in replace_dict.items():
        html_content = html_content.replace(key, value)
    processed_lines = []
    metadata = {"language": "he"}
    lines = html_content.splitlines()
    TextSource = lines[0].split("&")
    metadata["publisher"] = "תורת אמת"
    for i in TextSource:
        if "TextSource" in i:
            text_source = i.replace("TextSource=", "")
            if text_source != "." and text_source != "":
                metadata["publisher"] = text_source
        elif "SpecialTitle" in i:
            text_source = i.replace("SpecialTitle=", "")
            if text_source != "." and text_source != "":
                metadata["publisher"] = "ויקיטקסט"
    for line in lines[1:]:
        if line.endswith('pages'):
            continue
        if "**INDEX_WRITE=" in line:
            continue
        mapping = {"#": 1, "^": 1, "@": 2, "~": 3, "!": 4}
        if not line:
            continue
        if line[0] in mapping:
            level = mapping[line[0]]
            processed_lines.append(f'<h{level}>{line[2:]}</h{level}>')
        elif line.startswith("$"):
            if len(line) >= 2:
                book_title = line[2:]
                metadata["title"] = book_title
        elif line.strip():
            processed_lines.append(f'<p>{line}</p>')
    processed_lines_2 = []
    for index, line in enumerate(processed_lines, start=1):
        try:
            next_line = processed_lines[index]
            if line.startswith('<h') and next_line.startswith('<h') and line[:15] == next_line[:15]:
                continue
            else:
                processed_lines_2.append(line)
        except IndexError:
            processed_lines_2.append(line)
    processed_html = f'<html><head><title>{book_title}</title></head><body dir="rtl">{"\n".join(processed_lines_2)}</body></html>'
    return processed_html, metadata


def book(file_path: str, target_path: str, tags: list | None = None) -> None:
    html_func = process_html_file(file_path)
    if html_func:
        html_content, metadata = html_func
        os.makedirs(target_path, exist_ok=True)
        title = metadata.get("title") or os.path.splitext(os.path.split(file_path)[1])[0]
        target_file_path = os.path.join(target_path, sanitize_filename(title))
        if tags:
            metadata["tags"] = ",".join(tags)
        html_path = f"{target_file_path}.html"
        epub_file = f"{target_file_path}.epub"
        html_content = heading_order(html_content)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        to_ebook(html_path, epub_file, metadata)
        os.remove(html_path)


def main(root_folder: str, target_folder: str, he_folder_names_file: str) -> None:
    skip_files = ("interleave", "merged", "debugmix")
    with open(he_folder_names_file, "r", encoding="utf-8") as f:
        he_folder_names = json.load(f)
    for root, _, files in os.walk(root_folder):
        for file in files:
            if any(map(lambda x: x in file.lower(), skip_files)):
                continue
            if not file.lower().endswith(".txt"):
                continue
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, root_folder)
            tags = [he_folder_names.get(i.split("_")[1]) for i in rel_path.split(os.sep)[:-1] if he_folder_names.get(i.split("_")[1])]
            target_path = os.path.join(target_folder, *[sanitize_filename(i) for i in tags])
            book(file_path, target_path, tags)


if __name__ == "__main__":
    folder_path = "/media/zevi5/387E388E7E384742/Users/משתמש/Documents/ToratEmetInstall/Books/"
    target_folder = "תורת אמת"
    he_folder_names_file = "folder_he_names.json"
    main(folder_path, target_folder, he_folder_names_file)

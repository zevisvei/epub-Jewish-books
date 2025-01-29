import os
from epub_Jewish_books.utils import sanitize_filename, to_ebook


def add_tags(line: str):
    if not line.strip().endswith(">") or not line.strip().startswith("<"):
        line = f"<p>{line.strip()}</p>"
    return line


def book(file_path: str, tags: list, target_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().split("\n")
    book_title = content[0].replace("<h1>", "").replace("</h1>", "").strip()
    author = content[1]
    book_body = "\n".join([add_tags(line) for line in content[2:]])
    for num in range(2, 7):
        book_body = book_body.replace(f"<h{num}>", f"<h{num - 1}>").replace(f"</h{num}>", f"</h{num - 1}>")
    book_body = f'<html lang=he><head><title>{book_title}</title></head><body dir="rtl">{book_body}</body></html>'
    meta_data = {"authors": author, "title": book_title, "language": "he", "publisher": "otzaria", "tags": ",".join(tags)}
    target_file_folder = os.path.join(target_path, *tags)
    os.makedirs(target_file_folder, exist_ok=True)
    target_file_path = os.path.join(target_file_folder, sanitize_filename(book_title))
    epub_path = f"{target_file_path}.epub"
    html_path = f"{target_file_path}.epub"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(book_body)
    epub_path = f"{os.path.splitext(file_path)[0]}.epub"
    to_ebook(html_path, epub_path, meta_data)
    os.remove(html_path)


def main(root_folder: str, target_path: str):
    for root, _, files in os.walk(root_folder):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, root_folder)
            tags = rel_path.split(os.sep)
            book(file_path, tags, target_path)


if __name__ == "__main__":
    root_folder = ""
    target_path = ""
    main(root_folder, target_path)

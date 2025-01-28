from bs4 import BeautifulSoup
import os
import zipfile
import re
import html as html_module

from epub_Jewish_books.utils import heading_order, sanitize_filename, to_ebook


def main(books_dir, target_dir):
    for root, _, files in os.walk(books_dir):
        for file_name in files:
            if not file_name.lower().endswith(".obk"):
                continue
            title = None
            file_path = os.path.join(root, file_name)
            content = read_zip(file_path)
            archive_comment = get_comment(file_path)
            metadata = {"language": "he"}
            if archive_comment:
                archive_comment = archive_comment.splitlines()
                dict_comment = {}
                for line in archive_comment:
                    try:
                        name_key, name_value = line.split("=")
                        dict_comment[name_key.strip()] = name_value.strip()
                    except ValueError:
                        continue
                title = dict_comment.get("DisplayName")
                if not title:
                    title = dict_comment.get("ForcedBookName")
                if dict_comment.get("RavMechaber"):
                    metadata["authors"] = dict_comment["RavMechaber"]
                metadata["publisher"] = dict_comment.get("TextSource") or "oryta"

            content = read_zip(file_path)
            if not content:
                continue
            content = re.sub(r"<!--[^א-ת]+?-->", "", content)
            content = content.splitlines()
            fix_content, title_from_file = proses_file(content)
            fix_spaces = fix_content.splitlines()
            output_text = [line.strip() for line in fix_spaces if line.strip()]
            join_lines = html_module.unescape("\n".join(output_text))
            join_lines = heading_order(join_lines)
            target_dir_heb, tags = get_path(file_path, books_dir, target_dir)
            if tags:
                metadata["tags"] = ",".join(tags)
            os.makedirs(target_dir_heb, exist_ok=True)
            if not title:
                title = title_from_file
            metadata["title"] = title
            title = sanitize_filename(title)
            target_file_path = os.path.join(target_dir_heb, f"{title}")
            num = 1
            while os.path.exists(target_file_path):
                num += 1
                target_file_path = os.path.join(target_dir_heb, f"{title}_{num}")
            html_file = f"{target_file_path}.html"
            epub_file = f"{target_file_path}.epub"
            processed_html = f'<html><head><title>{title}</title></head><body dir="rtl">{join_lines}</body></html>'
            with open(html_file, "w", encoding="utf-8") as output:
                output.write(processed_html)
            to_ebook(html_file, epub_file, metadata)
            os.remove(html_file)


def read_zip(file_path):
    with zipfile.ZipFile(file_path, 'r') as archive:
        content = archive.read("BookText")
    try:
        content = content.decode()
    except UnicodeDecodeError:
        try:
            content = content.decode(encoding='windows-1255')
        except UnicodeDecodeError:
            return False
    return content


def get_comment(file_path):
    with zipfile.ZipFile(file_path, 'r') as archive:
        archive_comment = archive.comment
    try:
        archive_comment = archive_comment.decode('utf-8')
    except UnicodeDecodeError:
        try:
            archive_comment = archive_comment.decode('windows-1255')
        except UnicodeDecodeError:
            return False

    return archive_comment


def get_path(file_path, books_dir, target_dir):
    rel_path = os.path.relpath(file_path, books_dir)
    split_path = rel_path.split(os.sep)
    path_now = books_dir
    tags = []
    for i in split_path[:-1]:
        folder_name_file = os.path.join(path_now, f"{i}.folder")
        try:
            with open(folder_name_file, "r", encoding="utf-8") as folder_name:
                new_name_from_file = folder_name.read().split("=")[1].strip()
                tags.append(new_name_from_file)
                new_name_from_file = sanitize_filename(new_name_from_file)
        except FileNotFoundError:
            new_name_from_file = i
            print(i)

        target_dir = os.path.join(target_dir, new_name_from_file)
        path_now = os.path.join(path_now, i)
    return target_dir, tags


def proses_file(text):
    mapping = {"#": 1, "^": 1, "@": 2, "~": 3, "!": 4}
    proses_file = []
    start = False
    title = None
    for line in text:
        if line.startswith("$") and not proses_file:
            line = line.strip("$").strip()
            title = line.strip()
            start = True
        elif start:
            if not line:
                continue
            if line[0] in mapping:
                level = mapping[line[0]]
                proses_file.append(f'<h{level}>{line[2:]}</h{level}>')
            elif line.startswith("**INDEX_WRITE"):
                continue
            elif line.strip():
                proses_file.append(f"<p>{line.strip()}</p>")

    join_lines = "\n".join(proses_file)

    soup = BeautifulSoup(join_lines, 'lxml')
    for tag in soup.find_all():
        if tag.name:
            if tag.name.lower() in ('html', "body", "amats", "iri", "nsobr", "qm", "r", "ra", "rb", "sp", "trim", "x", "y", "yesh"):
                tag.unwrap()
            elif tag.name.lower() == "center":
                tag.name = "span"
                if tag.attrs.get("style"):
                    tag.attrs["style"] += "text-align: center;"
                else:
                    tag.attrs["style"] = "text-align: center;"
            elif tag.name.lower() in ("div", "span"):
                tag_class = tag.attrs.get("class")
                if tag_class:
                    class_replace = ""
                    if tag_class == ["MsoNormal"]:
                        pass
                    elif tag_class == ["breadcrumbs"]:
                        pass
                    elif tag_class == ["pageno"]:
                        pass
                    elif tag_class == ["pirush"]:
                        class_replace += "color:#2828AC;"
                    elif tag_class == ["ref"]:
                        class_replace += "font-size:80%;"
                    elif tag_class == ["pasuk"]:
                        class_replace += "font-family: SBL Hebrew;"
                    elif tag_class == ["editor"]:
                        class_replace += "color:#008A00;"
                    elif tag_class == ["Aliyah"]:
                        class_replace += "font-size:80%;"
                    elif tag_class == ["S0"]:
                        class_replace += "font-size:95%;  font-weight:bold;"
                    elif tag_class == ["pasuk", "small"]:
                        class_replace += "font-size:70%; font-family: SBL Hebrew;"
                    if tag.attrs.get("style"):
                        tag.attrs["style"] += class_replace
                    elif class_replace:
                        tag.attrs["style"] = class_replace
                    del tag.attrs["class"]
    for tag in soup.find_all():
        if not tag.get_text(strip=True) and tag.name != "br":
            tag.decompose()

    return str(soup), title


books_dir = "/home/zevi5/Downloads/otzaria-library/OraytaToOtzaria/סקריפטים/books"
target_dir = os.path.join("..", "ספרים", "לא ממויין")
main(books_dir, target_dir)

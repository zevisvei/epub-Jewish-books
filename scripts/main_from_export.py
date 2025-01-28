from epub_Jewish_books.get_from_export import Book
from epub_Jewish_books.utils import sanitize_filename, to_ebook, footnotes_to_epub
import os


def get_book(book_title: str, text_file_path: str, schema_file_path: str, lang: str):
    book_ins = Book(book_title,
                    lang,
                    text_file_path,
                    schema_file_path)
    book_content = book_ins.process_book()
    metadata, categories = book_ins.get_metadata()
    return book_content, metadata, categories


def main(json_folder, schemas_folder, output_folder, lang: str):
    """
    Process all books in the given folder whose path ends with 'Hebrew/Merged.json'.
    It finds the corresponding schema file in the schemas folder by matching the
    pattern '/xxxx/Hebrew/Merged.json' to 'xxxx.json'.

    :param folder_path: Path to the folder containing the book files.
    :param schemas_folder: Path to the folder containing the schema files.
    """
    for root, _, files in os.walk(json_folder):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.lower().endswith(f'{lang}{os.sep}merged.json'):
                try:
                    text_file = file_path
                    print(text_file)
                    title = file_path.split(os.sep)[-3].replace(' ', '_')
                    schema_file_name = os.path.join(schemas_folder, title + '.json')
                    book_content, metadata, categories = get_book(title, text_file, schema_file_name, lang)
                    output_path = [sanitize_filename(i) for i in categories]
                    os.makedirs(os.path.join(output_folder, *output_path),exist_ok=True)
                    output_file_name = os.path.join(output_folder, *output_path, sanitize_filename(metadata["title"]))
                    print(output_file_name)
                    book_dir = ' dir="rtl"' if lang == "hebrew" else ""
                    book_content = f'<html lang={lang[:2]}><head><title></title></head><body{book_dir}>{"".join(book_content)}</body></html>'
                    if "footnote-marker" in book_content:
                        book_content = footnotes_to_epub(book_content)
                    with open(f'{output_file_name}.html', 'w', encoding='utf-8') as file:
                        file.write(book_content)
                    to_ebook(f"{output_file_name}.html", f"{output_file_name}.epub", metadata)
                    os.remove(f"{output_file_name}.html")
                except Exception as e:
                    with open("error.txt", "a", encoding="utf-8") as f:
                        f.write(f"{file_path} {e}\n")


json_folder = "json"
schemas_folder = "schemas"
output_folder = "output"
lang = "hebrew"
main(json_folder=json_folder, schemas_folder=schemas_folder,
     output_folder=output_folder, lang=lang)

from ebooklib import epub
import os
import re

def convert_in_folder(folder_path):
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.lower().endswith(".epub"):
                old_path = os.path.join(root, file_name)
                new_path = os.path.join(root, get_ebok_title(old_path)+".epub")
                os.rename(old_path, new_path)
                print(f"processed: {new_path}")
                
def sanitize_filename(filename):
    # Remove invalid characters
    sanitized_filename = re.sub(r'[\/:*?<>|]', '', filename)
    return sanitized_filename

                
def get_ebok_title(ebook):
    book = epub.read_epub(ebook)
    book_title = book.get_metadata('DC', 'title')
    book_title1 =(book_title[0])
    book_title2 = sanitize_filename(book_title1[0]).replace('"', "''")
    return (book_title2)
    

folder_path = r'kindle-seforim'

convert_in_folder(folder_path)

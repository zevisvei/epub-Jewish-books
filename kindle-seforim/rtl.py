import os
import zipfile

def edit_in_folder(folder_path):
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith('.epub'):
                file_path = os.path.join(root, file_name)
                edit_epub_spine(file_path)

def edit_epub_spine(srcfile):
    a = b'<spine toc="ncx">'
    b = b'<spine toc="ncx" page-progression-direction="rtl">'
    c = b'<spine>'
    temp_file = srcfile + "_temp"
    with zipfile.ZipFile(srcfile, "r") as inzip, zipfile.ZipFile(temp_file, "w") as outzip:
        for inzipinfo in inzip.infolist():
            with inzip.open(inzipinfo) as infile:
                if inzipinfo.filename == "content.opf":
                    content = infile.read().replace(a, b).replace(c, b)
                    outzip.writestr(inzipinfo.filename, content)
                else:
                    outzip.writestr(inzipinfo.filename, infile.read())
    
    os.remove(srcfile)
    os.rename(temp_file, srcfile)
    print(f"processed: {srcfile}")

folder_path = r'kindle-seforim'
edit_in_folder(folder_path)

import os
import shutil
import re
import zipfile


def sanitize_filename(filename):
    # Remove invalid characters
    sanitized_filename = re.sub(r'[\/:*?<>|]', '', filename)
    return sanitized_filename


def edit_in_folder(folder_path, autpoot_dir):
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith('.epub'):
                file_path = os.path.join(root, file_name)
                move_to_folder(file_path, autpoot_dir, file_name)
                
def move_to_folder(file_path, autpoot_dir, file_name):
    root = []
    with zipfile.ZipFile(file_path, "r") as inzip:
        for inzipinfo in inzip.infolist():
                with inzip.open(inzipinfo) as infile:
                    if inzipinfo.filename == "content.opf":
                        content = infile.read().decode("utf-8").splitlines()
                        for line in content:
                            if "<dc:subject" in line:
                                root.append(line.replace("  ","").replace("<dc:subject>","").replace("</dc:subject>","").replace(",","\\"))
                            if "<dc:title" in line:
                                title = sanitize_filename(line.replace("  ","").replace("<dc:title>","").replace("</dc:title>","")).replace('"', "''")
    root_2 = "\\".join(root)
    os.makedirs(os.path.join(autpoot_dir, root_2),exist_ok=True)
    file_name = os.path.join(autpoot_dir, root_2,title +".epub")
    count = 1
    while os.path.exists(file_name):
        file_name = f"{file_name[:-5]}_{count}.epub"
        count += 1
    shutil.move(file_path, file_name)

folder_path = r".\dddd"
autpoot_dir = r".\aaaaaa"

edit_in_folder(folder_path, autpoot_dir)       
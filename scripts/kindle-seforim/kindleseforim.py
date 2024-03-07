import os
import zipfile

def edit_in_folder(folder_path):
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith('.epub'):
                file_path = os.path.join(root, file_name)
                print(file_path)
                edit_epub_spine(file_path)

def edit_epub_spine(srcfile):
    temp_file = srcfile+"_temp"
    with zipfile.ZipFile(srcfile, "r") as inzip, zipfile.ZipFile(temp_file, "w") as outzip:
        for inzipinfo in inzip.infolist():
            with inzip.open(inzipinfo) as infile:
                if inzipinfo.filename == "content.opf":
                    content = infile.read()
                    content_2 = content.decode("utf-8").splitlines()
                    content_3 = []
                    line = -1
                    subject = False
                    publisher = False
                    tages = srcfile.split("\\")
                    tages_2 = tages[2:-1]                    
                    bbbb =f'    <dc:subject>{",".join(tages_2).replace("  ","")}</dc:subject>'
                    ccc = f'<dc:publisher>kindle seforim</dc:publisher>'
                    for i in content_2:
                        if "<dc:subject" in i:
                            content_3.append(bbbb)
                            subject = True
                            line+=1
                        elif "<dc:publisher" in i:
                            content_3.append(ccc)
                            publisher = True
                            line+=1
                        else:
                            try:
                                if "</metadata>" in content_2[line+1]:
                                    if not subject:
                                        content_3.append(bbbb)
                                    if not publisher:
                                        content_3.append(ccc)
                                    line+=1
                                else:
                                    content_3.append(i)
                                    line+=1
                            except IndexError:
                                content_3.append(i)
                    content_4 = "\n".join(content_3)
                    outzip.writestr(inzipinfo.filename, bytes(content_4, encoding="utf-8"))
                else:
                    outzip.writestr(inzipinfo.filename, infile.read())
    os.remove(srcfile)
    os.rename(temp_file, srcfile)
    
    print(f"processed: {srcfile}")

folder_path = r'.\kindleseforim'
edit_in_folder(folder_path)


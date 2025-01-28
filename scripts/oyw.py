import os
import xml.etree.ElementTree as ET
import re
import html as html_module

from bs4 import BeautifulSoup

from epub_Jewish_books.utils import sanitize_filename, heading_order, to_ebook


def process_node(node, book_folder: str, base_folder: list | None = None):
    node_name = node.get("name")
    if base_folder is None:
        base_folder = []
    if "ובלכתך בדרך" in base_folder:
        base_folder.remove("ובלכתך בדרך")
    if "nid" in node.attrib:
        nid = node.get("nid")
        old_filename = os.path.join(book_folder, nid + ".xml")
        if os.path.exists(old_filename):
            book(old_filename, base_folder, node_name)
        else:
            print(nid)
    if node.findall("node"):
        base_folder.append(node_name)
        for child_node in node.findall("node"):
            process_node(child_node, book_folder, base_folder)
        base_folder.pop()


def check_line(line):
    return re.search(r"[a-zA-Zא-ת0-9]+", line)


def process_body_xml(xml_content):
    h_dict = {"book": 0, "chap": 1, "p": 2}
    t_dict = {
        1: "אונקלוס", 2: 'תרגום ירושלמי', 3: 'רש"י', 4: 'רמב"ן', 5: 'אבן עזרא', 6: 'ספורנו', 7: 'בעל הטורים',
        8: 'אור החיים', 9: 'תורה תמימה', 10: 'מצודת דוד', 11: 'מצודת ציון', 12: 'רלב"ג', 14: 'רע"ב', 15: 'תוי"ט', 17: 'רש"י',
        18: 'תוס', 20: 'משנ"ב', 21: 'ביאור הלכה', 23: 'תרגום זוהר', 28: 'כלי יקר ', 29: 'מלבי"ם תוכן',
        30: 'מלבי"ם פירוש המילות', 31: 'מלבי"ם ביאור המילות'
    }
    title = None
    carector_list = ['<?xml version="1.0" ?>', "<![CDATA[", "]]>", '<?xml version="1.0" encoding="utf-8"?>']
    for i in carector_list:
        xml_content = xml_content.replace(i, " ")
    xml_content = re.sub(r"<!--[^א-ת]+?-->", "", xml_content)
    xml_content = re.sub(r"<\?xml.+?\?>", "", xml_content)
    soup = BeautifulSoup(xml_content, "lxml")
    for tag in soup.find_all():
        if tag.name:
            if tag.name.lower() in ('html', "body", "d", "iri", "pid", "qm", "rb", "sp", "tf", "col3", "f"):
                tag.unwrap()
            elif tag.name.lower() in ("center", "sid1", "sid2", "sid3", "sid4", "sidcom1", "sidcom2", "sidcom4", "tos", "e", "c", "m", "bl"):
                tag_replace = ""
                if tag.name.lower() == "center":
                    tag_replace += "text-align: center;"
                elif tag.name.lower() in ("sid1"):
                    tag_replace += "font-size:95%; color:RGB(0,0,255); text-shadow:0 0px 0 white;"
                elif tag.name.lower() == "sid2":
                    tag_replace += "font-size:110%; font-weight:bold;text-shadow:0 0px 0 white;"
                elif tag.name.lower() == "sid3":
                    tag_replace += "font-weight:bold;text-shadow:0 0px 0 white;"
                elif tag.name.lower() == "sid4":
                    tag_replace += "color: green;"
                elif tag.name == "sidcom1":
                    tag_replace += "color:RGB(127,127,127); font-family: arial; font-size:80%;text-shadow:0 0px 0 white;"
                elif tag.name.lower() == "sidcom2":
                    tag_replace += "color:RGB(0,127,127); font-family: arial; font-size:85%;text-shadow:0 0px 0 white;"
                elif tag.name.lower() == "sidcom4":
                    tag_replace += "padding:10; margin:10;  background-color=RGB(244,244,244);text-shadow:0 0px 0 white;"
                elif tag.name.lower() == "tos":
                    tag_replace += "background-color: #AAAAAA;text-shadow:0 0px 0 white;"
                elif tag.name.lower() == "e":
                    tag_replace += "font-size:100%; display:inline;"
                elif tag.name.lower() == "c":
                    tag_replace += "font-weight:bold; visibility: visible; display:inline; font-size:100%;"
                elif tag.name.lower() == "bl":
                    tag_replace += "font-weight:bold; color:#0000FF; font-size:110%;"
                elif tag.name.lower() == "n":
                    tag_replace += "color:#888888; font-size:80%;"
                elif tag.name.lower() == "m":
                    tag_replace += "color:#444444; font-size:80%; display:none;"
                if tag.attrs.get("style"):
                    tag.attrs["style"] += tag_replace
                elif tag_replace:
                    tag.attrs["style"] = tag_replace
                tag.name = 'span'

            elif tag.name.lower() in ("script", "style", "pid", "a", "input", "ps"):
                tag.decompose()
            elif tag.name.lower() in ("book", "chap", "p"):
                name = tag.attrs.get("n")
                if name:
                    if h_dict.get(tag.name) == 0:
                        title = name.strip()
                    elif name.strip() not in ("-", ".", "_"):
                        tag.insert_before(f"\n<h{h_dict.get(tag.name)}>{name.strip()}</h{h_dict.get(tag.name)}>\n")
                tag.unwrap()
            elif tag.name.lower() == "t":
                name = tag.attrs.get("i").strip()
                if name:
                    name_2 = t_dict[int(name)]
                    new_tag = soup.new_tag("b")
                    new_tag.string = name_2
                    new_tag.attrs["style"] = "color: gray;"
                    tag.insert_before(new_tag)
                    tag.insert_before(" ")
                tag.unwrap()

            elif tag.name.lower() in ("span", "div"):
                tag_class = tag.attrs.get("class")
                if tag_class:
                    class_replace = ""
                    if tag_class == ["ot"]:
                        pass
                    elif tag_class == ["answer"]:
                        class_replace += "padding:3px;background-color:#CCCCCC;display:none;"
                    elif tag_class == ["tfilaq"]:
                        class_replace += "border-bottom: 2px dotted blue; margin: 20px 0;"
                    elif tag_class == ["bothq"]:
                        class_replace += "margin: 0;display: inline; border-bottom: 2px dashed #0000FF;"
                    elif tag_class == ["rashiq"]:
                        class_replace += "margin: 0;display: inline;border-bottom: 2px dashed #990000;"
                    elif tag_class == ["tosfotq"]:
                        class_replace += "margin: 0;display: inline;border-bottom: 2px dashed #006600;"
                    elif tag_class == ["fq"]:
                        class_replace += "margin: 0;display: inline;border-bottom: 2px dashed #0000FF;"
                    elif tag_class == ["al"]:
                        class_replace += "margin: 0;display: inline;color: #0000ff;"
                    if tag.attrs.get("style"):
                        tag.attrs["style"] += class_replace
                    elif class_replace:
                        tag.attrs["style"] = class_replace
                    del tag.attrs["class"]

    for tag in soup.find_all():
        if not tag.get_text(strip=True) and tag.name != "br":
            tag.decompose()

    return str(soup), title


def book(file_path: str, target_file: list, file_name: str, target_folder: str = "oyw"):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="windows-1255") as file:
            content = file.read()
    metadata = {"language": "he"}
    metadata["publisher"] = "ובלכתך בדרך"
    metadata["tags"] = ",".join(target_file)
    fix_xml, title = process_body_xml(content)
    metadata["title"] = title or file_name
    fix_spaces = fix_xml.splitlines()
    output_text = [line.strip() for line in fix_spaces if check_line(line)]
    join_lines = html_module.unescape("\n".join(output_text))
    if len(file_name) > 100:
        file_name = " ".join(file_name.split()[0:10])
    processed_html = f'<html><head><title>{title or file_name}</title></head><body dir="rtl">{join_lines}</body></html>'
    processed_html = heading_order(processed_html)
    target_file_path = os.path.join(target_folder, *[sanitize_filename(folder) for folder in target_file], sanitize_filename(file_name))
    os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
    epub_file = f"{target_file_path}.epub"
    html_file = f"{target_file_path}.html"
    with open(html_file, "w", encoding="utf-8") as output:
        output.write(processed_html)
    to_ebook(html_file, epub_file, metadata)
    os.remove(html_file)


xml_file = "/home/zevi5/Downloads/otzaria-library/OnYourWayToOtzaria/סקריפטים/שונות/xml/tnc.xml"
tree = ET.parse(xml_file)
book_folder = "/home/zevi5/Downloads/otzaria-library/OnYourWayToOtzaria/סקריפטים/שונות/xml"
root = tree.getroot()

process_node(root, book_folder)

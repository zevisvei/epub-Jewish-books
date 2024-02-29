import os

def convert_in_folder(folder_path):
    skip_files = ["interleave", "merged", "debugmix"]
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            remove_file = False
            if file_name.lower().endswith(".txt"):
                old_path = os.path.join(root, file_name)
                for i in skip_files:
                    if i in file_name.lower():
                        remove_file = True
                if remove_file:        
                    os.remove(old_path)
                    print (f"removed: {old_path}")
                else:
                    new_path = os.path.join(root, file_name[:-4] + ".html")
                    os.rename(old_path, new_path)
                    convert_encoding(new_path, file_name)
                    os.remove(new_path)

def convert_encoding(file_path, file_name):
    try:
        with open(file_path, 'r', encoding='windows-1255') as ansi_file:
            content = ansi_file.read().replace("[[","<b>").replace("]]","</b>").replace("{{{","<u><b>").replace("}}}","</b></u>").replace("(((",f'<b style="color:RGB(127,127,127); font-size:25px;">').replace(")))","</b>")

        # Remove un convertible characters
        content = content.encode('utf-8', 'ignore').decode('utf-8')

        with open(file_path, 'w', encoding='utf-8') as utf8_file:
            utf8_file.write(content)

        print(f"Converted: {file_path}")
        process_html_file(file_path, file_name)
    except Exception as e:
        print(f"Error converting {file_path}: {e}")
    
def process_html_file(input_file, file_name, input_encoding='utf-8'):
    with open(input_file, 'r', encoding=input_encoding) as f:
        html_content = f.read()
        processed_lines = []
    # Split lines and process each line
    lines = html_content.splitlines()
    lest_line = 0
    lest_line_2 = ""
    line_index = 0
    first = False
    informashen_file = [input_file + "$$$"]
    booktitle = 'Untitled Book'
    textsurce2=""
    TextSource = lines[0].split("&")
    for i in TextSource:
        if "TextSource" in i:
            textsurce = i.replace("TextSource=", "")
            if textsurce != "." and textsurce != "":
                informashen_file.append(textsurce + "$$$")
                textsurce2 = f'<p>כל הזכויות שמורות ל{textsurce}</p>'+'\n'+f'<p>בכפוף לתנאי רשיון CC BY-NC-SA 2.5 - אסור בשימוש מסחרי</p>'+'\n'+f'<p><a href=http://creativecommons.org/licenses/by-nc-sa/2.5/deed.he_GB target=_blank style=color:blue>http://creativecommons.org/licenses/by-nc-sa/2.5/deed.he_GB</a></p>'
                informashen_file.append(textsurce2.replace("</p>","").replace("<p>","") + "$$$")
        elif "SpecialTitle" in i:
            textsurce = i.replace("SpecialTitle=","")
            if textsurce != "." and textsurce != "":
                informashen_file.append("ויקיטקסט" + "$$$")
                textsurce2 = f'כל הזכויות שמורות ל - ''ויקיטקסט'' תחת רשיון ''GNU Free Doc"'
                informashen_file.append(textsurce2 + "$$$")
 
    if textsurce2 != "":
        processed_lines.append(textsurce2)
    for line in lines[1:]:
        # Process lines with #, @, ~
        if line.startswith(f'// C:\Dev') and line.endswith('pages'):
            pass
        elif "**INDEX_WRITE=" in line:
            pass
        elif line.startswith('#'):
            processed_lines.append(f'<h1 class="bookTitle">{line[2:]}</h1>')
            lest_line=1
            first = True
        elif line.startswith('^'):
            processed_lines.append(f'<h1 class="bbookTitle">{line[2:]}</h1>')
            lest_line=1
            first = True
        elif line.startswith('@'):
            if not first: 
                processed_lines.append(f'<h1 class="subbookTitle">{line[2:]}</h1>')
                lest_line = 1
            elif first:
                processed_lines.append(f'<h2 class="chapter">{line[2:]}</h2>')
                lest_line = 2
        elif line.startswith('~'):
            if lest_line > 1:
                processed_lines.append(f'<h3 class="section">{line[2:]}</h3>')
                lest_line=3
            elif lest_line == 1:
                processed_lines.append(f'<h2 class="chapter">{line[2:]}</h2>') 
            elif lest_line == 0:
                processed_lines.append(f'<h1 class="bookTitle">{line[2:]}</h1>')
        elif line.startswith("!"):
            lest_line_2 = f'<b>{line[2:]}</b>'
        elif line.startswith("$"):
            if len(line) >= 2:
                booktitle = line[2:]
                informashen_file.insert(0, booktitle + "$$$")
        elif line != "":
            if lest_line_2 != "":
                processed_lines.append('<p class="text">'+ lest_line_2 + " " + line + '</p>')
                lest_line_2 = ""
            else:
                processed_lines.append('<p class="text">' + line + '</p>')
    processed_lines_2 = [f'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" lang="he" xml:lang="he" dir="rtl">
  <head>
    <title>'''+booktitle+f'''</title>
    <meta http-equiv="content-type" content="text/html;charset=utf-8" />
    <meta http-equiv="content-language" content="he" />
  </head>
  <body lang="he-IL" xml:lang="he-IL">
		<div class="Basic-Text-Frame" dir="rtl">''']
    for line in processed_lines:
        try:
            line_index+=1
            next_line = processed_lines[line_index]
            if line.startswith(f'<h') and next_line.startswith(f'<h') and line[:15] == next_line[:15]:
                pass
            else:
                processed_lines_2.append(line)
        except IndexError:
            processed_lines_2.append(line)
    processed_lines_2.append(f'''  </head>
  </div>
  <body>
  </html>''')
    # Join the processed lines back into HTML content
    processed_html = '\n'.join(processed_lines_2)
    # Write the modified HTML content to the output file
    output_file_name = os.path.join(input_file[:-5], file_name[:-4])
    os.makedirs(os.path.join(input_file[:-5]),exist_ok=True) #אפשר להוריד את הג'וין
    with open(output_file_name+".html", 'w', encoding='utf-8') as f:
        f.write(processed_html)
        print(f"processed: {input_file}")
    processed_informashen = '\n'.join(informashen_file)
    with open(output_file_name+".txt", 'w', encoding='utf-8') as text:
        text.write(processed_informashen)

folder_path = r'.\Books'

convert_in_folder(folder_path)

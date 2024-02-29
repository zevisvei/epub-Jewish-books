import os
import zipfile

def edit_in_folder(folder_path, autpoot_dir):
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith('.epub'):
                file_path = os.path.join(root, file_name)
                print(file_path)
                edit_epub_spine(file_path, autpoot_dir, file_name)

def edit_epub_spine(srcfile, autpoot_dir, file_name):
    a = b'<spine toc="ncx">'
    b = b'<spine toc="ncx" page-progression-direction="rtl">'
    c = b'<spine>'

    file_path = srcfile[:-4] + "txt"
    folder_dic = {"ACCESORIES":"עזרים שונים", "HORADOT":"ספרים להורדה", "TORA":"תורה", "NAVI":"נביאים",
    "KTUVIM":"כתובים", "MISHNA":"משנה", "BAVLI":"תלמוד בבלי", "RAMBAM":"משנה תורה להרמב''ם", "HALACHA1":"הלכה 1",
    "HALACHA2":"הלכה 2", "IYUNIM":"עיונים בהלכה ובש''ס", "MUSAR":"מוסר", "KABALA":"קבלה", "CHASIDUT":"חסידות",
    "HANHAGOT":"הנהגות", "PARSHA":"פרשת השבוע", "HAGIM":"חגי ומועדי ישראל", "GDOLEY_HADOROT":"גדולי הדורות",
    "SHUT":"שאלות ותשובות", "HABITE":"הבית היהודי", "CONTRAS":"קונטרסים", "HADERECH_LATORA":"הדרך לתורה",
    "TFILOT_VESGULOT":"תפילות וסגולות", "HIDONIM":"חידונים", "AHAVAT_ISRAEL":"אהבת ישראל", "MISC":"שונות",
    "GROUPS":"קבוצות", "NOTES":"פנקסי ההערות שלי", "MY_BOOKS":"הספרים שלי", "TUR":"טור", "YERUSHALMI":"תלמוד ירושלמי",
    "RAMBAM_ON_MISHNA":"רמבם על המשנה", "SHIMONI":"ילקוט שמעוני", "BERESHIT":"בראשית", "SHEMOT":"שמות", "VAIKRA":"ויקרא",
    "BAMIDBAR":"במדבר", "DEVARIM":"דברים", "YEHOSUA":"יהושע", "SHOFETIM":"שופטים", "SHEMUEL_A":"שמואל א", "SHEMUEL_B":"שמואל ב",
    "MELACIM_A":"מלכים א", "MELACIM_B":"מלכים ב", "YISHAYA":"ישעיה", "YERMIYA":"ירמיה", "YEHEZKEL":"יחזקאל", "HOSEA":"הושע",
    "YOEL":"יואל", "AMOS":"עמוס", "OVADYA":"עובדיה", "YONA":"יונה", "MICHA":"מיכה", "NAHUM":"נחום", "HAVAKUK":"חבקוק",
    "ZFANYA":"צפניה", "HAGAY":"חגי", "ZECHARYA":"זכריה", "MALACHI":"מלאכי", "TEHILIM":"תהילים", "MISHLEI":"משלי", "IYOV":"איוב",
    "SHIR_HASHIRIM":"שיר השירים", "RUTH":"רות", "EICHA":"איכה", "KOHELET":"קהלת", "ESTER":"אסתר", "DANIEL":"דניאל", "EZRA":"עזרא",
    "NECHEMYA":"נחמיה", "DIVRE_A":"דברי הימים א", "DIVRE_B":"דברי הימים ב", "SEDER_ZRAIM":"סדר זרעים", "SEDER_MOED":"סדר מועד",
    "SEDER_NASHIM":"סדר נשים", "SEDER_NEZIKIN":"סדר נזיקין", "SEDER_KADASHIM":"סדר קדשים", "SEDER_TAHAROT":"סדר טהרות",
    "MAS_BRACHOT":"מסכת ברכות", "MAS_PEA":"מסכת פאה", "MAS_DEMAI":"מסכת דמאי", "MAS_KILAIIM":"מסכת כלאים",
    "MAS_SHEVIIT":"מסכת שביעית", "MAS_TRUMOT":"מסכת תרומות", "MAS_MAASROT":"מסכת מעשרות", "MAS_MAASER_SHENI":"מסכת מעשר שני",
    "MAS_CHALA":"מסכת חלה", "MAS_ORLA":"מסכת ערלה", "MAS_BIKURIM":"מסכת ביכורים", "MAS_SHABAT":"מסכת שבת",
    "MAS_ERUVIN":"מסכת עירובין", "MAS_PSACHIM":"מסכת פסחים", "MAS_SHKALIM":"מסכת שקלים", "MAS_ROSH":"מסכת ראש השנה",
    "MAS_YOMA":"מסכת יומא", "MAS_SUCA":"מסכת סוכה", "MAS_BEITSA":"מסכת ביצה", "MAS_TAANIT":"מסכת תענית",
    "MAS_MEGILA":"מסכת מגילה", "MAS_MOED_KATAN":"מסכת מועד קטן", "MAS_HAGIGA":"מסכת חגיגה",
    "MAS_YEVAMOT":"מסכת יבמות", "MAS_KTUBOT":"מסכת כתובות", "MAS_NEDARIM":"מסכת נדרים",
    "MAS_NAZIR":"מסכת נזיר", "MAS_SOTA":"מסכת סוטה", "MAS_GITIN":"מסכת גיטין", "MAS_KIDUSHIN":"מסכת קידושין",
    "MAS_KAMA":"מסכת בבא קמא", "MAS_METSIA":"מסכת בבא מציעא", "MAS_BATRA":"מסכת בבא בתרא", "MAS_SANHEDRIN":"מסכת סנהדרין",
    "MAS_MAKOT":"מסכת מכות", "MAS_SHVUOT":"מסכת שבועות", "MAS_AVODA_ZARA":"מסכת עבודה זרה", "MAS_AVOT":"מסכת אבות",
    "MAS_HORAYOT":"מסכת הוריות", "MAS_EDUYOT":"מסכת עדיות", "MAS_ZEVACHIM":"מסכת זבחים", "MAS_MENACHOT":"מסכת מנחות",
    "MAS_CHULIN":"מסכת חולין", "MAS_BECHOROT":"מסכת בכורות", "MAS_ARACHIN":"מסכת ערכין", "MAS_TEMURA":"מסכת תמורה",
    "MAS_KRETOT":"מסכת כריתות", "MAS_MEILA":"מסכת מעילה", "MAS_TAMID":"מסכת תמיד", "MAS_MIDOT":"מסכת מדות",
    "MAS_KANIM":"מסכת קנים", "MAS_KELIM":"מסכת כלים", "MAS_AHALOT":"מסכת אהלות", "MAS_NEGAIIM":"מסכת נגעים",
    "MAS_PARA":"מסכת פרה", "MAS_TAHAROT":"מסכת טהרות", "MAS_MIKVAOT":"מסכת מקואות", "MAS_NIDA":"מסכת נדה",
    "MAS_MACHSHIRIN":"מסכת מכשירין", "MAS_ZAVIM":"מסכת זבים", "MAS_TEVUL_YOM":"מסכת טבול יום",
    "MAS_YADAIIM":"מסכת ידים", "MAS_OKATSIN":"מסכת עוקצין", "GROUP_SHABAT":"קבוצת שבת קודש", "GROUP_TAHARA":"קבוצת טהרת המשפחה",
    "GROUP_TSNIUT":"קבוצת צניעות האשה", "GROUP_KASHRUT":"קבוצת כשרות המטבח"}
    with open(file_path, 'r', encoding='utf-8') as text:
        text_content = text.read().split("$$$")
        tages_2 = ""
        heb_root = ""
        file_root = text_content[1]
        tages = file_root.split("\\")
        print(tages)
        for i in tages[2:-1]:
            i_2 = i.split("_")
            i_3 = "_".join(i_2[1:])
            tages_2+=", " + folder_dic.get(i_3)
            heb_root+=i_2[0]+"_"+folder_dic.get(i_3)+"\\"
    os.makedirs(os.path.join(autpoot_dir, heb_root),exist_ok=True) 
    temp_file = os.path.join(autpoot_dir, heb_root, file_name)
    with zipfile.ZipFile(srcfile, "r") as inzip, zipfile.ZipFile(temp_file, "w") as outzip:
        for inzipinfo in inzip.infolist():
            with inzip.open(inzipinfo) as infile:
                if inzipinfo.filename == "content.opf":
                    content = infile.read().replace(a, b).replace(c, b)
                    content_2 = content.decode("utf-8").splitlines()
                    content_3 = []
                    line = -1
                    try:
                        rights = text_content[3]
                    except IndexError:
                        rights = "לא צויין"
                    bbbb = {"<dc:publisher":False,"<dc:creator":False
                    ,"<dc:subject":False,"<dc:rights":False}
                    description = publisher = True
                    xx = {"<dc:publisher":f'    <dc:publisher>תורת אמת</dc:publisher>'
                    ,"<dc:creator":f'    <dc:creator>{text_content[2]}</dc:creator>'
                    ,"<dc:subject":f'    <dc:subject>{tages_2[2:]}</dc:subject>'
                    ,"<dc:rights":f'    <dc:rights>{rights}</dc:rights>'
                    ,"<dc:title":f'    <dc:title>{text_content[0]}</dc:title>'}
                    for i in content_2:
                        aaaaa = []
                        for x in xx:
                            if x in i:
                                content_3.append(xx.get(x))
                                aaaaa.append(True)
                                bbbb.update({x:True})
                                line+=1
                            else:
                                aaaaa.append(False)
                        if any (aaaaa):
                            pass
                        else:
                            try:
                                if "</metadata>" in content_2[line+1]:
                                    for i in bbbb:
                                        if bbbb.get(i) == False:
                                            content_3.append(xx.get(i))
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
    
    print(f"processed: {srcfile}")

folder_path = r'.\jj'
autpoot_dir = r'.\autpoot'
edit_in_folder(folder_path, autpoot_dir)
#"<dc:description":False
#"<dc:description":f'    <dc:description>gggggדדדדד</dc:description>'


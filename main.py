import fitz  # PyMuPDF
import json
import re

def extract_number_and_text(title):
    # 3.1.4
    multi_part_match = re.match(r"^(\d+\.\d+\.\d+)", title)
    if multi_part_match:
        number = multi_part_match.group(1)
        text = title[multi_part_match.end():].strip()  
        return number, text
    # 3.2
    single_part_match = re.match(r"^(\d+\.\d+)", title)
    if single_part_match:
        number = single_part_match.group(1)
        text = title[single_part_match.end():].strip()  
        return number, text
    # 13
    if 'Глава' in title:
        chapter_match = re.search(r"(\d+)", title) 
        if chapter_match:
            number = chapter_match.group(1)
            text = title[chapter_match.end():].strip()  
            return str(number), text
    # " "
    return " ", title.strip()


def build_structure_data(items):
    structure = {}
    
    for number, text in items:
        levels = number.split('.')
        section = structure

        for i, level in enumerate(levels):
            section_number = '.'.join(levels[:i + 1])

            if section_number not in section:
                section[section_number] = {"title": text if i == len(levels) - 1 else ""}
                
                if i == 0:
                    section[section_number]["sections"] = {}
                elif i == 1:
                    section[section_number]["subsections"] = {}

            if i == 0:
                section = section[section_number]["sections"]
            elif i == 1:
                section = section[section_number]["subsections"]
            else:
                section = section[section_number]

    return structure

def extract_structure_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        toc = doc.get_toc()
        items = []
        for i in range(len(toc)):
            _, title, _ = toc[i]
            # print(title)
            number, text = extract_number_and_text(title)
            if 'Глава' in title:
                _,text = extract_number_and_text(toc[i+1][1])
            if number.strip():    
                items.append((number, text))
                print(number)
        structure = build_structure_data(items)

    except Exception as e:
        print(f"Error processing PDF: {e}")

    return structure

def save_to_json(data, filename="structure.json"):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Structure saved to {filename}")
    except Exception as e:
        print(f"Error saving JSON: {e}")

if __name__ == '__main__':
    pdf_path = "./data/pdf/1.pdf"
    structure = extract_structure_from_pdf(pdf_path)
    save_to_json(structure)

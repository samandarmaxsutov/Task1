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
     # Match for single-part version numbers (e.g., 2.1 or 2.1.)
    single_part_match = re.match(r"^(\d+\.\d+\.?)", title)  # Allow for an optional trailing dot
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

def remove_equal_subsections(structure):
    for key, value in list(structure.items()):
        if "subsections" in value:
            keys_to_remove = [sub_key for sub_key in value["subsections"].keys() if sub_key == key]
            for sub_key in keys_to_remove:
                del value["subsections"][sub_key]
        if "sections" in value:
            remove_equal_subsections(value["sections"])
            
def build_structure_data(items):
    structure = {}

    for number, text in items:
        if not number.strip():
            continue
        
        levels = number.split('.')
        current_section = structure
        
        for i, level in enumerate(levels):
            section_number = '.'.join(levels[:i + 1])
            
            if i == 1 and number.endswith('.'):
                section_number += '.'

            if section_number not in current_section:
                section_data = {"title": ""}
                
                if i == 0:
                    section_data["sections"] = {}
                elif i == 1:
                    section_data["subsections"] = {}
                
                current_section[section_number] = section_data
            if i == len(levels) - 1 or (i == 1 and number.endswith('.')):
                current_section[section_number]["title"] = text
            
            if i == 0:
                current_section = current_section[section_number]["sections"]
            elif i == 1:
                current_section = current_section[section_number]["subsections"]
            else:
                current_section = current_section[section_number]

    return structure

def extract_structure_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        toc = doc.get_toc()
        items = []
        for i in range(len(toc)):
            _, title, _ = toc[i]
            
            number, text = extract_number_and_text(title)
            if 'Глава' in title:
                _,text = extract_number_and_text(toc[i+1][1])
            if number.strip():    
                items.append((number, text))
                # print(number)
        structure = build_structure_data(items)
        remove_equal_subsections(structure)
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

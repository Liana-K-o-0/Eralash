import json
from pathlib import Path
from dataclasses import dataclass
import shutil
from collections import defaultdict
from classifier import EmailClassifier
from logger import Result_file

result_file = Result_file()
classifier = EmailClassifier()

@dataclass
class Email:
    def __init__(self, file_path:Path, sender:str="", towho:str="", topic:str="", text:str=""):
        self.towho = towho
        self.sender = sender
        self.file_path = file_path
        self.text = text
        self.topic = topic

def cycle_in_dir(dirpath : Path):

    for item in dirpath.iterdir():
        if item.is_file() and item.suffix.lower() == '.txt':
            create_letter_object(item)
        else:
            result_file.add_information('error',item.name)



def create_letter_object(file_path):
    try:
        with open(file_path,'r', encoding='utf-8') as file:
            letter_object = Email(file_path=file_path)
            for line in file:
                stripped = line.strip()
                if not stripped:
                    continue 

                if ":" in stripped:
                    key_part,text_part = stripped.split(':',1)
                    key_part = key_part.strip()
                    text_lower = text_part.strip().lower()
                    
                    if key_part in ("Subject","Тема") and not letter_object.topic:
                        letter_object.topic = text_lower
                    elif key_part in ("From","От кого") and not letter_object.sender:
                        letter_object.sender = text_lower
                    elif key_part in ("To","Кому") and not letter_object.towho:
                        letter_object.towho = text_lower
                    else:
                        letter_object.text += stripped
                else:
                    letter_object.text += stripped
            classifier.classify(letter_object)
    except Exception as e:
        result_file.add_information('error',file_path.name)
        

def put_to_folder(category:str,filepath):

    outbox = Path("")#
    # if not filepath.is_file():
    #     print(f"Файл не найден: {filepath}")
    target_dir = outbox / category 
    target_dir.mkdir(exist_ok=True)
    target_path = target_dir/filepath.name
    shutil.move(str(filepath),str(target_path))

    result_file.add_information(category,filepath.name)
    

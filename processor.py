import json
from pathlib import Path
from dataclasses import dataclass
import shutil
from collections import defaultdict
from logger import Result_file


@dataclass
class Email:
    def __init__(self, file_path:Path, sender:str="", towho:str="", topic:str="", text:str=""):
        self.towho = towho
        self.sender = sender
        self.file_path = file_path
        self.text = text
        self.topic = topic

class Process:

    def __init__(self):
        self.result_file=Result_file()
        self.category = ""

    def cycle_in_dir(self,dirpath : Path, classifier):
        for item in dirpath.iterdir():
            if item.is_file():
                self.process_file(item, classifier)

    def process_file(self,item, classifier):
        if item.name == '.DS_Store' or item.name.startswith('.'):
            print("error in process_file :item.name == '.DS_Store' or item.name.startswith('.') ")
            self.result_file.add_information('error',item.name)
            return
        if item.suffix in ('.txt', '.eml') :
            self.create_letter_obj_txt(item, classifier)
        elif item.suffix == '.json':
            self.create_letter_obj_json(item, classifier)
        elif item.suffix == '':
            self.try_create_obj_unknown(item, classifier)
        else:
            print("error in process_file ")
            self.result_file.add_information('error',item.name)
            return

    def try_create_obj_unknown(self,file_path, classifier):
        try:
            with open(file_path, "r",encoding='utf-8') as file:
                data = file.read()
            if data:
                self.create_letter_obj_txt(file_path, classifier)
            else:
                print("error in try_create_obj_unknown after opening unknowm ")
                self.result_file.add_information('error',file_path.name)
                return
        except Exception as e:
            print("error in try_create_obj_unknown ")
            self.result_file.add_information('error',file_path.name)

    def create_letter_obj_json(self,file_path, classifier):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            sender = data.get('from', '')
            topic = data.get('subject', '')
            body = data.get('body', '')

            if isinstance(body, (dict, list)):
                body = json.dumps(body, ensure_ascii=False)
            letter_object = Email(file_path=file_path, sender=sender, topic=topic, text=body)
            
            self.put_to_folder(classifier.classify(letter_object),file_path)
        except Exception as e:
            print("error in create_letter_obj_json ")
            self.result_file.add_information('error',file_path.name)

    def create_letter_obj_txt(self,file_path, classifier):
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
                self.put_to_folder(classifier.classify(letter_object),file_path)
        except Exception as e:
            print("error in create_letter_obj_txt ")
            self.result_file.add_information('error',file_path.name)
            

    def put_to_folder(self,category:str,filepath):

        target_dir = Path(f"outbox/{category}")
        target_dir.mkdir(exist_ok=True)
        target_path = target_dir/filepath.name
        shutil.move(str(filepath),str(target_path))

        self.result_file.add_information(category,filepath.name)


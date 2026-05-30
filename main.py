import sys
import os
# from processor import cycle_in_dir
# from logger import Result_file
import json
from classifier import EmailClassifier
from processor import Process
from pathlib import Path

def main():

    classifier = EmailClassifier()
    process = Process()
    outbox_dir = "outbox"

    directory_path = "inbox"
    show_logs = False
    config_file = None

    if len(sys.argv) > 1:
        i = 1
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == "--show-logs":
                show_logs = True
                i += 1
            elif arg == "--config":
                if i + 1 < len(sys.argv):
                    config_file = sys.argv[i + 1]
                    i += 2
                else:
                    print("Ну ты чё дурак?")
                    return
            elif not arg.startswith("--"):
                directory_path = arg
                i += 1
            else: i += 1

    if config_file:
        if os.path.exists(config_file):
            classifier.add_rules(config_file)

    process.cycle_in_dir(Path(directory_path), classifier)
    logs_list = process.result_file.get_log_list()
    json_stat = process.result_file.get_stat_json()

    with open("statistics.json", "w", encoding="utf-8") as f_stat:
        f_stat.write(json_stat)

    with open("process_log.json", "w", encoding="utf-8") as f_log:
        json_logs = json.dumps(logs_list, ensure_ascii=False, indent=4)
        f_log.write(json_logs)

    if show_logs:
        print("\n---ИТОГОВАЯ СТАТИСТИКА---")
        stat_dict = json.loads(json_stat)
        print(json.dumps(stat_dict, ensure_ascii=False, indent=4))

        print("\n---ИТОГОВЫЙ ЛОГ---")
        for line in logs_list:
            print(line)


contacts = {"Черемша": "+7 (988) 472-88-72", "Анна": "+7 (988) 994-98-49", "Виктория": "+7 (922) 879-50-43", "Мария": "+7 (989) 249-36-40", "Елена": "+7 (982) 888-05-91","Дарья": "+7 (918) 473-26-57","Ксения": "+7 (918) 052-29-60","Полина": "+7 (495) 771-32-42","Анастасия": "+7 (995) 223-73-98","Екатерина": "+7 (962) 039-73-55","Ольга": "+7 (967) 307-46-26","Татьяна": "+7 (967) 652-59-63","Наталья": "+7 (950) 530-40-79","Ирина": "+7 (968) 049-75-10","Светлана": "+7 (918) 165-12-83","Марина": "+7 (961) 525-27-34","Надежда": "+7 (995) 262-15-27","Любовь": "+7 (918) 476-14-29","Алиса": "+7 (988) 620-54-10"}
folder_name = "Бабочки Набережные Челны"
os.makedirs(folder_name, exist_ok=True)
file_path = os.path.join(folder_name, "contacts.json")
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(contacts, f, ensure_ascii=False, indent=4)
if __name__ == "__main__":
    main()

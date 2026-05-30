import sys
import os
from processor import Processor
from logger import Result_file
import json
from classifier import EmailClassifier
from pathlib import Path



def main():

    classifier = EmailClassifier()
    processor = Processor()
    
    outbox_dir = "outbox"
    categories = ["черновики", "важное", "спам", "ошибки", "неотсортированное"]
    for category in categories:
        os.makedirs(os.path.join(outbox_dir, category), exist_ok=True)

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

    processor.cycle_in_dir(Path(directory_path), classifier)
    logs_list = Result_file.get_log_list()
    json_stat = Result_file.get_stat_json()

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

if __name__ == "__main__":
    main()

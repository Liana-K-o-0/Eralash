#Надо будет добавить обработку json и разобраться с именами категорий

import sys
import os
from processor import cycle_in_dir
from logger import Result_file
import json

def main():
    outbox_dir = "outbox"
    categories = ["черновики", "важное", "спам", "ошибки", "неотсортированное"]
    for category in categories:
        os.makedirs(os.path.join(outbox_dir, category), exist_ok=True)

    directory_path = "inbox"
    show_logs = False

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg == "--show-logs":
                show_logs = True
            elif not arg.startswith("--"):
                directory_path = arg

    print(f"Скрипт запущен. Путь к папке: {directory_path}")
    cycle_in_dir(directory_path)
    logs_list = Result_file.get_log_list()
    json_stat = Result_file.get_stat_json()

    with open("statistics.json", "w", encoding="utf-8") as f_stat:
        f_stat.write(json_stat)

    with open("process_log.json", "w", encoding="utf-8") as f_log:
        json_logs = json.dumps(logs_list, ensure_ascii=False, indent=4)
        f_log.write(json_logs)

    if show_logs:
        print("\n--- ИТОГОВАЯ СТАТИСТИКА ---")
        stat_dict = json.loads(json_stat)
        print(json.dumps(stat_dict, ensure_ascii=False, indent=4))

        print("\n--- ИТОГОВЫЙ ЛОГ ---")
        for line in logs_list:
            print(line)


if __name__ == "__main__":
    main()

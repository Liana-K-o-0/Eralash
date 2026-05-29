from collections import defaultdict
import json
class Result_file:
    def __init__(self):
        self.data=defaultdict(int)
        self.log=[]

    def add_information(self, category, email_name):
        self.data[category]+=1
        if category != 'error':
            self.log.append(f'{email_name} ---> {category}')
        else:
            self.log.append(f'{email_name} ---> Файл не удалось отнести ни к одной категории')
        
    def get_log_list(self):
        return self.log
    
    def get_stat_json(self):
        return json.dumps(self.data, ensure_ascii=False)
    
result = Result_file()

result.add_information('spam', 'email1')
result.add_information('ham', 'email2')
result.add_information('error', 'email3')

log=result.get_log_list()
for line in log:
    print(line)
stat_json=result.get_stat_json()
print(stat_json)

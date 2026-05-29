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
    

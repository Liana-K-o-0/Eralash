from collections import defaultdict
import json
import matplotlib.pyplot as plt
#from processor import to_logger

class Result_file:
    def __init__(self):
        self.data=defaultdict(int)
        self.log=[]

    def add_information(self, category, email_name):
        self.data[category]+=1
        self.log.append(f'{email_name} ---> {category}')
        
    def get_log_list(self):
        return self.log
    
    def get_stat_json(self):
        return json.dumps(self.data, ensure_ascii=False)
    
    def make_pie(self):
        if not self.data:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "Нет данных", ha="center", va="center")
            ax.axis("off")
            return fig

        labels = [f"{cat}: {n}" for cat, n in self.data.items()]
        values = list(self.data.values())

        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct="%1.0f%%", startangle=90)
        ax.set_title("Письма по категориям")
        ax.axis("equal")
        return fig

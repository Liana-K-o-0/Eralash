#Надо будет ещё раз подумать про категории и ключевые слова перебрать

from dataclasses import dataclass, field
import json
from pathlib import Path

@dataclass
class Rule:
    category: str
    keywords: list = field(default_factory=list)
    from_contains: list = field(default_factory=list)
    priority: int = 1000

    def match(self, email):
        text = email.topic.lower()+email.text.lower()  
        for i in self.keywords:
            if i.lower() in text:
                return True
            
        if email.sender:
            sender = email.sender.lower()
            for j in self.from_contains:
                if j.lower() in sender:
                    return True   
                  
        return False
    
    @classmethod
    def new_rule(cls, inf):
        return cls(
            category=inf["category"],
            keywords=inf.get("keywords", []),
            from_contains=inf.get("from_contains", []),
            priority=inf.get("priority", 1000)
        )

class EmailClassifier:
    def __init__(self, rules=None, default_category="иное"):
        if rules is None:
            rules = self.get_rules()
        self.rules = sorted(rules, key=lambda x: x.priority)
        self.default_category = default_category
    
    def get_rules(self):
        return [
            Rule(
                category="проблемы",
                priority=100,
                keywords=[
                    "срочн", "не работ", "слома",
                    "ошибка", "баг", "глюк", "падение",
                    "авария", "инцидент", "проблем",
                    "критично", "критическое",
                    "сервер не отвечает", "доступ",
                    "не загружается", "висит", "завис"
                    "urgent", "critical", "asap",
                    "fail", "error", "crash", "down", "outage",
                    "not working", "broken"
                ],
                from_contains=[
                    "alert", "monitoring", "nagios", "zabbix"
                ]
            ),
            
            Rule(
                category="важное",
                priority=200,
                keywords=[
                    "важн",
                    "начальник", "директор", "руковод",
                    "распоряжен", "приказ", "правление",
                    "внимание", "вниманию"
                ],
                from_contains=[
                    "director", "ceo", "head", "boss", "chief",
                    "руководитель", "начальник", "директор"
                ]
            ),
            
            Rule(
                category="спам",
                priority=300,
                keywords=[
                    "спам", "реклама", "акция", "скидка", "распродажа",
                    "партнер", "сотрудничество", "продвижение",
                    "заработок", "инвестиции", "криптовалюта",
                    "лотерея", "выигрыш", "приз", "бесплатно",
                    "купить", "продать", "оферта",
                    "увеличь продажи", "раскрутка", "seo",
                    "отписка", "рассылка", "подписка",
                    "spam", "advertisement", "promo", "offer", "deal",
                    "discount", "sale", "buy now", "click here",
                    "unsubscribe", "newsletter", "marketing"
                ],
                from_contains=[
                    "promo", "marketing", "newsletter", "noreply",
                    "no-reply", "mailer", "advert"
                ]
            ),

            Rule(
                category="уведомления",
                priority=400,
                keywords=[
                    "уведомление", "автоматическое сообщение", "do not reply",
                    "не отвечайте на это письмо", "notification",
                    "резервное копирование", "мониторинг"
                    "backup completed", "alert:",
                ],
                from_contains=["no-reply", "noreply", "donotreply",
                            "notification", "monitoring"]
            ),
            
            Rule(
                category="запросы",
                priority=500,
                keywords=[
                    "пароль",
                    "доступ", "права", "разрешени",
                    "установ", "настро",
                    "помоги", "подскажи", "как сделать", "вопрос",
                    "заявка", "обращение", "просьба", "помощь", "программа", "обнов"
                    "не могу войти", "не заходит", "не получает"
                    "help", "request", "question", "issue",
                    "password", "access", "permission", "install",
                    "update", "upgrade", "how to"
                ]
            ),
        ]
    
    def classify(self, email):
        for rule in self.rules:
            if rule.match(email):
                return rule.category
        return self.default_category
    
    
    def add_rules(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            inf = json.load(f)
        new_rules = [Rule.new_rule(i) for i in inf.get("rules", [])]
        self.rules.extend(new_rules)
        self.rules.sort(key=lambda x: x.priority)

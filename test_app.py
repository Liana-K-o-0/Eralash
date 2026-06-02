import json
from typing import Literal
import pytest
from pathlib import Path
from classifier import EmailClassifier
from processor import Process, Email

@pytest.fixture
def classifier():
    return EmailClassifier()

@pytest.fixture
def processor():
    return Process()

@pytest.mark.parametrize('sender, topic, text, expected_category', [
    ("scammer@bad.com", "Поздравляем!", "Вы выиграли iphone", "спам, фишинг, вредоносные"),
    ("hello@spam.com", "Обычная тема", "Обычный текст", "спам, фишинг, вредоносные"),
    ("dev@company.com", "Алерт", "Ошибка 500 на сервере", "технические сбои и проблемы ПО"),
    ("user@company.com", "Проблема", "Как настроить vpn?", "доступы, права, учетные записи"),
    ("manager@company.com", "Заявление", "Прошу дать отпуск", "документы, бухгалтерия, юридические запросы"),
    ("hr@company.com", "Обучение", "Приглашаем на вебинар", "прочие запросы и уведомления"),
    ("friend@mail.ru", "Привет", "Как дела?", "неотсортированное"),
    ("", "", "", "неотсортированное")
])
def test_classifier_logic(classifier: EmailClassifier, sender: Literal['scammer@bad.com'] | Literal['hello@spam.com'] | Literal['dev@company.com'] | Literal['user@company.com'] | Literal['manager@company.com'] | Literal['hr@company.com'] | Literal['friend@mail.ru'] | Literal[''], topic: Literal['Поздравляем!'] | Literal['Обычная тема'] | Literal['Алерт'] | Literal['Проблема'] | Literal['Заявление'] | Literal['Обучение'] | Literal['Привет'] | Literal[''], text: Literal['Вы выиграли iphone'] | Literal['Обычный текст'] | Literal['Ошибка 500 на сервере'] | Literal['Как настроить vpn?'] | Literal['Прошу дать отпуск'] | Literal['Приглашаем на вебинар'] | Literal['Как дела?'] | Literal[''], expected_category: Literal['спам, фишинг, вредоносные'] | Literal['технические сбои и проблемы ПО'] | Literal['доступы, права, учетные записи'] | Literal['документы, бухгалтерия, юридические запросы'] | Literal['прочие запросы и уведомления'] | Literal['неотсортированное']):
    print(f"Тест [{expected_category}] - ", end="")
    email = Email(file_path=Path("dummy.txt"), sender=sender, topic=topic, text=text)
    
    try:
        assert classifier.classify(email) == expected_category
        print("ok")
    except AssertionError:
        print("error")
        raise

def test_processor_txt_files(processor: Process, classifier: EmailClassifier, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    print("Проверка txt файлов - ", end="")
    monkeypatch.chdir(tmp_path)
    inbox_dir = Path("inbox")
    inbox_dir.mkdir()

    f_doc = inbox_dir / "doc.txt"
    f_doc.write_text("From: a@b.com\nSubject: Договор\n\nСкан паспорта.", encoding="utf-8")

    processor.cycle_in_dir(inbox_dir, classifier)
    
    try:
        assert Path("outbox/документы, бухгалтерия, юридические запросы/doc.txt").exists()
        print("ok")
    except AssertionError:
        print("error")
        raise

def test_processor_json_files(processor: Process, classifier: EmailClassifier, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    print("Проверка парсинга json - ", end="")
    monkeypatch.chdir(tmp_path)
    inbox_dir = Path("inbox")
    inbox_dir.mkdir()

    js_file = inbox_dir / "data.json"
    js_file.write_text(json.dumps({
        "from": "sys@sys.com", 
        "subject": "Alert", 
        "body": "Сервер упал"
    }), encoding="utf-8")

    processor.cycle_in_dir(inbox_dir, classifier)
    
    try:
        assert Path("outbox/технические сбои и проблемы ПО/data.json").exists()
        print("ok")
    except AssertionError:
        print("error")
        raise

def test_processor_empty_file(processor: Process, classifier: EmailClassifier, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    print("Тест на пустой файл - ", end="")
    monkeypatch.chdir(tmp_path)
    inbox_dir = Path('inbox')
    inbox_dir.mkdir()
    empty_f = inbox_dir / 'empty.txt'
    empty_f.write_text("", encoding="utf-8")

    processor.cycle_in_dir(inbox_dir, classifier)

    try:
        assert Path("outbox/неотсортированное/empty.txt").exists()
        print("ok")
    except AssertionError:
        print("error")
        raise

def test_processor_unreadable_format(processor: Process, classifier: EmailClassifier, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    print("Тест бинарника - ", end="")
    monkeypatch.chdir(tmp_path)
    inbox_dir = Path("inbox")
    inbox_dir.mkdir()

    img_file = inbox_dir / "image.png"
    img_file.write_bytes(b"image")

    processor.cycle_in_dir(inbox_dir, classifier)
    
    try:
        assert Path("outbox/нечитаемый формат/image.png").exists()
        assert processor.result_file.data['нечитаемый формат'] == 1
        print("ok")
    except AssertionError:
        print("error")
        raise

def test_classifier_with_config(classifier: EmailClassifier, tmp_path: Path):
    print("Тест json конфига - ", end="")
    
    config_data = {
        "rules": [
            {
                "category": "безопасность",
                "priority": 1,
                "keywords": ["пароль"],
                "from_contains": ["security", "soc"]
            },
            {
                "category": "финансы",
                "priority": 25,
                "keywords": ["оплата", "счёт", "налог"],
                "from_contains": ["finance", "bank"]
            }
        ]
    }
    
    conf = tmp_path / "my_rules.json"
    conf.write_text(json.dumps(config_data, ensure_ascii=False), encoding="utf-8")
    classifier.add_rules(str(conf))

    e_sec = Email(file_path=Path("d1.txt"), sender="user@test.ru", topic="Доступ", text="Мой пароль истек")
    e_fin = Email(file_path=Path("d2.txt"), sender="accounting@bank.com", topic="Отчет", text="Прикрепил отчет")
    
    try:
        assert classifier.classify(e_sec) == "безопасность"
        assert classifier.classify(e_fin) == "финансы"
        print("ok")
    except AssertionError:
        print("error")
        raise

if __name__ == "__main__":
    pytest.main(["-s", "-q", __file__])
    

    

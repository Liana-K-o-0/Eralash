#!/bin/bash
 
INBOX="inbox"
 
case "$OSTYPE" in
    msys*|cygwin*|win*) PY="py" ;;
    *)                  PY="python3" ;;
esac

if [ ! -d "$INBOX" ]; then
    echo "Ошибка: папка '$INBOX' не найдена"
    exit 1
fi

"$PY" main.py "$INBOX" --show-logs

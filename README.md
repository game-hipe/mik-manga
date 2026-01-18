# MikManga - Пауки на любой вкус и свет!

В чём прикол данного проекта? Я люблю чиать мангу, и смотреть аниме, как любой школьник в 17 лет, поэтому я создал этот проект! Я хочу эксперементировать с Git, поэтому создам 3 ветки.

## Ветки
    1. Ветка только парсеры, ничего более Это будет основная ветка, тут будут хранится парсеры, сайтов.

    2. Ветка (Telegram Bot)
    Это будет ветка с ТГ ботом, где будет админ аккаунты, просмотр манги, скачивание манги, кэширование в БД, и т п.

    3. Ветка (FastAPI)
    Это будет ветка с FastAPI, где будет FastAPI, будет в роли админа, мы будем собирать данные, и хранить в БД.

# Как запустить проект

## 1 Способ через docker-compose
```bash
git clone https://github.com/game-hipe/notifer.git
cd notifer
cp configuration-example.yaml > configuration.yaml

nano configuration.yaml # Вставтье ваш бот токен, для работы.

docker-compose up . # Либо docker compose up .
```

## 2 Способ через прямой python (python3.13.X+)
```bash
git clone https://github.com/game-hipe/notifer.git
cd notifer
cp configuration-example.yaml > configuration.yaml

nano configuration.yaml # Вставтье ваш бот токен, для работы.
pip install -r requirements.txt
python main.py
```


> [!WARNING]
> Проект является просто демонстрацие своих сил в BackEnd, и в ТГ ботах, поэтому не бейте тапком
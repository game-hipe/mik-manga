# MikManga - Пауки на любой вкус и свет!

В чём прикол данного проекта? Я люблю чиать мангу, и смотреть аниме, как любой школьник в 17 лет, поэтому я создал этот проект!

# Как запустить проект

## 1 Способ через docker-compose
```bash
git clone https://github.com/game-hipe/notifer.git
cd notifer
cp configuration-example.yaml > configuration.yaml

nano configuration.yaml # Вставтье ваш бот токен, для работы.

docker-compose build --no-cache
docker-compose up -d
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

> [!WARNING]
> На данный момент, ни паук, ни тг бот не готов, поэтому запускать ТГ бота бессмысленно!
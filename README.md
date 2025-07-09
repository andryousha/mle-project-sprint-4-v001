# Подготовка виртуальной машины

## Склонируйте репозиторий

Склонируйте репозиторий проекта:

```
git clone https://github.com/yandex-praktikum/mle-project-sprint-4-v001.git
```

## Активируйте виртуальное окружение

Используйте то же самое виртуальное окружение, что и созданное для работы с уроками. Если его не существует, то его следует создать.

Создать новое виртуальное окружение можно командой:

```
python3 -m venv env_recsys_start
```

После его инициализации следующей командой

```
. env_recsys_start/bin/activate
```

установите в него необходимые Python-пакеты следующей командой

```
pip install -r requirements.txt
```

### Скачайте файлы с данными

Для начала работы понадобится три файла с данными:
- [tracks.parquet](https://storage.yandexcloud.net/mle-data/ym/tracks.parquet)
- [catalog_names.parquet](https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet)
- [interactions.parquet](https://storage.yandexcloud.net/mle-data/ym/interactions.parquet)
 
Скачайте их в директорию локального репозитория. Для удобства вы можете воспользоваться командой wget:

```
wget https://storage.yandexcloud.net/mle-data/ym/tracks.parquet

wget https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet

wget https://storage.yandexcloud.net/mle-data/ym/interactions.parquet
```

## Запустите Jupyter Lab

Запустите Jupyter Lab в командной строке

```
jupyter lab --ip=0.0.0.0 --no-browser
```

# Расчёт рекомендаций

Код для выполнения первой части проекта находится в файле `recommendations.ipynb`. Изначально, это шаблон. Используйте его для выполнения первой части проекта.

# Сервис рекомендаций

Код сервиса рекомендаций находится в файле `recommendations_service.py`.

Чтобы запустить сервис:
- Для примера есть файл `.env_example`, заполните секреты для s3 и сохраните как файл `.env`.
- Выполнить (Скачаются все необходимые таблицы с рекомендациями.):  
  ```python
    python downloads_recs_from_s3.py
  ```
- Микросервис имеет 4 модуля:
  - `service/recommendations_service.py` - главный модуль для генерации рекомендаций любого типа
  - `service/events_service.py` - модуль для добавления онлайн событий в историю пользователя
  - `service/features_service.py`- модуль для генерации онлайн рекомендаций
  - `service/recs_offline_service.py` - модуль для генерации оффлайн рекомендаций 

- Чтобы запустить все модули сервиса необходимо в отдельных терминалах запустить команды:
  - ```bash
    . env_recsys_start/bin/activate
    python -m uvicorn service.recommendations_service:app --port 8010 
    ```
  - ```bash
    . env_recsys_start/bin/activate
    python -m uvicorn service.recs_offline_service:app --port 8020  
    ```
  - ```bash
    . env_recsys_start/bin/activate
    python -m uvicorn service.events_service:app --port 8030
    ```
  - ```bash
    . env_recsys_start/bin/activate
    python -m uvicorn service.features_service:app --port 8040
    ```
- После того, как все сервисы буду запущены, можно пользоваться api сервиса по порту '8010'.


# Инструкции для тестирования сервиса

Код для тестирования сервиса находится в файле `test_service.py`.

Запустите следующий код:
```bash
. env_recsys_start/bin/activate
python test_service.py
```

Логи по тестированию будут храниться в файле `test_service.log`.

# Какая стратегия для рекомедаций используется?  
Если у пользователя есть онлайн-история, то сервис будет смешивать онлайн и оффлайн рекомендации. Онлайн на нечетных
местах, а офaлайн на четных.

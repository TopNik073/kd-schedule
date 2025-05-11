# KD-Schedule

Сервис планирования и отслеживания приёма лекарств

## Описание проекта

KD-Schedule - это сервис для управления расписаниями приёма лекарств, который позволяет пользователям:

- Создавать расписания приёма лекарств с настраиваемой частотой
- Получать информацию о ближайших приёмах лекарств

Сервис предоставляет как REST API, так и gRPC интерфейсы для интеграции с различными клиентами.

## Функциональность

- **Создание расписания**: пользователи могут создавать расписания с указанием названия лекарства, частоты приёма, даты начала и окончания (или продолжительности)
- **Получение списка расписаний**: получение всех расписаний для конкретного пользователя
- **Информация о расписании**: получение детальной информации о конкретном расписании
- **Ближайшие приёмы**: получение списка ближайших приёмов лекарств в заданном временном интервале
- **Ограничения по времени**: возможность настройки периодов дня, когда лекарства должны приниматься (например, только с 8:00 до 22:00)

## Технический стек

- **Python 3.12+**
- **FastAPI и Pydantic**: для реализации REST API
- **datamodel-code-generator и protobuf**: для кодогенерации
- **gRPC**: для реализации RPC-интерфейса
- **SQLAlchemy**: ORM для работы с базой данных
- **alembic**: для миграций базы данных
- **PostgreSQL**: система управления базами данных
- **ruff и Black**: для обеспечения качества кода
- **pytest**: для обеспечения работоспособности
- **Docker**: для контейнеризации приложения
- **uv**: быстрый Python пакетный менеджер

## Установка и запуск

### Предварительные требования

- Docker и Docker Compose
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) для управления зависимостями
- [just](https://github.com/casey/just) (опционально)

### Локальный запуск

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/TopNik073/kd-schedule.git
   cd kd-schedule
   ```
   
2. Создайте файл окружения и отредактируйте его, указав необходимые параметры подключения к БД.
   Пример его заполнения [здесь](https://github.com/TopNik073/kd-schedule/blob/main/.env.template) или более подробно [тут](https://github.com/TopNik073/kd-schedule/blob/main/src/core/config.py)

3. Установите зависимости:
   ```
   uv venv .venv
   .\.venv\Scripts\activate  # Для Windows
   uv pip install -r requirements.txt
   ```

4. Запустите приложение:
   + 4.1 Если установлен just:
   ```
   just app-start
   ```
   + 4.2 Если just НЕ установлен:
   ```
   uv run python -m src.main
   ```

### Запуск через Docker

Используйте Docker Compose для запуска приложения, предварительно настроив окружение
> Создайте файл окружения и отредактируйте его, указав необходимые параметры подключения к БД.
   Пример его заполнения [здесь](https://github.com/TopNik073/kd-schedule/blob/main/.env.template) или более подробно [тут](https://github.com/TopNik073/kd-schedule/blob/main/src/core/config.py)

+ С установленным just:
  ```
  just docker-start
  ```
+ Без just:
  ```
  docker compose up --build
  ```

## API Endpoints

### REST API

После запуска приложения ознакомиться можно [тут](http://localhost:8000/docs)

- **POST /api/v1/schedule**: Создание нового расписания
- **GET /api/v1/schedules**: Получение списка идентификаторов расписаний
- **GET /api/v1/schedule**: Получение информации о расписании по ID
- **GET /api/v1/next_takings**: Получение списка ближайших приёмов лекарств

### gRPC API

Сервис предоставляет следующие gRPC методы:

- **CreateSchedule**: Создание нового расписания
- **GetSchedulesIds**: Получение списка идентификаторов расписаний
- **GetSchedule**: Получение информации о расписании по ID
- **GetNextTakings**: Получение списка ближайших приёмов лекарств

## Руководство

### Структура проекта

Структура проекта была вдохновлена [сборником лучших практик FastAPI](https://github.com/zhanymkanov/fastapi-best-practices)

```
kd-schedule/
├── .github/
|   └── workflows             # GitHub Actions
├── alembic/
|   └──versions               # Миграции базы данных
├── src/
│   ├── api/
│   │   └── v1/
│   │       └── schedule/     # REST API endpoints, схемы, зависимости и сервис
│   ├── core/                 # Конфигурационные файлы и настройки
│   ├── database/             # Модели БД и соединения
│   ├── grpc_server/          # gRPC сервер и имплементация его методов
│   ├── repositories/         # Репозитории для работы с базой данных
|   └── main.py               # Точка входа
├── tests/                    # Тесты (unit и e2e)
├── protos/                   # Protobuf контракты
├── docs/                     # Контракты API для кодогенерации
└── README.md
```

### Команды доступные для just

```
Available recipes:
    default

    [app]
    app-start         # Start the application locally
    generate-schemas  # Generate schemas from openapi.yaml (codegeneration)

    [docker]
    docker-start      # Start the application in docker

    [linters]
    check             # Check code formatting with Black and ruff
    format            # Format code with Black
    uv-fix            # Fix code formatting with ruff

    [testing]
    test-all          # Run all tests (without coverage)
    test-all-coverage # Run all tests with coverage
    test-api          # Run e2e tests for API
    test-grpc         # Run e2e tests for grpc server
    test-next-takings # Run unit tests for next takings feature
```

## Тестирование

В проекте реализованы:

- Unit-тесты
- E2E тесты для REST API и gRPC интерфейсов
- Репорты с предоставлением покрытия

Запуск тестов

- Обычный запуск:

```
just test-all
```
+ С просмотром покрытия
```
just test-all-coverage
```

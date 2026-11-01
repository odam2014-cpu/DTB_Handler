# Инструкция по развертыванию DTB_Handler

## Описание

DTB_Handler — мультиплатформенный бот-фреймворк, работающий с Telegram, MAX Platform и ВКонтакте.

**Версия:** v.2.05

---

## Требования

| Компонент | Версия | Примечание |
|-----------|--------|------------|
| Python | 3.13+ | |
| ОС | Windows / Linux / macOS | |
| Доступ к интернету | Да | Для работы с API мессенджеров |

### Python-зависимости

| Пакет | Назначение |
|-------|------------|
| `python-dotenv` | Загрузка переменных окружения из `.env` |
| `pyTelegramBotAPI` (telebot) | Работа с Telegram Bot API |
| `vk_api` | Работа с ВКонтакте API |
| `requests` | HTTP-клиент для MAX Platform API |
| `beautifulsoup4` | Парсинг HTML (VK-бот) |
| `vobject` | Парсинг vCard (MAX-бот, контакты) |
| `pysocks` | SOCKS5-прокси для Telegram Bot API |

---

## Шаг 1. Клонирование репозитория

```bash
git clone <repository-url>
cd DTB_Handler
```

---

## Шаг 2. Создание виртуального окружения

```bash
# Создание окружения
python -m venv venv

# Активация (Windows — PowerShell)
.\venv\Scripts\Activate.ps1

# Активация (Windows — CMD)
venv\Scripts\activate.bat

# Активация (Linux / macOS)
source venv/bin/activate
```

---

## Шаг 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

> **Примечание:** Если файл `requirements.txt` отсутствует, создайте его:
> ```
> python-dotenv
> pyTelegramBotAPI
> vk_api
> requests
> ```

---

## Шаг 4. Настройка переменных окружения (.env)

Скопируйте шаблон и заполните токены:

```bash
# Windows
copy .env.example .env
# Linux / macOS
cp .env.example .env
```

Откройте файл `.env` и укажите актуальные токены:

| Переменная | Описание |
|------------|----------|
| `MAX_Main` | Токен основного бота MAX |
| `MAX_Second` | Токен второго бота MAX |
| `TLG_Main` | Токен основного Telegram-бота |
| `TLG_Second` | Токен второго Telegram-бота |
| `DTB_RECOVERY_TLG` | Токен Telegram-бота восстановления |
| `DTB_RECOVERY_MAX` | Токен MAX-бота восстановления |
| `VK_Main` | Токен ВКонтакте-бота |

> **Важно:** Файл `.env` находится в `.gitignore` — он не попадёт в репозиторий.

---

## Шаг 5. Настройка конфигурации

### DTB_Cfg.json

Определяет список ботов и параметры системы:

| Параметр | Описание | Значение по умолчанию |
|----------|----------|----------------------|
| `MaxApiBaseUrl` | URL API MAX Platform | `https://platform-api.max.ru/` |
| `DataBaseName` | Имя SQLite-базы | `DTB_DB.db` |
| `CheckPinCount` | Количество попыток PIN | `5` |
| `TokenLenght` | Длина токена | `6` |
| `TokenLifeTime` | Время жизни токена (сек) | `30` |
| `ChatLifeTime` | Время жизни чата (сек) | `180` |
| `ClearLifeTime` | Время очистки (сек) | `36000` |
| `Version` | Версия конфигурации | `v.2.05` |

### DTB_Api.cfg

Настройки HTTP-сервера для проверки токенов:

```json
{
    "ADDRESS": "127.0.0.1",
    "PORT": "9000"
}
```

HTTP-сервер предоставляет endpoint:

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/check_token` | Проверка токена пользователя |

**Пример запроса:**
```bash
curl -X POST http://127.0.0.1:9000/check_token \
  -H "Content-Type: application/json" \
  -d '{"user": "0000", "token": "123456", "respondent": "test"}'
```

**Ответ:**
```json
{"result": "ok"}    // токен валиден
{"result": "fail"}  // токен невалиден
```

---

## Шаг 6. Запуск

### Основной запуск

```bash
python DTB_Main.py
```

При запуске:
1. Загружается конфигурация из `DTB_Cfg.json`
2. Переменные окружения читаются из `.env`
3. Создаётся SQLite-база `DTB_DB.db` (таблицы `CHAT`, `MESSAGE`, `USER`)
4. Запускаются потоки для каждого бота из `BotList`
5. Запускается HTTP-сервер для API-проверки токенов

### Структура запускаемых ботов

| Тип | Название | Назначение |
|-----|----------|------------|
| `MAX` | MAX_Main | Основной бот MAX |
| `MAX` | MAX_Second | Второй бот MAX |
| `TLG` | TLG_Main | Основной Telegram-бот |
| `TLG` | TLG_Second | Второй Telegram-бот |
| `TLG_Recovery` | DTB_RECOVERY_TLG | Telegram-бот восстановления |
| `MAX_Recovery` | DTB_RECOVERY_MAX | MAX-бот восстановления |
| `VK` | VK_Main | ВКонтакте-бот |

---

## Шаг 7. Логирование

Логи автоматически записываются в папку `log/`:

- Формат имени файла: `YYYY-MM-DD.log`
- Формат записи:
  ```
  2026-11-01 18:30:00
  [Сообщение]
  [Дополнительно]
  ```

Папка `log/` находится в `.gitignore`.

---

## Структура проекта

```
DTB_Handler/
├── DTB_Main.py          # Точка входа
├── DTB_Start.py         # Инициализация ботов
├── DTB_Cfg.py           # Загрузка конфигурации
├── DTB_Cfg.json         # Конфигурация ботов
├── DTB_Api.py           # HTTP API для проверки токенов
├── DTB_Api.cfg          # Настройки HTTP-сервера
├── DTB_DB.py            # SQLite ORM
├── DTB_DB.sql           # DDL таблиц
├── DTB_DB.db            # База данных (создаётся автоматически)
├── DTB_Chat.py          # Менеджер сессий чата
├── DTB_User.py          # Менеджер пользователей
├── DTB_Token.py         # Менеджер временных токенов
├── DTB_Res.py           # Загрузка текстовых ресурсов
├── DTB_Log.py           # Логирование
├── DTB_Utils.py         # Утилиты (хэши, генерация токенов)
├── DTB_Kbrd.py          # PIN-клавиатура
├── DTB_Timer.py         # Фоновые задачи
├── .env                 # Переменные окружения (токены)
├── .env.example         # Шаблон .env
├── BOT/                 # Платформы мессенджеров
│   ├── DTB_Bot.py       # Базовый класс бота
│   ├── DTB_Bot_Tlg.py   # Telegram
│   ├── DTB_Bot_Max.py   # MAX Platform
│   ├── DTB_Bot_Vk.py    # ВКонтакте
│   └── ...
├── CM/                  # Command Modules
│   ├── DTB_C_Start.py   # /start, отмена
│   ├── DTB_C_Reg.py     # Регистрация
│   ├── DTB_C_Auth.py    # Авторизация
│   ├── DTB_C_Pass.py    # Смена пароля
│   ├── DTB_C_MainMenu.py# Главное меню
│   └── DTB_C_Token.py   # Получение токена
├── log/                 # Логи (создаётся автоматически)
└── image/               # Изображения
```

---

## Решение проблем

### Ошибка: `ModuleNotFoundError`

Убедитесь, что виртуальное окружение активировано и зависимости установлены:
```bash
pip install -r requirements.txt
```

### Ошибка: `Token not found`

Проверьте, что файл `.env` существует и содержит нужные токены. Формат ключей должен точно соответствовать именам в `DTB_Cfg.json` (`BotList[].Name`).

### Ошибка: `sqlite3.OperationalError`

Убедитесь, что у процесса есть права на запись в рабочую директорию. База данных `DTB_DB.db` создаётся автоматически при первом запуске.

### HTTP-сервер не запускается

Порт 9000 может быть занят. Измените порт в `DTB_Api.cfg`:
```json
{
    "ADDRESS": "127.0.0.1",
    "PORT": "9001"
}
```

---

## Бэкап

Для сохранения состояния системы:

1. Скопируйте файл `DTB_DB.db` — в нём хранятся все данные пользователей и чатов
2. Сохраните файл `.env` — в нём хранятся токены ботов
3. Файл `DTB_Cfg.json` можно хранить в репозитории

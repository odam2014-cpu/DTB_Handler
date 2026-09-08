# DTB_Handler — Архитектура (C4 Model)

## Level 1: System Context

Система в контексте внешних акторов и зависимостей.

```mermaid
graph TB
    subgraph "Внешние системы"
        TG_API[Telegram Bot API]
        MAX_API[MAX Platform API]
        VK_API[VK API]
        SQLITE[(SQLite DB<br/>на диске)]
    end

    subgraph "Пользователи"
        END_USER[Конечный пользователь<br/>Телеграм/MAX/VK]
        ADMIN[Администратор<br/>Управление пользователями]
    end

    END_USER -->|Отправляет сообщения| DTB_SYSTEM[DTB_Handler]
    ADMIN -->|Управление| DTB_SYSTEM
    DTB_SYSTEM -->|HTTP/Proxy| TG_API
    DTB_SYSTEM -->|HTTPS REST| MAX_API
    DTB_SYSTEM -->|HTTPS REST| VK_API
    DTB_SYSTEM -->|SQLite| SQLITE
```

**Описание:**
- **DTB_Handler** — мультиплатформенный бот-фреймворк
- **Пользователи** — взаимодействуют через мессенджеры
- **Внешние API** — Telegram, MAX, VK для отправки/получения сообщений
- **SQLite** — локальная база данных

---

## Level 2: Containers

Технологические контейнеры и потоки данных между ними.

```mermaid
graph TB
    subgraph "Python Process"
        subgraph "Telegram Container"
            TLG_BOT[DTB_Bot_Tlg.py<br/>pyTelegramBotAPI<br/>SOCKS5 Proxy]
        end

        subgraph "MAX Container"
            MAX_BOT[DTB_Bot_Max.py<br/>requests + REST API<br/>platform-api.max.ru]
        end

        subgraph "VK Container"
            VK_BOT[DTB_Bot_Vk.py<br/>vk_api<br/>long-poll/Webhook]
        end

        subgraph "Core Container"
            CFG[DTB_Cfg.py<br/>JSON Config]
            CHAT[DTB_Chat.py<br/>Session Manager]
            USER[DTB_User.py<br/>User Manager]
            TOKEN[DTB_Token.py<br/>Token Manager]
            CM[Command Modules<br/>CM/DTB_C_*.py]
            RES[DTB_Res.py<br/>Messages & Texts]
            LOG[DTB_Log.py<br/>Logging]
            UTILS[DTB_Utils.py<br/>Hash + Token Gen]
        end

        subgraph "Data Container"
            DB[DTB_DB.py<br/>SQLite ORM<br/>DTB_DB.db]
        end

        subgraph "Scheduler Container"
            TIMER[DTB_Timer.py<br/>Background Tasks]
        end
    end

    TLG_BOT -->|gate()| CHAT
    MAX_BOT -->|gate()| CHAT
    VK_BOT -->|gate()| CHAT
    CHAT -->|CRUD| DB
    CHAT -->|auth| USER
    CHAT -->|token| TOKEN
    CHAT -->|route| CM
    CHAT -->|texts| RES
    USER -->|hash| UTILS
    TIMER -->|cleanup| DB
    TIMER -->|ping| TLG_BOT
    TIMER -->|ping| MAX_BOT
    CFG -->|config| CHAT
```

**Описание контейнеров:**

| Контейнер | Технология | Назначение |
|-----------|-----------|------------|
| Telegram | pyTelegramBotAPI | Обработка событий Telegram, SOCKS5 proxy |
| MAX | requests + REST | Обработка событий MAX Platform |
| VK | vk_api | Обработка событий ВКонтакте |
| Core | Python 3.x | Логика сессий, пользователей, токенов |
| Data | SQLite | Персистентное хранение |
| Scheduler | threading.Timer | Фоновые задачи (очистка, пинг) |
| Config | JSON | Конфигурация ботов и параметров |

---

## Level 3: Components

Детальная разбивка ключевых контейнеров.

### 3.1 Container: Core

```mermaid
graph TB
    subgraph "Core Components"
        CHAT[c_chat<br/>DTB_Chat.py<br/>Сессия чата]
        USER[c_User<br/>DTB_User.py<br/>Пользователь]
        TOKEN[c_token<br/>DTB_Token.py<br/>Временный токен]
        CM_START[DTB_C_Start<br/>/start, отмена]
        CM_REG[DTB_C_Reg<br/>Регистрация]
        CM_AUTH[DTB_C_Auth<br/>Авторизация]
        CM_PASS[DTB_C_Pass<br/>Смена пароля]
        CM_MENU[DTB_C_MainMenu<br/>Главное меню]
        CM_TOKEN[DTB_C_Token<br/>Получение токена]
        RES[DTB_Res<br/>Ресурсы]
        LOG[DTB_Log<br/>Логирование]
        UTILS[DTB_Utils<br/>Утилиты]
        KBRD[DTB_Kbrd<br/>PIN-клавиатура]
    end

    CHAT -->|create| USER
    CHAT -->|create| TOKEN
    CHAT -->|route| CM_START
    CHAT -->|route| CM_REG
    CHAT -->|route| CM_AUTH
    CHAT -->|route| CM_PASS
    CHAT -->|route| CM_MENU
    CHAT -->|route| CM_TOKEN
    CHAT -->|get text| RES
    CHAT -->|write| LOG
    USER -->|hash password| UTILS
    TOKEN -->|generate token| UTILS
    CM_AUTH -->|PIN input| KBRD
    CM_PASS -->|PIN input| KBRD
```

### 3.2 Container: Telegram

```mermaid
graph TB
    subgraph "Telegram Components"
        BASE[c_Bot<br/>DTB_Bot.py<br/>Базовый класс]
        TLG[c_BotTelegram<br/>DTB_Bot_Tlg.py<br/>Telegram бот]
        TLG_CHAT[c_BotTelegramChat<br/>DTB_Bot_Tlg_Chat.py<br/>Основной чат]
        TLG_REC[c_BotTelegramRecovery<br/>DTB_Bot_Tlg_Recovery.py<br/>Восстановление]
        BTN_TLG[DTB_Btn_Tlg.py<br/>Inline кнопки TLG]
    end

    TLG_CHAT -->|extends| TLG
    TLG_REC -->|extends| TLG
    TLG -->|extends| BASE
    TLG -->|create| BTN_TLG
```

### 3.3 Container: MAX

```mermaid
graph TB
    subgraph "MAX Components"
        BASE[c_Bot<br/>DTB_Bot.py<br/>Базовый класс]
        MAX_API[c_BotApiMax<br/>DTB_Bot_Max.py<br/>API обёртка]
        MAX_BOT[c_BotMax<br/>DTB_Bot_Max.py<br/>MAX бот]
        MAX_CHAT[c_BotMaxChat<br/>DTB_Bot_Max_Chat.py<br/>Основной чат]
        MAX_REC[c_BotMaxRecovery<br/>DTB_Bot_Max_Recovery.py<br/>Восстановление]
        BTN_MAX[DTB_Btn_Max.py<br/>Inline кнопки MAX]
    end

    MAX_CHAT -->|extends| MAX_BOT
    MAX_REC -->|extends| MAX_BOT
    MAX_BOT -->|extends| BASE
    MAX_BOT -->|uses| MAX_API
    MAX_BOT -->|create| BTN_MAX
```

### 3.4 Container: Data

```mermaid
graph TB
    subgraph "Data Components"
        DB[c_DB<br/>DTB_DB.py<br/>SQLite слой]
        DBFILE[DTB_DB.db<br/>База данных]

        subgraph "Таблицы"
            T_CHAT[CHAT<br/>ID, NAME, GID, USER_ID]
            T_USER[USER<br/>ID, PASSWORD, RECOVERY]
            T_MESS[MESSAGE<br/>CHAT_ID, MESS_ID, LEVEL, LASTTIME]
        end
    end

    DB -->|read/write| DBFILE
    DB -->|CRUD| T_CHAT
    DB -->|CRUD| T_USER
    DB -->|CRUD| T_MESS
```

---

## Level 4: Code (Class Diagram)

Ключевые классы и их отношения.

```mermaid
classDiagram
    class c_Bot {
        +string name
        +string token
        +dict options
        +gate(name, chat, mess, comm, text, phone)
        +build_message(key, ins)
    }

    class c_BotTelegram {
        +TeleBot Bot
        +handler_message()
        +handler_call()
        +clear_button(id, ms)
        +start()
        +delete_message(id, ms)
        +send_message(id, key, ins, btn)
        +edit_message(id, ms, key, ins, btn)
    }

    class c_BotMax {
        +c_BotApiMax Bot
        +start()
        +delete_message(id, ms)
        +send_message(id, key, ins, btn)
        +edit_message(ms, id, key, ins, btn)
    }

    class c_chat {
        +string name
        +bot
        +int id
        +string gid
        +c_User user
        +dict list_mess
        +int level
        +string step
        +bool auth
        +create_token()
        +gate(mess)
        +send_message(key, ins, btn, lvl)
        +edit_message(id, key, ins, btn, lvl)
        +delete_message(ms)
        +clear_mess(lv, isrev)
    }

    class c_User {
        +string id
        +string password
        +string recovery
        +c_token current_token
        +set_user(recovery, password)
        +check_password(input)
        +set_token(token)
    }

    class c_token {
        +c_chat ch
        +string token
        +bool enable
        +threading.Timer timer
        +close()
        +check(tk)
    }

    class c_DB {
        +sqlite3 conn
        +exec(sql)
        +get_chat(nm, ch)
        +get_user(id)
        +add_user(id)
        +upd_user(id, rec, pass)
        +del_user(id)
    }

    c_BotTelegram --|> c_Bot : extends
    c_BotMax --|> c_Bot : extends
    c_chat o-- c_Bot : has
    c_chat o-- c_User : has
    c_chat o-- c_token : has
    c_User o-- c_token : has
    c_User --> c_DB : queries
    c_chat --> c_DB : queries
    c_token --> c_DB : none (memory only)
```

---

## Потоки данных

### 4.1 Входящее сообщение

```mermaid
sequenceDiagram
    participant U as User
    participant P as Platform (TLG/MAX/VK)
    participant B as c_Bot
    participant C as c_chat
    participant CM as Command Module
    participant DB as c_DB

    U->>P: отправляет сообщение
    P->>B: event/hook
    B->>B: gate()
    B->>C: find/create c_chat
    C->>C: gate(mess)
    C->>CM: route by comm
    CM->>C: send_message()
    C->>DB: save message
    C->>B: send_message()
    B->>P: API call
    P->>U: сообщение
```

### 4.2 Регистрация пользователя

```mermaid
sequenceDiagram
    participant U as User
    participant C as c_chat
    participant CM as CM_DTB_C_Reg
    participant DB as c_DB
    participant U2 as c_User

    U->>C: /start
    C->>CM: Registration
    CM->>C: send_message("Registration")
    U->>C: контакт (phone)
    C->>CM: ContactHandler
    CM->>DB: check user
    alt user exists
        DB->>CM: user found
        CM->>C: send_message("Auth")
    else user new
        DB->>CM: no user
        CM->>U2: create new user
        U2->>DB: INSERT INTO USER
        CM->>C: send_message("Password")
    end
    U->>C: пароль
    C->>CM: PasswordFirstHandler
    CM->>U2: set_user()
    U2->>DB: UPDATE USER
    CM->>C: send_message("Token")
    C->>CM: create_token()
    CM->>U: токен
```

---

## Словарь компонентов

| Компонент | Файл | Роль |
|-----------|------|------|
| **c_Bot** | BOT/DTB_Bot.py | Абстрактный базовый класс бота |
| **c_BotTelegram** | BOT/DTB_Bot_Tlg.py | Telegram-бот (pyTelegramBotAPI) |
| **c_BotMax** | BOT/DTB_Bot_Max.py | MAX-бот (REST API) |
| **c_chat** | DTB_Chat.py | Сессия чата, центральный роутер |
| **c_User** | DTB_User.py | Модель пользователя |
| **c_token** | DTB_Token.py | Временный токен с таймером |
| **c_DB** | DTB_DB.py | SQLite ORM, потокобезопасный |
| **CM_*** | CM/DTB_C_*.py | Обработчики команд |
| **DTB_Res** | DTB_Res.py | Загрузка текстов из JSON |
| **DTB_Timer** | DTB_Timer.py | Фоновые задачи (очистка, пинг) |

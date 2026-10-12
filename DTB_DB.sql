--
-- Файл сгенерирован с помощью SQLiteStudio v3.4.17 в Пн окт 12 21:01:08 2026
--
-- Использованная кодировка текста: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Таблица: CHAT
CREATE TABLE IF NOT EXISTS CHAT (
    ID      INTEGER,
    USER_ID TEXT    DEFAULT "",
    NAME    TEXT,
    GID     TEXT    AS (NAME || ID) STORED
);


-- Таблица: MESSAGE
CREATE TABLE IF NOT EXISTS MESSAGE (
    CHAT_ID  TEXT,
    MESS_ID  TEXT,
    LEVEL    INTEGER,
    LASTTIME INTEGER DEFAULT (strftime('%s', 'now') ) 
);


-- Таблица: USER
CREATE TABLE IF NOT EXISTS USER (
    ID       TEXT    PRIMARY KEY,
    PASSWORD TEXT    DEFAULT "",
    RECOVERY TEXT    DEFAULT "",
    BLOCK_DT INTEGER DEFAULT (0),
    BLOCK_CN INTEGER DEFAULT (0),
    BLOCK_AT INTEGER DEFAULT (0) 
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;

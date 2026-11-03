PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS RequestHistory;
DROP TABLE IF EXISTS Comments;
DROP TABLE IF EXISTS Requests;
DROP TABLE IF EXISTS Categories;
DROP TABLE IF EXISTS Statuses;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Roles;

CREATE TABLE Roles (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE Users (
    id INTEGER PRIMARY KEY,
    role_id INTEGER NOT NULL,
    full_name TEXT NOT NULL CHECK (length(trim(full_name)) > 0),
    login TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES Roles(id) ON DELETE RESTRICT
);

CREATE TABLE Statuses (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (name IN ('Новая', 'В работе', 'Выполнена', 'Закрыта'))
);

CREATE TABLE Categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0),
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE Requests (
    id INTEGER PRIMARY KEY,
    number TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    description TEXT NOT NULL CHECK (length(trim(description)) > 0),
    applicant_id INTEGER NOT NULL,
    executor_id INTEGER,
    category_id INTEGER NOT NULL,
    status_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TEXT,
    FOREIGN KEY (applicant_id) REFERENCES Users(id) ON DELETE RESTRICT,
    FOREIGN KEY (executor_id) REFERENCES Users(id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES Categories(id) ON DELETE RESTRICT,
    FOREIGN KEY (status_id) REFERENCES Statuses(id) ON DELETE RESTRICT
);

CREATE TABLE Comments (
    id INTEGER PRIMARY KEY,
    request_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    body TEXT NOT NULL CHECK (length(trim(body)) > 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES Requests(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES Users(id) ON DELETE RESTRICT
);

CREATE TABLE RequestHistory (
    id INTEGER PRIMARY KEY,
    request_id INTEGER NOT NULL,
    old_status_id INTEGER,
    new_status_id INTEGER NOT NULL,
    old_executor_id INTEGER,
    new_executor_id INTEGER,
    changed_by INTEGER NOT NULL,
    changed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    note TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (request_id) REFERENCES Requests(id) ON DELETE CASCADE,
    FOREIGN KEY (old_status_id) REFERENCES Statuses(id) ON DELETE RESTRICT,
    FOREIGN KEY (new_status_id) REFERENCES Statuses(id) ON DELETE RESTRICT,
    FOREIGN KEY (old_executor_id) REFERENCES Users(id) ON DELETE RESTRICT,
    FOREIGN KEY (new_executor_id) REFERENCES Users(id) ON DELETE RESTRICT,
    FOREIGN KEY (changed_by) REFERENCES Users(id) ON DELETE RESTRICT
);

CREATE INDEX idx_requests_status ON Requests(status_id);
CREATE INDEX idx_requests_category ON Requests(category_id);
CREATE INDEX idx_requests_applicant ON Requests(applicant_id);
CREATE INDEX idx_requests_executor ON Requests(executor_id);
CREATE INDEX idx_comments_request ON Comments(request_id);
CREATE INDEX idx_history_request ON RequestHistory(request_id, changed_at);

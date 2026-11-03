-- Q01: список заявок с категорией, статусом и исполнителем (JOIN).
SELECT r.number, r.title, c.name AS category, s.name AS status, COALESCE(u.full_name, 'Не назначен') AS executor
FROM Requests AS r
JOIN Categories AS c ON c.id = r.category_id
JOIN Statuses AS s ON s.id = r.status_id
LEFT JOIN Users AS u ON u.id = r.executor_id
ORDER BY r.created_at DESC, r.id DESC;

-- Q02: новые заявки (WHERE).
SELECT number, title, created_at
FROM Requests
WHERE status_id = (SELECT id FROM Statuses WHERE name = 'Новая')
ORDER BY created_at;

-- Q03: заявки на оборудование в работе (два JOIN и составной WHERE).
SELECT r.number, r.title, u.full_name AS executor
FROM Requests AS r
JOIN Categories AS c ON c.id = r.category_id
JOIN Statuses AS s ON s.id = r.status_id
LEFT JOIN Users AS u ON u.id = r.executor_id
WHERE c.name = 'Оборудование' AND s.name = 'В работе';

-- Q04: количество комментариев по заявкам (JOIN, GROUP BY, HAVING).
SELECT r.number, r.title, COUNT(cm.id) AS comments_count
FROM Requests AS r
LEFT JOIN Comments AS cm ON cm.request_id = r.id
GROUP BY r.id, r.number, r.title
HAVING COUNT(cm.id) >= 1
ORDER BY comments_count DESC, r.number;

-- Q05: поиск по номеру или части темы (WHERE и LIKE).
SELECT number, title
FROM Requests
WHERE number LIKE '%00001%' OR lower(title) LIKE '%принтер%';

-- Q06: история изменений с именами участников и статусами (несколько JOIN).
SELECT h.id, r.number, COALESCE(os.name, '—') AS old_status, ns.name AS new_status,
       u.full_name AS changed_by, h.changed_at
FROM RequestHistory AS h
JOIN Requests AS r ON r.id = h.request_id
LEFT JOIN Statuses AS os ON os.id = h.old_status_id
JOIN Statuses AS ns ON ns.id = h.new_status_id
JOIN Users AS u ON u.id = h.changed_by
ORDER BY h.changed_at, h.id;

-- Дополнительный INSERT для проверки изменения данных.
INSERT INTO Comments (request_id, author_id, body, created_at)
VALUES (2, 5, 'Уточнение: ошибка возникает после обновления конфигурации.', '2026-11-03 12:00:00');

-- Временные записи для безопасной проверки INSERT и DELETE.
INSERT INTO Categories (name, description)
VALUES ('Тестовая категория', 'Временная запись для проверки SQL');

INSERT INTO Requests (number, title, description, applicant_id, category_id, status_id)
SELECT 'REQ-2026-99999', 'Временная тестовая заявка', 'Проверка вставки и последующего удаления.', 5, c.id, 1
FROM Categories AS c
WHERE c.name = 'Тестовая категория';

-- UPDATE 1: назначение исполнителя и перевод новой заявки в работу.
UPDATE Requests
SET executor_id = 3, status_id = 2, updated_at = '2026-11-03 12:05:00'
WHERE id = 2 AND status_id = 1;

INSERT INTO RequestHistory (request_id, old_status_id, new_status_id, old_executor_id, new_executor_id, changed_by, changed_at, note)
VALUES (2, 1, 2, NULL, 3, 2, '2026-11-03 12:05:00', 'Назначен Иван Петров после уточнения');

-- UPDATE 2: закрытие выполненной заявки после проверки результата.
UPDATE Requests
SET status_id = 4, closed_at = '2026-11-03 12:10:00', updated_at = '2026-11-03 12:10:00'
WHERE id = 3 AND status_id = 3;

INSERT INTO RequestHistory (request_id, old_status_id, new_status_id, old_executor_id, new_executor_id, changed_by, changed_at, note)
VALUES (3, 3, 4, 4, 4, 5, '2026-11-03 12:10:00', 'Результат VPN подтверждён заявителем');

-- DELETE 1: удаление добавленного уточнения после проверки.
DELETE FROM Comments
WHERE request_id = 2 AND body = 'Уточнение: ошибка возникает после обновления конфигурации.';

-- DELETE 2: очистка временной заявки и её категории.
DELETE FROM Requests WHERE number = 'REQ-2026-99999';
DELETE FROM Categories WHERE name = 'Тестовая категория';

-- Q07: итоговые агрегаты после DML-операций.
SELECT
    (SELECT COUNT(*) FROM Requests) AS requests_total,
    (SELECT COUNT(*) FROM Requests WHERE status_id = 4) AS closed_total,
    (SELECT COUNT(*) FROM Comments) AS comments_total,
    (SELECT COUNT(*) FROM RequestHistory) AS history_total;

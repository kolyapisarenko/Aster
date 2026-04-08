CREATE TABLE savings_new (
    user_id INTEGER NOT NULL,
    event_date DATE NOT NULL,
    amount INT NOT NULL,
    balance_at_moment REAL NOT NULL,
    PRIMARY KEY (user_id, event_date)
);
INSERT INTO savings_new (user_id, event_date, amount, balance_at_moment)
SELECT user_id,
    event_date,
    amount,
    balance_at_moment
FROM savings;
DROP TABLE savings;
ALTER TABLE savings_new
    RENAME TO savings;
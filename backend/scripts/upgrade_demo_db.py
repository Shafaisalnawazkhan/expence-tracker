import sqlite3
from pathlib import Path

database = Path(__file__).parents[1] / "finance.db"
connection = sqlite3.connect(database)
transaction_columns = {row[1] for row in connection.execute("pragma table_info(transactions)")}
user_columns = {row[1] for row in connection.execute("pragma table_info(users)")}
if "is_recurring" not in transaction_columns:
    connection.execute("alter table transactions add column is_recurring boolean not null default 0")
if "currency" not in transaction_columns:
    connection.execute("alter table transactions add column currency varchar(3) not null default 'INR'")
if "app_lock_hash" not in user_columns:
    connection.execute("alter table users add column app_lock_hash varchar(255)")
if "bank_account_id" not in transaction_columns:
    connection.execute("alter table transactions add column bank_account_id integer")
if "external_id" not in transaction_columns:
    connection.execute("alter table transactions add column external_id varchar(100)")
connection.execute("create table if not exists bank_accounts (id integer primary key, user_id integer not null, provider varchar(30) not null default 'demo', bank_name varchar(100) not null, account_name varchar(100) not null, account_type varchar(30) not null, account_mask varchar(4) not null, balance float not null default 0, currency varchar(3) not null default 'INR', status varchar(20) not null default 'connected', last_synced_at datetime, created_at datetime not null, foreign key(user_id) references users(id))")
bank_columns = {row[1] for row in connection.execute("pragma table_info(bank_accounts)")}
if "consent_request_id" not in bank_columns:
    connection.execute("alter table bank_accounts add column consent_request_id varchar(100)")
connection.commit()
print("Demo database schema is current.")

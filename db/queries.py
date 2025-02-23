

create_table_query = """
    CREATE TABLE IF NOT EXISTS products (
        id          SERIAL PRIMARY KEY,
        title       VARCHAR(64) NOT NULL,
        sizes       JSONB NOT NULL,
        comb        INT NOT NULL,
        details     TEXT,
        post_link   TEXT NOT NULL,
        post_id     TEXT NOT NULL,
        created_at  TIMESTAMP DEFAULT current_timestamp
    )
"""

# the sizes field represent the size and quantity of each size like this [(size, quantity), ...]
insert_item_query = """
    INSERT INTO products (title, details, sizes, comb, post_link, post_id) VALUES ($1, $2, $3::jsonb, $4, $5, $6)
"""

delete_item_query = """
    DELETE FROM products WHERE post_id = $1
"""


update_item_query = """
    UPDATE products SET quantity = $1 WHERE p
"""


fetch_items_query = """
    SELECT title, sizes, comb, details, post_link, post_id, TO_CHAR(created_at, 'YYYY/MM/DD HH:MM:SS') AS created_at FROM products
"""
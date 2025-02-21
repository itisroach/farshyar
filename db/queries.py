

create_table_query = """
    CREATE TABLE IF NOT EXISTS products (
        id          SERIAL PRIMARY KEY,
        title       VARCHAR(64) NOT NULL,
        quantity    INT NOT NULL,
        details     TEXT NOT NULL,
        post_link   TEXT NOT NULL,
        post_id     TEXT NOT NULL,
        created_at  TIMESTAMP DEFAULT current_timestamp
    )
"""

insert_item_query = """
    INSERT INTO products (id, title, quantity, details, post_link, post_id) VALUES ($1, $2, $3, $4, $5, $6)
"""

delete_item_query = """
    DELETE FROM products WHERE post_id = $1
"""


update_item_query = """
    UPDATE products SET quantity = $1 WHERE p
"""


fetch_items_query = """
    SELECT (title, quantity, details, post_link, post_id, created_at) FROM products
"""
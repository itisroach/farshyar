

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



delete_item_query = """
    DELETE FROM products WHERE post_id = $1
"""


update_item_query = """
    UPDATE products SET quantity = $1 WHERE p
"""
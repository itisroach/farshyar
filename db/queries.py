

create_table_query = """
    CREATE TABLE IF NOT EXISTS products (
        id          SERIAL PRIMARY KEY,
        title       VARCHAR(256) NOT NULL,
        sizes       JSONB NOT NULL,
        comb        INT NOT NULL,
        details     TEXT,
        post_link   TEXT NOT NULL,
        post_id     TEXT NOT NULL,
        channel_id  TEXT NOT NULL,
        images      TEXT[],
        created_at  TIMESTAMP DEFAULT current_timestamp
    )
"""

create_images_table_query = """
    CREATE TABLE IF NOT EXISTS images (
        id       SERIAL PRIMARY KEY,
        url      TEXT NOT NULL,
        product  INT NOT NULL,
        CONSTRAINT fk_product FOREIGN KEY(product) REFERENCES products(id)
    )
"""

# the sizes field represent the size and quantity of each size like this [(size, quantity), ...]
insert_item_query = """
    INSERT INTO products (title, details, sizes, comb, post_link, post_id, channel_id, images) VALUES ($1, $2, $3::jsonb, $4, $5, $6, $7, $8)
"""


fetch_items_to_remove = """
    SELECT (channel_id, post_id) FROM products
"""

delete_item_query = """
    DELETE FROM products WHERE channel_id = $1 AND post_id = $2 
"""


update_item_query = """
    UPDATE products SET 
    title=$1, details=$2, sizes=$3, comb=$4
    WHERE channel_id = $5 AND post_id = $6
"""


fetch_items_query = """
    SELECT 
        id,
        title, 
        sizes, 
        comb, 
        details, 
        post_link, 
        post_id, 
        channel_id,
        images,
        TO_CHAR(created_at, 'YYYY/MM/DD HH:MM:SS') AS created_at 

    FROM products
"""
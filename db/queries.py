create_table_query = """
    CREATE TABLE IF NOT EXISTS products (
        id               INT AUTO_INCREMENT PRIMARY KEY,
        title            VARCHAR(256) NOT NULL,
        sizes            JSON NOT NULL,
        comb             INT NOT NULL,
        details          TEXT,
        post_link        TEXT NOT NULL,
        post_id          VARCHAR(100) NOT NULL,
        channel_id       VARCHAR(100) NOT NULL,
        channel_posts_id JSON,
        created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""

create_images_table_query = """
    CREATE TABLE IF NOT EXISTS images(
        id          INT PRIMARY KEY AUTO_INCREMENT,
        product_id  INT,
        filename    TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    );
"""


insert_item_query = """
    INSERT INTO products (title, details, sizes, comb, post_link, post_id, channel_id, channel_posts_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
"""

insert_images_query = """
    INSERT INTO images (product_id, filename) VALUES (%s, %s);
"""

fetch_items_to_remove = """
    SELECT channel_id, post_id, channel_posts_id FROM products;
"""


fetch_images_to_remove = """
    SELECT filename FROM images WHERE product_id = (SELECT id FROM products WHERE post_id = %s AND channel_id = %s)
"""

delete_item_query = """
    DELETE FROM products WHERE channel_id = %s AND post_id = %s;
"""

update_item_query = """
    UPDATE products SET 
    title=%s, details=%s, sizes=%s, comb=%s
    WHERE channel_id = %s AND post_id = %s;
"""

returning_update_query = """
    SELECT channel_posts_id FROM products WHERE channel_id = %s AND post_id = %s
"""

fetch_items_query = """
    SELECT 
        p.id,
        p.title, 
        p.sizes, 
        p.comb,
        p.details, 
        p.post_link, 
        p.post_id, 
        p.channel_id,
        JSON_ARRAYAGG(i.filename) AS images,
        DATE_FORMAT(p.created_at, '%Y/%m/%d %H:%i:%s') AS created_at 
    FROM products p
    LEFT JOIN images i ON p.id = i.product_id
    GROUP BY p.id;
"""

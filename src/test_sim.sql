
CREATE DATABASE IF NOT EXISTS TEST;
USE TEST;
CREATE FUNCTION image_sim RETURNS REAL SONAME 'sim_api.so';


CREATE TABLE images (
    img_name varchar(255)
);

INSERT INTO images (img_name)
VALUES ("/mysqludf/img.png"),
       ("/mysqludf/cat.jpeg"),
       ("/mysqludf/dog.jpeg");

SELECT * FROM images;
SELECT img_name, image_sim(img_name, './img.png') AS sim FROM images;
SELECT img_name FROM images WHERE image_sim(img_name, './img.png') > 0.8;



DROP DATABASE TEST;

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
-- SELECT img_name, image_sim(img_name, './img.png') AS sim FROM images;
-- SELECT img_name FROM images WHERE image_sim(img_name, './img.png') > 0.8;

-- LPIPS, PSNR: the smaller, the better
-- SSIM: the larger, the better
-- SELECT img_name, image_sim(img_name, './img.png', 'LPIPS') AS Sim FROM images;
-- SELECT img_name, image_sim(img_name, './img.png', 'PSNR') AS Sim_PSNR FROM images;
SELECT img_name, image_sim(img_name, './n02099601_5.JPEG', 'SSIM') AS Sim_SSIM FROM images;
-- SELECT img_name, image_sim(img_name, 'A cat') AS Sim FROM images WHERE image_sim(img_name, 'A cat') > 0.25;



DROP DATABASE TEST;
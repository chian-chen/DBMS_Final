CREATE DATABASE demoImageDB;
use demoImageDB;

-- User Define Function 
CREATE FUNCTION image_sim RETURNS REAL SONAME 'sim_api.so';
CREATE  FUNCTION clip RETURNS STRING SONAME 'clip_api.so';

-- Create Table
CREATE TABLE image_table (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    img_path VARCHAR(255) NOT NULL,
    img_type1 int DEFAULT(-1),
    img_type2 int DEFAULT(-1),
    img_type3 int DEFAULT(-1),
    ground_truth int DEFAULT(-1)
);

-- Some Procedure, Trigger, Function
DELIMITER //
CREATE PROCEDURE SplitString(
    IN input_string VARCHAR(255),
    OUT part1 VARCHAR(255),
    OUT part2 VARCHAR(255),
    OUT part3 VARCHAR(255)
)
BEGIN
    -- Extract the first part
    SET part1 = REPLACE(SUBSTRING_INDEX(input_string, '_', 1), '$', '');
    
    -- Extract the second part by removing the first part and extracting the next segment
    SET part2 = SUBSTRING_INDEX(SUBSTRING_INDEX(input_string, '_', 2), '_', -1);
    
    -- Extract the third part by removing the first two parts and extracting the next segment
    SET part3 = REPLACE(SUBSTRING_INDEX(SUBSTRING_INDEX(input_string, '_', 3), '_', -1), '$', '');
END //
DELIMITER ;


DELIMITER //
CREATE TRIGGER AfterImageInsert
BEFORE INSERT ON image_table
FOR EACH ROW
BEGIN
    -- Calling the 'clip' function with the 'path' column of the new row and storing the result
    SET @result = clip(NEW.img_path);
    CALL SplitString(@result, @part1, @part2, @part3);
    
    SET NEW.img_type1 = CONVERT(@part1, UNSIGNED INTEGER);
    SET NEW.img_type2 = CONVERT(@part2, UNSIGNED INTEGER);
    SET NEW.img_type3 = CONVERT(@part3, UNSIGNED INTEGER);
END //

DELIMITER ;


DELIMITER $$
CREATE PROCEDURE fastest_sim(
IN input_image VARCHAR(255))
BEGIN
    SET @result = clip(input_image);
    CALL SplitString(@result, @c1, @c2, @c3);
    SELECT ground_truth, img_path, image_sim(img_path, input_image) AS sim FROM image_table 
    WHERE img_type1 IN (@c1, @c2, @c3) ORDER BY sim DESC;   
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE faster_sim(
IN input_image VARCHAR(255))
BEGIN
    SET @result = clip(input_image);
    CALL SplitString(@result, @c1, @c2, @c3);
    SELECT ground_truth, img_path, image_sim(img_path, input_image) AS sim FROM image_table 
    WHERE (img_type1 IN (@c1, @c2, @c3) OR img_type2 IN (@c1, @c2, @c3)) ORDER BY sim DESC; 
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE fast_sim(
IN input_image VARCHAR(255))
BEGIN
    SET @result = clip(input_image);
    CALL SplitString(@result, @c1, @c2, @c3);
    SELECT ground_truth, img_path, image_sim(img_path, input_image) AS sim FROM image_table 
    WHERE (img_type1 IN (@c1, @c2, @c3) OR img_type2 IN (@c1, @c2, @c3) OR img_type3 IN (@c1, @c2, @c3))
    ORDER BY sim DESC;  
END$$
DELIMITER ;

-- DEMO
-- Image path should be replaced to the path in your own system

-- insert an image and show its auto-tagging results
INSERT INTO image_table (img_path) VALUES ('/mysqludf/imgs/n02124075/n02124075_428.JPEG'); 
SELECT * FROM image_table;

-- insert some images to show other functions
INSERT INTO image_table (img_path) VALUES ('/mysqludf/imgs/n02124075/n02124075_1183.JPEG'); 
INSERT INTO image_table (img_path) VALUES ('/mysqludf/imgs/n01833805/n01833805_169.JPEG'); 

-- Similarity Search by another image
SELECT img_path, image_sim(img_path, '/mysqludf/imgs/n02124075/n02124075_1183.JPEG') AS sim FROM image_table;

-- Setting a real number threshold
SELECT img_path FROM image_table WHERE image_sim(img_path, '/mysqludf/imgs/n02124075/n02124075_1183.JPEG') > 0.8;

-- use text to search
SELECT img_path, image_sim(img_path, 'A cat') AS Sim FROM image_table WHERE image_sim(img_path, 'A cat') > 0;

-- More Similarity Algorithm
SELECT img_path, image_sim(img_path, '/mysqludf/imgs/n02124075/n02124075_1183.JPEG', 'LPIPS') AS Sim_LPIPS FROM image_table;
SELECT img_path, image_sim(img_path, '/mysqludf/imgs/n02124075/n02124075_1183.JPEG', 'PSNR') AS Sim_PSNR FROM image_table;
SELECT img_path, image_sim(img_path, '/mysqludf/imgs/n02124075/n02124075_1183.JPEG', 'SSIM') AS Sim_SSIM FROM image_table;

-- Large Data Experiments are shown in a python notebook named experiments.ipynb

-- DROP DATABASE demoImageDB;
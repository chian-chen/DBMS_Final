
USE imageDB;

DELIMITER //
CREATE PROCEDURE SplitString(
    IN input_string VARCHAR(255),
    OUT part1 VARCHAR(255),
    OUT part2 VARCHAR(255),
    OUT part3 VARCHAR(255)
)
BEGIN
    -- Extract the first part
    SET part1 = SUBSTRING_INDEX(input_string, '/', 1);
    
    -- Extract the second part by removing the first part and extracting the next segment
    SET part2 = SUBSTRING_INDEX(SUBSTRING_INDEX(input_string, '/', 2), '/', -1);
    
    -- Extract the third part by removing the first two parts and extracting the next segment
    SET part3 = SUBSTRING_INDEX(SUBSTRING_INDEX(input_string, '/', 3), '/', -1);
END //
DELIMITER ;


DELIMITER //

CREATE TRIGGER BeforeImageInsert
BEFORE INSERT ON image_table
FOR EACH ROW
BEGIN
    -- Calling the 'clip' function with the 'path' column of the new row and storing the result
    SET @result = clip(NEW.img_path);
    CALL SplitString(@result, @part1, @part2, @part3);
    
    SET NEW.img_type1 = CONVERT(@part1, UNSIGNED INTEGER);
    SET NEW.img_type2 = CONVERT(@part2, UNSIGNED INTEGER);
    SET NEW.img_type3 = CONVERT(@part3, UNSIGNED INTEGER);
    
    -- Note: NEW refers to the row that is about to be inserted.
    -- Here, we modify 'processed_path' directly before the row is actually inserted into the database.
END //

DELIMITER ;
-- Change the path
INSERT INTO image_table (img_path) VALUES ('/mysqludf/img/n02124075/n02124075_428.JPEG'); 
INSERT INTO image_table (img_path) VALUES ('/mysqludf/img/n02124075/n02124075_1183.JPEG'); 
INSERT INTO image_table (img_path) VALUES ('/mysqludf/img/n01833805/n01833805_169.JPEG'); 
SELECT * FROM image_table;


-- test procedure 
-- CALL SplitString('apple/orange/banana', @part1, @part2, @part3);

-- SELECT @part1, @part2, @part3;

DROP DATABASE TEST;
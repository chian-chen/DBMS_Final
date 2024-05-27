
CREATE DATABASE IF NOT EXISTS TEST;
USE TEST;

CREATE TABLE IF NOT EXISTS image (
    imgID INT PRIMARY KEY,
	image_path VARCHAR(100),
    C1 INT DEFAULT -1, 
    C2 INT DEFAULT -1,
    C3 INT DEFAULT -1
);

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

CREATE FUNCTION clip(input_path VARCHAR(255)) RETURNS VARCHAR(255)
DETERMINISTIC
BEGIN
    -- Implementation of the function that modifies the input_path and returns a result
    RETURN CONCAT('1', input_path);
END //

DELIMITER ;


DELIMITER //

CREATE TRIGGER BeforeImageInsert
BEFORE INSERT ON image
FOR EACH ROW
BEGIN
    -- Calling the 'clip' function with the 'path' column of the new row and storing the result
    SET @result = clip(NEW.image_path);
    CALL SplitString(@result, @part1, @part2, @part3);
    
    SET NEW.C1 = CONVERT(@part1, UNSIGNED INTEGER);
    SET NEW.C2 = CONVERT(@part2, UNSIGNED INTEGER);
    SET NEW.C3 = CONVERT(@part3, UNSIGNED INTEGER);
    
    -- Note: NEW refers to the row that is about to be inserted.
    -- Here, we modify 'processed_path' directly before the row is actually inserted into the database.
END //

DELIMITER ;

INSERT INTO image (imgID, image_path) VALUES (1, '12/23/22');
SELECT * FROM image;


-- test procedure 
-- CALL SplitString('apple/orange/banana', @part1, @part2, @part3);

-- SELECT @part1, @part2, @part3;

DROP DATABASE TEST;
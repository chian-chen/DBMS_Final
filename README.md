# DBMS_Final
## Requirement
* docker
* docker-compose
## Quick start
```bash
$ ./setup.sh
```
## Create Loadable Function into Mysql
```sql
CREATE FUNCTION image_sim RETURNS REAL SONAME 'sim_api.so';
CREATE  FUNCTION clip RETURNS STRING SONAME 'clip_api.so';
```
## Functions
* clip
```sql
clip(string img_path)
-- img_path: the image path in database server
-- return top 3 types match the image separate by '/'. e.g. type1/type2/type3
```
* image_sim
```sql
image_sim(string img_path1, string img_path2, [string type])
-- img_path1: the image path in database server
-- img_path2: the image path in database server
-- type: type of similarity metric, including PSNR, SSIM, LPIPS
-- return the similarity (with different types of similarity metric) of two image
```
## Usage
### clip

We use ```clip``` to automatically label the image by using the trigger INSERT BEFORE
```sql
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

INSERT INTO image_table (img_path) VALUES ('/mysqludf/imgs/n02124075/n02124075_428.JPEG'); 
```

### image_sim
Suppose we already insert three images
```sql
INSERT INTO images (img_name)
VALUES ("/mysqludf/img.png"),
       ("/mysqludf/cat.jpeg"),
       ("/mysqludf/dog.jpeg");
```
The image_sim user define function support query with image and query with text. 

```sql
SELECT img_name, image_sim(img_name, './img.png') AS sim FROM images;

SELECT img_name FROM images WHERE image_sim(img_name, './img.png') > 0.8;

SELECT img_name, image_sim(img_name, 'A cat') AS Sim FROM images WHERE image_sim(img_name, 'A cat') > 0.25;

```

We also support query an image with different types of similairty metric, including PSNR, SSIM, LPIPS.

```sql
SELECT img_name, image_sim(img_name, '././n02099601_5.JPEG', 'LPIPS') AS Sim_LPIPS FROM images;

SELECT img_name, image_sim(img_name, './n02099601_5.JPEG', 'PSNR') AS Sim_PSNR FROM images;

SELECT img_name, image_sim(img_name, './n02099601_5.JPEG', 'SSIM') AS Sim_SSIM FROM images;
```


See more example in [demo.sql](./demo.sql), [test_clip.sql](./test_clip.sql), [test_sim.sql](./test_sim.sql)
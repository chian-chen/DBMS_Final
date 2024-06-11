# DBMS_Final

## Usage image_sim user define function

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




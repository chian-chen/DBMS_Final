
import clip
import torch
import os
import numpy as np
import random

from PIL import Image
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, lit
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, ArrayType, FloatType

from numpy.linalg import norm


@udf (returnType=FloatType())
def query_image(feat, image_feat):
    def cosine_similarity(a, b):
        return np.dot(a, b) / (norm(a) * norm(b)+ 0.00001)

    # image_feat = image_feat.numpy()
    image_feat = np.array(image_feat)
    image_feat = image_feat.flatten()

    feat_np = np.array(feat)
    feat_np = feat_np.flatten()

    similarity = cosine_similarity(feat_np, image_feat)
    similarity = float(similarity)

    return similarity

def image_to_feat(folder_path):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    # Define supported image extensions
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')

    # Initialize an empty list to store image paths
    image_paths = []

    # Iterate over all files in the directory
    for file_name in os.listdir(folder_path):
        # Check if the file has one of the supported image extensions
        if file_name.lower().endswith(image_extensions):
            # Construct the full file path and append it to the list
            image_paths.append(os.path.join(folder_path, file_name))

    image_features = []

    for img_pth in image_paths:
        image = preprocess(Image.open(img_pth)).unsqueeze(0).to(device)
        with torch.no_grad():
            image_feat = model.encode_image(image)
            # print(image_feat.tolist())
            image_features.append(image_feat.tolist())


    data = [ (path, feat) for path, feat in zip(image_paths, image_features)]
 
    schema = StructType([
    StructField("path", StringType(), False),
    StructField("feat", ArrayType(ArrayType(FloatType())), False)
    ])
    # schema = []

    return data, schema


if __name__=="__main__":
    spark = SparkSession.builder.getOrCreate()

    img_dir = "db"
    img_data, img_schema = image_to_feat(img_dir)

    # Create Spark DataFrame
    df = spark.createDataFrame(img_data, img_schema)

    # Create temporary views
    df.createOrReplaceTempView("df_view")

    # Show the DataFrame
    print("Create db for images in a folder:")
    spark.sql("SELECT * FROM df_view").show()



    # New data to add
    new_data = [
        ("path/to/image3.jpg", [[random.uniform(0.0, 1.0) for _ in range(512)] for _ in range(1)]),
        ("path/to/image4.jpg", [[random.uniform(0.0, 1.0) for _ in range(512)] for _ in range(1)])
    ]
    
    # Create DataFrame for new data
    new_df = spark.createDataFrame(new_data, img_schema)
    # new_df.show()
    
    # Combine the DataFrames
    df = df.union(new_df)

    print("Add new image to db:")
    df.show()


    # Query a image (TODO: text)

    query_path = "./query/query_cat.png"

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    image = preprocess(Image.open(query_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        image_feat = model.encode_image(image)
    image_feat = image_feat.cpu().tolist()
    # image_feat = image_feat.cpu().numpy().astype(np.float32)
    # print(image_feat.shape)

    print("Query a image:")
    df.withColumn('SIM_COSINE', query_image("feat", lit(image_feat))).show()
    print("Query a image, similarity > 0.8:")
    df.withColumn('SIM_COSINE', query_image("feat", lit(image_feat)) ).filter(col('SIM_COSINE') > 0.8).show()

    # df.withColumn('SIM_COSINE', query_image("feat", image_feat)).show()
    # df.createOrReplaceTempView("df_viewa")
    # spark.sql("SELECT path, query_ FROM df_viewa where SIM_COSINE > 0.8").show()
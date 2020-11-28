# -*- coding: utf-8 -*-
"""SOMDataAnalysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KSwmKktDhckGtK5UdW6pSt8ubzdNgSRF
"""

!apt-get install openjdk-11-jdk-headless -qq > /dev/null
!wget -q https://archive.apache.org/dist/spark/spark-3.0.0/spark-3.0.0-bin-hadoop3.2.tgz
!tar xf spark-3.0.0-bin-hadoop3.2.tgz
!pip install -q findspark

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"
os.environ["SPARK_HOME"] = "/content/spark-3.0.0-bin-hadoop3.2"

import findspark
findspark.init()

from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[*]").getOrCreate()

prediction25 = pd.read_csv("/content/part1_5x5.csv", skiprows=1, header=None)
prediction_df25 = spark.createDataFrame(prediction25)
prediction_df25.show()

prediction100 = pd.read_csv("/content/part1_10x10.csv", skiprows=1, header=None)
prediction_df100 = spark.createDataFrame(prediction100)
prediction_df100.show()
# for file_num in range(2, 6):
#   file_data = pd.read_csv("/content/part{}_10x10.csv".format(file_num), header=None)
#   prediction = pd.concat([prediction, file_data])

point = pd.read_csv("/content/part1.csv", header=None)
point.head(5)
point_df = spark.createDataFrame(point)
point_df.show()

from pyspark.sql import functions as F

xy_df = point_df.select('1', '2').withColumnRenamed('1', 'x').withColumnRenamed('2', 'y').withColumn("row_id", F.monotonically_increasing_id())
value_df = prediction_df100.withColumnRenamed('0', 'prediction').withColumn("row_id", F.monotonically_increasing_id())
xy_df.show()
value_df.show()

xy_df = xy_df.alias('xy_df')
value_df = value_df.alias('value_df')
concat_df = xy_df.join(value_df, xy_df.row_id == value_df.row_id, 'inner').sort(xy_df.row_id).drop('row_id')
concat_df.show()

clusterCount = concat_df.groupBy("prediction").count().sort('prediction')
clusterCount.show()

pdf = clusterCount.toPandas()
pdf.plot(color = '#44D3A5', legend = False,
                           kind = 'bar', use_index = True,  y = 'count', grid = False)
plt.xlabel('topic')
plt.ylabel('counts')

plt.show()

# x_array = concat_df.select('x').collect()
# y_array = concat_df.select('y').collect()
# p_array = concat_df.select('prediction').collect()

# clusters = pd.DataFrame(dict(x=x_array, y=y_array, prediction=p_array)).groupby('prediction')
pdf = concat_df.toPandas()
clusters = pdf.groupby('prediction')

# Plot
fig, ax = plt.subplots()
ax.margins(0.05) # Optional, just adds 5% padding to the autoscaling
for prediction, cluster in clusters:
    ax.plot(cluster.x, cluster.y, marker='.', linestyle='', ms=12)
ax.legend()

plt.show()

from sklearn.metrics import silhouette_samples, silhouette_score

silhouette_avg = silhouette_score(X, cluster_labels)
print(silhouette_avg)
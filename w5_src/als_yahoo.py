from pyspark.sql import SparkSession

from pyspark.sql.functions import split

from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS

import time

spark = SparkSession.builder.appName("Yahoo_Recommender").config("spark.executor.memory", "16g").getOrCreate()
#spark = SparkSession.builder.appName("ALSExample").getOrCreate()

startTime = time.time()

#lines = spark.read.text("ml-100k/u.data")

#parts = lines.withColumn("value", split("value", "\t"))
#ratings = parts.select(parts.value.getItem(0).cast("int").alias("userId"),
#                       parts.value.getItem(1).cast("int").alias("movieId"),
#                       parts.value.getItem(2).cast("float").alias("rating"))
#ratings = spark.read.option("inferSchema", "true").option("header", "true").csv("ml-20m/ratings.csv")
training = spark.read.csv('yahoo/train*.txt', sep='\t', schema='userId int, movieId int, rating int')

#(training, test) = ratings.randomSplit([0.8, 0.2])
test = spark.read.csv('yahoo/test*.txt', sep='\t', schema='userId int, movieId int, rating int')

# Build the recommendation model using ALS on the training data
# Note we set cold start strategy to 'drop' to ensure we don't get NaN evaluation metrics
als = ALS(maxIter=10, regParam=0.05, coldStartStrategy="drop",
          userCol="userId", itemCol="movieId", ratingCol="rating")
model = als.fit(training)

# Evaluate the model by computing the RMSE on the test data
predictions = model.transform(test)
evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating",
                                predictionCol="prediction")
rmse = evaluator.evaluate(predictions)
print("Root-mean-squared error = " + str(rmse))

# Generate top 10 movie recommendations for a specified set of users
users = training.select(als.getUserCol()).distinct().limit(3) # substitute raitings with training
userSubsetRecs = model.recommendForUserSubset(users, 10)

userSubsetRecs.show(truncate=False)

endTime = time.time()

print("Elapsed time = " + str(endTime - startTime))

spark.stop()

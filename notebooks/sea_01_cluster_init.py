# Databricks notebook source
# DBTITLE 1,Initialize the Data Cluster
# MAGIC %sh ../sea_cluster_init.sh

# COMMAND ----------

# DBTITLE 1,Install Python Dependencies
# MAGIC %pip install -r ../requirements.txt
# MAGIC dbutils.library.restartPython()
# MAGIC
# MAGIC print('')
# MAGIC print('Python is ready! :-)')

# COMMAND ----------

# DBTITLE 1,Make the S.E.A. Package Available
import sys
sys.path.append('../')

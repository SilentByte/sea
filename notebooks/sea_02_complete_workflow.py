# Databricks notebook source
# MAGIC %md
# MAGIC ![SEA](https://rab-stuff.web.app/sea/sea_banner.png)
# MAGIC
# MAGIC # Welcome to S.E.A.!
# MAGIC
# MAGIC This notebook makes it easy to get started with setting up the project, ingest documents, process the data, and query the GenAI models powered by Databricks!

# COMMAND ----------

# DBTITLE 1,Initialize Cluster & Python
# MAGIC %run ./sea_01_cluster_init

# COMMAND ----------

# DBTITLE 1,Create the SEA Runtime
from sea.config import SeaConfig
from sea.sea import SeaRuntime

sea_runtime = SeaRuntime(SeaConfig(), spark, dbutils)

# COMMAND ----------

# DBTITLE 1,⚠️☠️🚨 RESETS EVERYTHING! 🚨☠️⚠️
##
##                      ██████   █████  ███    ██  ██████  ███████ ██████
##                      ██   ██ ██   ██ ████   ██ ██       ██      ██   ██
##                      ██   ██ ███████ ██ ██  ██ ██   ███ █████   ██████
##                      ██   ██ ██   ██ ██  ██ ██ ██    ██ ██      ██   ██
##                      ██████  ██   ██ ██   ████  ██████  ███████ ██   ██ ▄█
##               
##               
##                                   ██     ██ ██ ██      ██
##                                   ██     ██ ██ ██      ██
##                                   ██  █  ██ ██ ██      ██
##                                   ██ ███ ██ ██ ██      ██
##                                    ███ ███  ██ ███████ ███████
##               
##               
##               ██████   ██████  ██████  ██ ███    ██ ███████  ██████  ███    ██ ██
##               ██   ██ ██    ██ ██   ██ ██ ████   ██ ██      ██    ██ ████   ██ ██
##               ██████  ██    ██ ██████  ██ ██ ██  ██ ███████ ██    ██ ██ ██  ██ ██
##               ██   ██ ██    ██ ██   ██ ██ ██  ██ ██      ██ ██    ██ ██  ██ ██
##               ██   ██  ██████  ██████  ██ ██   ████ ███████  ██████  ██   ████ ██
##
##
## DANGER: THIS OPERATION WILL DESTROY ALL CREATED TABLES, VECTOR SERACH INDEXES,
##         CHECKPOINTS, AND OTHER RESOURCES! EXECUTING THIS OPERATION MAY LEAD
##         TO DATA LOSS, SO BEWARE!
##
##
## Uncomment the following line to execute this operation:
## sea_runtime.destroy_runtime()

# COMMAND ----------

# DBTITLE 1,Initialize Databricks, Spark, and SEA
sea_runtime.initialize_runtime()

# COMMAND ----------

# DBTITLE 1,List Ingested Documents in Volume
display(dbutils.fs.ls(sea_runtime.config.documents_dir()))

# COMMAND ----------

# DBTITLE 1,Ingest all Documents in the Volume
sea_runtime.ingest_documents()

# COMMAND ----------

# DBTITLE 1,List Ingested Documents in Spark
# MAGIC %sql
# MAGIC SELECT file_name, file_hash, file_size
# MAGIC FROM documents
# MAGIC ORDER BY file_size DESC
# MAGIC LIMIT 20

# COMMAND ----------

# DBTITLE 1,Compute Search Vectors (Embeddings) and Create The Databrick's Vector Search Index
sea_runtime.compute_document_vectors()
sea_runtime.create_document_vectors_index()

# COMMAND ----------

# DBTITLE 1,Helper Function to Render Markdown
# MAGIC %pip install markdown
# MAGIC
# MAGIC import markdown as md
# MAGIC
# MAGIC def display_markdown(text: str):
# MAGIC     html = r'''
# MAGIC         <style>
# MAGIC             .mdc {
# MAGIC                 font-size: 12pt;
# MAGIC                 line-height: 1.5em;
# MAGIC             }
# MAGIC             .mdc hr {
# MAGIC                 margin: 2em 0;
# MAGIC             }
# MAGIC             .mdc p {
# MAGIC                 margin-bottom: 0.75em;
# MAGIC             }
# MAGIC             .mdc ul, ol {
# MAGIC                 margin: 0 0 1.5em 0;
# MAGIC             }
# MAGIC             .mdc li + li {
# MAGIC                 margin-top: 0.75em;
# MAGIC             }
# MAGIC         </style>
# MAGIC         <div class='mdc'>
# MAGIC             {{MARKDOWN}}
# MAGIC         </div>
# MAGIC     '''.replace('{{MARKDOWN}}', md.markdown(text))
# MAGIC
# MAGIC     displayHTML(html)
# MAGIC

# COMMAND ----------

# DBTITLE 1,Let's Ask The Model!
from sea.inference import SeaInferenceClient, InferenceInteraction

question = r'''
    My oil pressure suddenly dropped. I am using the Jabiru 5100 Aircraft Engine.
    What could have caused the problem? Can you provide a list of steps to do?
'''

client = SeaInferenceClient(
    vector_search_endpoint=sea_runtime.config.vector_search_endpoint,
    vector_search_index=sea_runtime.config.document_vectors_index,
    result_count=4,
    prompt_template_override=r'''
        You are an assistant to a qualified engineer and about to answer their question.

        Here is the previous conversation history between you and the engineer:

        {history}

        Here are a few search results from aircraft manufacturing and maintenance documentations that you need to consider:

        {search_results}

        Based on these results, answer the following question:

        {question}

        Your response must be formatted using markdown.
    ''',
)

inference_result = client.infer_interaction([
    InferenceInteraction('user', question),
])

display_markdown(inference_result.to_markdown())

# COMMAND ----------

# DBTITLE 1,It's Multilingual! 🤩
from sea.inference import SeaInferenceClient, InferenceInteraction

question = r'''
    Der Öldruck im Motor hat plötzlich nachgelassen. Ich verwende den Jabiru 5100 Motor.
    Was könnte das Problem verursacht haben? Kannst du mir eine Liste mit Schritten erstellen,
    die ich abarbeiten kann?
'''

client = SeaInferenceClient(
    vector_search_endpoint=sea_runtime.config.vector_search_endpoint,
    vector_search_index=sea_runtime.config.document_vectors_index,
    result_count=4,
)

inference_result = client.infer_interaction([
    InferenceInteraction('user', question),
])

display_markdown(inference_result.to_markdown())

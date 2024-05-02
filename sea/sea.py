# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #


from typing import Any
from textwrap import dedent

import pyspark.sql.functions as F

from databricks.vector_search.client import VectorSearchClient

from sea.config import SeaConfig
from sea.udf import extract_document_chunks, compute_embeddings
from sea import utils


class SeaVectorSearchIndex:
    client: VectorSearchClient
    endpoint_name: str
    index_name: str

    def __init__(self, endpoint_name: str, index_name: str):
        self.client = VectorSearchClient()
        self.endpoint_name = endpoint_name
        self.index_name = index_name

    def _index(self):
        return self.client.get_index(self.endpoint_name, self.index_name)

    def query_status(self) -> str:
        try:
            description = self._index().describe()
        except Exception as e:
            # There seems to be no other way to get this information in a structured manner from the Databricks SDK...
            if 'RESOURCE_DOES_NOT_EXIST' in str(e):
                return 'ABSENT'

            raise e

        return utils.dict_item_from_path(description, 'status.detailed_state')

    def query_exists(self) -> bool:
        return self.query_status() != 'ABSENT'

    def await_deployment(self, timeout: int | None = None, report_progress: bool = True) -> str:
        status = 'UNKNOWN'
        start_time = utils.epoch()

        while timeout is None or start_time + timeout < utils.epoch():
            status = self.query_status()

            if 'ONLINE' in status:
                print(f'Vector Search Index {self.index_name} @ {self.endpoint_name} is {status}')
                break

            if report_progress:
                print(f'Waiting for Vector Search Index {self.index_name} @ {self.endpoint_name}: {status}')

            utils.sleep(10)

        return status

    def create(
            self,
            source_table_name: str,
            pipeline_type: str,
            primary_key: str,
            embedding_vector_column: str,
            embedding_dimension: int,
    ) -> None:
        self.client.create_delta_sync_index(
            endpoint_name=self.endpoint_name,
            index_name=self.index_name,
            source_table_name=source_table_name,
            pipeline_type=pipeline_type,
            primary_key=primary_key,
            embedding_vector_column=embedding_vector_column,
            embedding_dimension=embedding_dimension,
        )

    def drop(self) -> None:
        self.client.delete_index(self.endpoint_name, self.index_name)

    def sync(self) -> None:
        self._index().sync()


class SeaRuntime:
    def __init__(self, config: SeaConfig, spark, dbutils):
        self.config = config
        self.spark = spark
        self.dbutils = dbutils

    def spark_query(self, query: str, args: dict[str, Any] | list | None = None, **kwargs: Any) -> Any:
        query = dedent(query).strip()
        print(query)
        return self.spark.sql(query, args, **kwargs)

    def initialize_runtime(self) -> None:
        self.spark.conf.set("spark.sql.execution.arrow.maxRecordsPerBatch", self.config.spark_max_records_per_batch)

        current_catalog = self.spark_query('SELECT current_catalog() AS name').collect()[0]['name']
        available_catalogs = [
            row['catalog']
            for row in self.spark_query('SHOW CATALOGS').collect()
        ]

        if current_catalog != self.config.catalog:
            if current_catalog not in available_catalogs:
                self.spark_query(f'CREATE CATALOG IF NOT EXISTS `{self.config.catalog}`')
                self.spark_query(f'ALTER CATALOG `{self.config.catalog}` OWNER TO `account users`')

            self.spark_query(f'CREATE SCHEMA IF NOT EXISTS `{self.config.catalog}`.`{self.config.schema}`')
            self.spark_query(f'GRANT CREATE, USAGE ON DATABASE `{self.config.catalog}`.`{self.config.schema}` TO `account users`')

        self.spark_query(f'USE `{self.config.catalog}`.`{self.config.schema}`')

        self.spark_query(f'CREATE VOLUME IF NOT EXISTS `{self.config.catalog}`.`{self.config.schema}`.`{self.config.volume}`')

        self.spark_query(r'''
            CREATE TABLE IF NOT EXISTS documents (
                id                  BIGINT GENERATED BY DEFAULT AS IDENTITY,
                file_name           STRING,
                file_hash           STRING,
                file_size           BIGINT,
                file_timestamp      TIMESTAMP,
                content             BINARY,
                created_on          TIMESTAMP
            )
        ''')

        self.spark_query(r'''
            CREATE TABLE IF NOT EXISTS document_vectors (
                id                  BIGINT GENERATED BY DEFAULT AS IDENTITY,
                file_name           STRING,
                file_hash           STRING,
                start_page_no       INT,
                end_page_no         INT,
                content             STRING,
                embeddings          ARRAY<FLOAT>,
                created_on          TIMESTAMP
            ) TBLPROPERTIES (delta.enableChangeDataFeed = true)
        ''')

        # Ensure the properties are set correctly in case the table already existed.
        self.spark_query(r'ALTER TABLE document_vectors SET TBLPROPERTIES (delta.enableChangeDataFeed = true)')

    def destroy_runtime(self) -> None:
        index = SeaVectorSearchIndex(
            endpoint_name=self.config.vector_search_endpoint,
            index_name=self.config.document_vectors_index,
        )

        if index.query_exists():
            index.drop()

        self.spark_query(r'DROP TABLE IF EXISTS document_vectors')
        self.spark_query(r'DROP TABLE IF EXISTS documents')

        self.dbutils.fs.rm(self.config.checkpoints_dir("documents"), True)
        self.dbutils.fs.rm(self.config.checkpoints_dir("document_vectors"), True)

    def ingest_documents(self) -> None:
        (
            self.spark
            .readStream
            .format('cloudFiles')
            .option('cloudFiles.format', 'BINARYFILE')
            .option('pathGlobFilter', '*.pdf')
            .load(self.config.documents_dir())

            .withColumn('file_hash', F.sha2('content', 256))
            .withColumn('created_on', F.now())
            .selectExpr(
                'path AS file_name',
                'file_hash',
                'length AS file_size',
                'modificationTime AS file_timestamp',
                'content',
                'created_on',
            )

            .writeStream
            .trigger(availableNow=True)
            .option('checkpointLocation', self.config.checkpoints_dir('documents'))
            .table('documents')
            .awaitTermination()
        )

    def compute_document_vectors(self) -> None:
        (
            self.spark
            .readStream
            .table('documents')
            .withColumn('processed', F.explode(extract_document_chunks('content')))
            .withColumn('content', F.col('processed.text'))
            .withColumn('start_page_no', F.col('processed.start_page_no'))
            .withColumn('end_page_no', F.col('processed.end_page_no'))
            .withColumn('embeddings', compute_embeddings('content'))
            .withColumn('created_on', F.now())
            .selectExpr('file_name', 'file_hash', 'start_page_no', 'end_page_no', 'content', 'embeddings', 'created_on')
            .writeStream.trigger(availableNow=True)
            .option('checkpointLocation', self.config.checkpoints_dir('document_vectors'))
            .table('document_vectors')
            .awaitTermination()
        )

    def create_document_vectors_index(self) -> None:
        index = SeaVectorSearchIndex(
            endpoint_name=self.config.vector_search_endpoint,
            index_name=self.config.document_vectors_index,
        )

        if index.query_exists():
            index.await_deployment()
            index.sync()
        else:
            index.create(
                source_table_name=f'{self.config.catalog}.{self.config.schema}.document_vectors',
                pipeline_type='TRIGGERED',
                primary_key='id',
                embedding_vector_column='embeddings',
                embedding_dimension=1024,
            )

            index.await_deployment()

# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #


from typing import Any
from textwrap import dedent

import pyspark.sql.functions as F

from sea.config import SeaConfig


class SeaRuntime:
    def __init__(self, config: SeaConfig, spark):
        self.config = config
        self.spark = spark

    def spark_query(self, query: str, args: dict[str, Any] | list | None = None, **kwargs: Any) -> Any:
        query = dedent(query).strip()
        print(query)
        return self.spark.sql(query, args, **kwargs)

    def initialize_spark(self) -> None:
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

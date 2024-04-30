# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #

from typing import Iterator

from sea import dataprocessing

import pandas as pd
import mlflow.deployments
from pyspark.sql.functions import pandas_udf, PandasUDFType


@pandas_udf('ARRAY<STRUCT<text: STRING, start_page_no: INT, end_page_no: INT>>', PandasUDFType.SCALAR_ITER)
def extract_document_chunks(document_data_series: Iterator[pd.Series]) -> Iterator[pd.Series]:
    for document_data in document_data_series:
        yield document_data.apply(lambda dd: [
            {
                'text': chunk.text,
                'start_page_no': chunk.start_page_no,
                'end_page_no': chunk.end_page_no,
            } for chunk in dataprocessing.extract_document_sentence_chunks(
                document_data=dd,
                chunk_size=640,
                chunk_overlap=60,
            )
        ])


@pandas_udf('ARRAY<FLOAT>', PandasUDFType.SCALAR)
def compute_embeddings(content_series: pd.Series) -> pd.Series:
    deploy_client = mlflow.deployments.get_deploy_client('databricks')

    def predict(batch):
        return [
            e['embedding']
            for e in deploy_client.predict(
                endpoint='databricks-bge-large-en',
                inputs={
                    'input': batch,
                },
            ).data
        ]

    model_chunk_size = 150
    chunks = [
        content_series.iloc[i: i + model_chunk_size]
        for i in range(0, len(content_series), model_chunk_size)
    ]

    return pd.Series([
        embedding
        for batch in chunks
        for embedding in predict(batch.tolist())
    ])

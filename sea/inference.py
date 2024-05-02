# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #


import os

from dataclasses import dataclass

from databricks.vector_search.client import VectorSearchClient
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableLambda
from langchain_community.chat_models import ChatDatabricks
from langchain_community.embeddings import DatabricksEmbeddings
from langchain_community.vectorstores import DatabricksVectorSearch

from sea import utils


@dataclass
class InferenceSource:
    text: str
    file_name: str
    file_hash: str
    start_page_no: int
    end_page_no: int

    def to_dict(self) -> dict:
        return {
            'text': self.text,
            'file_name': self.file_name,
            'file_hash': self.file_hash,
            'start_page_no': self.start_page_no,
            'end_page_no': self.end_page_no,
        }

    def to_markdown(self) -> str:
        if self.start_page_no == self.end_page_no:
            return f'{self.file_name}, p. {self.start_page_no}'
        else:
            return f'{self.file_name}, pp. {self.start_page_no}-{self.end_page_no}'


@dataclass
class InferenceResult:
    text: str
    sources: list[InferenceSource]

    def to_dict(self) -> dict:
        return {
            'text': self.text,
            'sources': [
                s.to_dict()
                for s in self.sources
            ],
        }

    def to_markdown(self) -> str:
        if len(self.sources) == 0:
            return self.text

        sources_list = '\n'.join(sorted([
            f'- {s.to_markdown()}'
            for s in self.sources
        ]))

        return f'{self.text}\n\nSources:\n{sources_list}'


@dataclass
class InferenceInteraction:
    originator: str
    text: str


class SeaInferenceClient:
    def __init__(
            self,
            vector_search_endpoint: str,
            vector_search_index: str,
            result_count: int,
    ):
        self.vector_search_endpoint = vector_search_endpoint
        self.vector_search_index = vector_search_index
        self.result_count = max(1, min(result_count, 16))

        self.embedding_model = DatabricksEmbeddings(endpoint="databricks-bge-large-en")
        self.agent_model = ChatDatabricks(
            endpoint="databricks-dbrx-instruct",
            max_tokens=620,
        )

    def _retriever(self):
        vector_search_client = VectorSearchClient()
        vector_search_index = vector_search_client.get_index(
            endpoint_name=self.vector_search_endpoint,
            index_name=self.vector_search_index,
        )

        return DatabricksVectorSearch(
            index=vector_search_index,
            text_column='content',
            embedding=self.embedding_model,
            columns=[
                'file_name',
                'file_hash',
                'start_page_no',
                'end_page_no',
            ],
        ).as_retriever(search_kwargs={
            'k': self.result_count,
        })

    def _prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            input_variables=['question', 'search_results'],
            template=utils.dedent('''
                You are an assistant to an engineer and about to answer their question.        

                Here is the previous conversation history between you and the engineer:
                
                {history}

                Here are a few search results from aircraft manufacturing and maintenance documentations that you need to consider:

                {search_results}

                Based on these results, answer the following question:

                {question}

                Your response must be formatted using markdown.
            '''),
        )

    @staticmethod
    def _extract_question(interaction_history: list[InferenceInteraction]) -> str:
        return (interaction_history[-1].text).strip()

    @staticmethod
    def _concatenate_history_text(interaction_history: list[InferenceInteraction]) -> str:
        if len(interaction_history) < 2:
            return "None."

        def format_interaction(interaction: InferenceInteraction) -> str:
            if interaction.originator == 'agent':
                return f'You: {interaction.text.strip()}'
            else:
                return f'Engineer: {interaction.text.strip()}'

        return '\n\n'.join([
            format_interaction(ir)
            for ir in interaction_history[:-1]
        ])

    @staticmethod
    def _concatenate_search_results(search_results) -> str:
        return '\n\n'.join([
            sr.page_content
            for sr in search_results
        ])

    @staticmethod
    def _extract_sources(search_results) -> list[InferenceSource]:
        return [
            InferenceSource(
                text=sr.page_content,
                file_name=os.path.basename(sr.metadata['file_name']),
                file_hash=sr.metadata['file_hash'],
                start_page_no=int(sr.metadata['start_page_no']),
                end_page_no=int(sr.metadata['end_page_no']),
            )
            for sr in search_results
        ]

    def _search_index(self, interaction_history: list[InferenceInteraction]):
        return (
                RunnableLambda(SeaInferenceClient._extract_question)
                | self._retriever()
        ).invoke(interaction_history)

    def infer_interaction(self, interaction_history: list[InferenceInteraction]) -> InferenceResult:
        if len(interaction_history) == 0:
            raise ValueError('Interaction history must not be empty')

        search_results = self._search_index(interaction_history)
        prompt_template = self._prompt_template()

        inference_result = (
                prompt_template
                | self.agent_model
                | StrOutputParser()
        ).invoke({
            'search_results': SeaInferenceClient._concatenate_search_results(search_results),
            'history': SeaInferenceClient._concatenate_history_text(interaction_history),
            'question': SeaInferenceClient._extract_question(interaction_history),
        })

        return InferenceResult(
            text=inference_result,
            sources=SeaInferenceClient._extract_sources(search_results),
        )

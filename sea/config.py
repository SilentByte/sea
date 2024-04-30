# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #


from dataclasses import dataclass


@dataclass
class SeaConfig:
    catalog: str = 'sea'
    schema: str = 'sea'
    volume: str = 'sea_data'
    vector_search_endpoint: str = 'sea_vector_search'

    def volume_dir(self, path: str) -> str:
        return f'dbfs:/Volumes/{self.catalog}/{self.schema}/{self.volume}/{path}'

    def documents_dir(self) -> str:
        return self.volume_dir('documents')

    def checkpoints_dir(self, name: str) -> str:
        return self.volume_dir(f'checkpoints/{name}')

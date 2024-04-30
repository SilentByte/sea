# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #


from typing import Any

from sea.config import SeaConfig

CONFIG = SeaConfig()


# noinspection PyUnresolvedReferences
def spark_query(query: str, args: dict[str, Any] | list | None = None, **kwargs: Any) -> Any:
    print(query)
    return spark.sql(query, args, **kwargs)


def initialize_spark():
    current_catalog = spark_query('SELECT current_catalog() AS name').collect()[0]['name']
    available_catalogs = [
        row['catalog']
        for row in spark_query('SHOW CATALOGS').collect()
    ]

    if current_catalog != CONFIG.catalog:
        if current_catalog not in available_catalogs:
            spark_query(f'CREATE CATALOG IF NOT EXISTS `{CONFIG.catalog}`')
            spark_query(f'ALTER CATALOG `{CONFIG.catalog}` OWNER TO `account users`')

        spark_query(f'CREATE SCHEMA IF NOT EXISTS `{CONFIG.catalog}`.`{CONFIG.schema}`')
        spark_query(f'GRANT CREATE, USAGE ON DATABASE `{CONFIG.catalog}`.`{CONFIG.schema}` TO `account users`')

    spark_query(f'USE `{CONFIG.catalog}`.`{CONFIG.schema}`')

    spark_query(f'CREATE VOLUME IF NOT EXISTS `{CONFIG.catalog}`.`{CONFIG.schema}`.`{CONFIG.volume}`')

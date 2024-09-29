from typing import Optional, List
from v1.db import DatabaseController
from v1.common.schemas import Page, FetchPage, FetchPages

# for embedding
from fastembed import TextEmbedding
import spacy
import re
import numpy as np

nlp = spacy.load("en_core_web_sm", enable=["attribute_ruler", "tagger", "lemmatizer"])
model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")


def embed(sentence: str, precision: int = 3) -> List[float]:
    """creates a vector embedding given a senctence"""
    lemma = " ".join(
        token.lemma_
        for token in nlp(sentence)
        if not token.is_stop and not token.is_punct
    )
    embedding = next(model.embed([lemma]))
    return np.round(embedding.astype(np.float64), precision).tolist()


def create_insert_page_sql(page: Page) -> str:
    """creates the surrealdb sql to create the page and it's commands"""
    command_ids = [
        f"page_{page.id}_" + re.sub(r'\W+', '', c.name.replace(" ", "_").lower()) for c in page.commands
    ]
    page_create = f"""CREATE ONLY page:{page.id} SET title="{page.title}", text="{page.text}", embedding={embed(page.title + '. ' + page.text)}, limit={page.limit}, commands=[{','.join([f"command:{c_id}" for c_id in command_ids])}];\n"""
    for c_id, c in zip(command_ids, page.commands):
        command_create = f"""CREATE ONLY command:{c_id} SET name="{c.name}", text="{c.text}", page=page:{c.page}, required=[{','.join([f"'page:{page_id}'" for page_id in c.required])}];\n"""
        page_create += command_create
    return page_create


class PageRepository(DatabaseController):
    def __init__(self):
        super().__init__()

    async def fetch_page(self, page_id: int) -> FetchPage:
        """selects one page given by the page_id from surreal"""
        select_query = f"SELECT id, title, text, commands.name, commands.text, commands.page, commands.required FROM page:{page_id};"
        data = await anext(self.sql(select_query))
        if data:
            return FetchPage.model_validate(data[0])
        else:
            return None

    async def fetch_all_pages(self) -> FetchPages:
        """fetch pages from database"""
        select_query = "SELECT id, title, text, commands.name, commands.text, commands.page, commands.required FROM page;"
        data = await anext(self.sql(select_query))
        if data:
            return FetchPages.validate_python(data)
        else:
            return None

    async def create_page(self, page: Page):
        create_query = create_insert_page_sql(page)
        data = [res async for res in self.sql(create_query)]
        if data:
            return data
        else:
            return None

    async def delete_page(self, page_id: int):
        res = await anext(self.sql(f"DELETE page:{page_id}"))
        return res

    async def search_pages(self, query: str, limit: int = 3):
        res = await anext(
            self.sql(f"""
        SELECT title, id, commands.name,
          search::highlight('<b>', '</b>', 1) AS text,
          search::score(0) * 2 + search::score(1) * 1 AS score FROM page
        WHERE title @0@ '{query}' OR text @1@ '{query}'
        ORDER BY score DESC
        LIMIT {limit};
        """)
        )
        return res

    async def semantic_search_pages(self, query: str, limit: int = 3):
        embedding = embed(query)
        iter = self.sql(f"""
        LET $pt = {embedding};
        SELECT title, id, commands.name, text,
            vector::similarity::cosine(embedding, $pt) AS score
            FROM page WHERE embedding <|384,COSINE|> $pt
            ORDER BY score DESC LIMIT {limit};
        """)

        _ = await anext(iter)
        res = await anext(iter)
        return res

    async def find_parent_pages(self, page_id: int):
        res = await anext(
            self.sql(f"""
                SELECT title, text, command.name, command.text
                FROM (
                    SELECT title, text, array::at(commands, array::find_index(commands.page, page:{page_id})) AS command
                        FROM page
                        WHERE commands.page CONTAINS page:{page_id}
                        FETCH command
                    );
            """)
        )
        return res

from uuid import uuid4
# from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter, TextSplitter
from chimera.core import Frame, Scene, Novel
from transformers import AutoTokenizer
import chromadb
from chromadb import Metadata, EmbeddingFunction
from chromadb.utils import embedding_functions



class CharMemory:

    def __init__(self, path, collection_name="character"):
        client = chromadb.PersistentClient(path)
        self.collection = client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})
    
    def add(self, content, scene_index, character_name):
        self.collection.add(
            ids=[str(uuid4())],
            documents=[content],
            metadatas=[
                {"scene_index": scene_index,
                 "character_name": character_name,
                }
            ]
        )

    def query(self, query_text, character_name, scene_index, n_results=5):
        
        memories = self.collection.query(
            query_texts=[query_text], 
            n_results=n_results, 
            where={"$and": [{"character_name": character_name}, {"scene_index": {"$lte": scene_index}}]}
            )
        # print(memories)
        return "\n".join(memories["documents"][0])


class NovelGlobalMemory:

    def __init__(self, database_path, embedding_model_path, chunk_size=512, chunk_overlap=128):
        client = chromadb.PersistentClient(database_path)
        embedding_fun = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embedding_model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(embedding_model_path)
        self.splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=lambda x: len(self.tokenizer.encode(x)))
        self.collection = client.get_or_create_collection(name="novel", metadata={"hnsw:space": "cosine"}, embedding_function=embedding_fun)

    def add(self, content):
        texts = self.splitter.split_text(content)
        ids = [str(uuid4()) for _ in texts]
        self.collection.add(
            ids=ids,
            documents=texts
        )
    
    def query(self, query_text, n_results=5):
        memories = self.collection.query(query_texts=[query_text], n_results=n_results)
        return "\n".join(memories["documents"][0])

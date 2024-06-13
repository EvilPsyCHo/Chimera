import chromadb
from chromadb import Metadata
from uuid import uuid4

from chimera.core import Frame, Scene, Novel


class CharMemory:

    def __init__(self, path, collection_name):
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

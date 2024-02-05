from elasticsearch import Elasticsearch
from datetime import datetime
import json
from urllib.request import urlopen

# Password for the 'elastic' user generated by Elasticsearch
ELASTIC_PASSWORD = "7BU_+4UxvKE6kPAE7nXW"

# Create the client instance
client = Elasticsearch(
    "https://localhost:9200",
    ca_certs="/Users/vamsi/http_ca.crt",
    basic_auth=("elastic", ELASTIC_PASSWORD)
)

# Successful response!
print(client.info())

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def pretty_response(response):
    if len(response['hits']['hits']) == 0:
        print('Your search returned no results.')
    else:
        for hit in response['hits']['hits']:
            id = hit['_id']
            publication_date = hit['_source']['publish_date']
            score = hit['_score']
            title = hit['_source']['title']
            summary = hit['_source']['summary']
            publisher = hit["_source"]["publisher"]
            num_reviews = hit["_source"]["num_reviews"]
            authors = hit["_source"]["authors"]
            pretty_output = (f"\nID: {id}\nPublication date: {publication_date}\nTitle: {title}\nSummary: {summary}\nPublisher: {publisher}\nReviews: {num_reviews}\nAuthors: {authors}\nScore: {score}")
            print(pretty_output)

def index_a_document(client):
    mappings = {
        "properties": {
            "title_vector": {
                "type": "dense_vector",
                "dims": 384,
                "index": "true",
                "similarity": "cosine"
            }
        }
    }

    # Create the index
    client.indices.create(index='book_index', mappings=mappings)
    url = "https://raw.githubusercontent.com/elastic/elasticsearch-labs/main/notebooks/search/data.json"
    response = urlopen(url)
    books = json.loads(response.read())

    operations = []
    for book in books:
        operations.append({"index": {"_index": "book_index"}})
        # Transforming the title into an embedding using the model
        book["title_vector"] = model.encode(book["title"]).tolist()
        operations.append(book)
    client.bulk(index="book_index", operations=operations, refresh=True)




def search_for_document(client):
    response = client.search(
        index="book_index",
        knn={
        "field": "title_vector",
        "query_vector": model.encode("javascript books"),
        "k": 10,
        "num_candidates": 100
        }
    )

    pretty_response(response)

if(__name__=="__main__"):
    index_a_document(client)
    search_for_document(client)
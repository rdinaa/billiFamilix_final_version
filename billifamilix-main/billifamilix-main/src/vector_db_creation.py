from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import os
import numpy as np

from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_community.document_loaders import S3DirectoryLoader, S3FileLoader
from langchain_community.embeddings import BedrockEmbeddings
from langchain.llms.bedrock import Bedrock

from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chains import LLMChain

region = "eu-central-1"
service = "aoss"
billi_host = "a4pkevhrjfw0pasvcu18.eu-central-1.aoss.amazonaws.com"
fam_host = "ezfuwmpse0avly7gwq9h.eu-central-1.aoss.amazonaws.com"

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

awsauth = AWS4Auth(AWS_ACCESS_KEY_ID,
                   AWS_SECRET_ACCESS_KEY,
                   region,
                   service)


bedrock = boto3.client(service_name='bedrock-runtime', region_name=region)
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=bedrock, region_name=region)

# s3_resource = boto3.resource('s3', region_name=region)
# billi_s3_bucket = s3_resource.Bucket("paris4-clean-billi")
# fam_s3_bucket = s3_resource.Bucket("paris4-clean-fam")

# for file in s3_bucket.objects.all():
#     loader = S3FileLoader(file.bucket_name, file.key)
#     doc = loader.load()
#     print(doc)


billi_client = OpenSearch(
    hosts=[{"host": billi_host, "port": 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    pool_maxsize=20
)

billi_vector = OpenSearchVectorSearch(
  embedding_function = bedrock_embeddings,
  index_name = 'billi-index',
  http_auth = awsauth,
  use_ssl = True,
  verify_certs = True,
  http_compress = True, # enables gzip compression for request bodies
  connection_class = RequestsHttpConnection,
  opensearch_url="https://" + billi_host
)

billi_function_vector = OpenSearchVectorSearch(
  embedding_function = bedrock_embeddings,
  index_name = 'billi-function-index',
  http_auth = awsauth,
  use_ssl = True,
  verify_certs = True,
  http_compress = True, # enables gzip compression for request bodies
  connection_class = RequestsHttpConnection,
  opensearch_url="https://" + billi_host
)

fam_client = OpenSearch(
    hosts=[{"host": fam_host}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    pool_maxsize=20
)

fam_vector = OpenSearchVectorSearch(
  embedding_function = bedrock_embeddings,
  index_name = 'fam-index',
  http_auth = awsauth,
  use_ssl = True,
  verify_certs = True,
  http_compress = True, # enables gzip compression for request bodies
  connection_class = RequestsHttpConnection,
  opensearch_url="https://" + fam_host
)

fam_function_vector = OpenSearchVectorSearch(
  embedding_function = bedrock_embeddings,
  index_name = 'fam-function-index',
  http_auth = awsauth,
  use_ssl = True,
  verify_certs = True,
  http_compress = True, # enables gzip compression for request bodies
  connection_class = RequestsHttpConnection,
  opensearch_url="https://" + fam_host
)


def generate_chunks(root_folder):

    loader = GenericLoader.from_filesystem(
        root_folder,
        suffixes=[".java"],
        parser=LanguageParser(language=Language.JAVA, parser_threshold=0),
    )

    docs = loader.load()
    len(docs)

    java_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.JAVA, chunk_size=5000, chunk_overlap=100
    )

    chunks = java_splitter.split_documents(docs)

    # for chunk in chunks:
    #     # print(chunk)
    #     sample_embedding = np.array(bedrock_embeddings.embed_query(chunk.page_content))
    #     # modelId = bedrock_embeddings.model_id
    #     # print("Embedding model Id :", modelId)
    #     # print("Sample embedding of a document chunk: ", sample_embedding)
    #     # print("Size of the embedding: ", sample_embedding.shape)

    return chunks

def remove_simplified_code(chunks):

    cleaned_chunks = []

    for chunk in chunks:
        print(chunk.metadata)
        if (('content_type' not in chunk.metadata.keys()) or (chunk.metadata['content_type'] == 'functions_classes')):
            cleaned_chunks.append(chunk)

    return cleaned_chunks


def create_VDB(chunks, vector):

    vector.add_documents(
        documents = chunks,
        vector_field = "nominee_vector",
        bulk_size = 5000
    )   


# Creation of FAM vdb
# chunks = generate_chunks("/Users/maximegillot/Desktop/Hackathon/Cleaned_FAM")
# function_chunks = remove_simplified_code(chunks)
# create_VDB(function_chunks,fam_function_vector)
# create_VDB(chunks,fam_vector)

# Creation of BILLI vdb
chunks = generate_chunks("/Users/maximegillot/Desktop/Hackathon/Cleaned_BILLI")
function_chunks = remove_simplified_code(chunks)
create_VDB(function_chunks,billi_function_vector)
# create_VDB(chunks,billi_vector)


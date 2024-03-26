from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import os
import json
from dotenv import load_dotenv
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_community.document_loaders import S3FileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import S3DirectoryLoader, S3FileLoader
import openai
from langchain_community.embeddings import BedrockEmbeddings
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chains import LLMChain

load_dotenv('.env',
            verbose=False)
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')


host = 'e6d35vvfu6a32vviyny9.eu-central-1.aoss.amazonaws.com'
region = "eu-central-1"
service = "aoss"


awsauth = AWS4Auth(AWS_ACCESS_KEY_ID,
                   AWS_SECRET_ACCESS_KEY,
                   region,
                   service)


client = OpenSearch(
    hosts=[{"host": host, "port": 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    pool_maxsize=20
)


index_name = "billi-index"
index_body = {
    "mappings": {
        "properties": {
            "nominee_text": {"type": "text"},
            "nominee_vector": {
                "type": "knn_vector",
                "dimension": 1536.,
                "method": {
                    "engine": "nmslib",
                    "space_type": "cosinesimil",
                    "name": "hnsw",
                    "parameters": {"ef_construction": 512, "m": 16},
                },
            },
        }
    },
    "settings": {
        "index": {
            "number_of_shards": 2,
            "knn.algo_param": {"ef_search": 512},
            "knn": True,
        }
    },
}

### Create index

#try:
#    response = client.indices.create(index_name, body=index_body)
#    print(json.dumps(response, indent=2))
#except Exception as ex:
#    print(ex)



bedrock = boto3.client(service_name='bedrock-runtime', region_name=region)
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=bedrock, region_name=region)

vector = OpenSearchVectorSearch(
  embedding_function = bedrock_embeddings,
  index_name = 'billi-index',
  http_auth = awsauth,
  use_ssl = True,
  verify_certs = True,
  http_compress = True, # enables gzip compression for request bodies
  connection_class = RequestsHttpConnection,
  opensearch_url="https://e6d35vvfu6a32vviyny9.eu-central-1.aoss.amazonaws.com"
)



### For all ressources

#s3_resource = boto3.resource('s3', region_name=region)
#s3_bucket = s3_resource.Bucket("paris4-experimentation")
#s3_bucket_files = []
#for s3_object in s3_bucket.objects.all():
#    loader = S3FileLoader(s3_object.bucket_name, s3_object.key)
#    text_splitter = RecursiveCharacterTextSplitter(
#      chunk_size = 1000,
#      chunk_overlap = 20,
#        length_function = len,
#        is_separator_regex = False,
#            )


loader_dir = S3DirectoryLoader("paris4-billi")

splitter = RecursiveCharacterTextSplitter.from_language("java")
docs = loader_dir.load_and_split(splitter)
print("load and split ended")


### add to database

#vector.add_documents(
#  documents = docs,
#  vector_field = "nominee_vector",
#  bulk_size = 4000
#)


embedding_vector = bedrock_embeddings.embed_query("Explain the code provided")
docs = vector.similarity_search_by_vector(
  embedding_vector,
  vector_field="nominee_vector",
  text_field="text",
  metadata_field="metadata",
)



docs_dict = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docs]
data = ""
for doc in docs_dict:
  data += doc['page_content'] + "\n\n"

### creating the LLM

llm = Bedrock(model_id="anthropic.claude-v2", client=bedrock, model_kwargs={'max_tokens_to_sample':200})

prompt_template = """

Human: Use the following pieces of context to provide a concise answer to the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
<context>
{context}
</context

Question: {question}

Assistant:"""

prompt = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

question = "Describe this code"
chain = LLMChain(llm=llm, prompt=prompt)
llm_return_data = chain.run({'question': question, 'context': data})

print(llm_return_data)
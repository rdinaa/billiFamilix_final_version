from utils.prompts import CODE_COMPARAISON_FR,CODE_EXPLANATION, CODE_EXTRACT
from utils.bedrock import ask_llm

# from prompts import CODE_COMPARAISON_FR,CODE_EXPLANATION, CODE_EXTRACT
# from bedrock import ask_llm

from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import os

from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_community.embeddings import BedrockEmbeddings
from langchain.llms.bedrock import Bedrock
from langchain_community.chat_models import BedrockChat

from langchain.chains import LLMChain


region_llm = "us-east-1"
region_opensearch = "eu-central-1"
service = "aoss"
billi_host = "a4pkevhrjfw0pasvcu18.eu-central-1.aoss.amazonaws.com"
fam_host = "ezfuwmpse0avly7gwq9h.eu-central-1.aoss.amazonaws.com"

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

awsauth = AWS4Auth(AWS_ACCESS_KEY_ID,
                   AWS_SECRET_ACCESS_KEY,
                   region_opensearch,
                   service)


bedrock = boto3.client(service_name='bedrock-runtime',
                       region_name=region_llm)
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1",
                                       client=bedrock,
                                       region_name=region_llm)


billi_vector = OpenSearchVectorSearch(
  embedding_function = bedrock_embeddings,
  index_name = 'billi-function-index',
  http_auth = awsauth,
  use_ssl = True,
  verify_certs = True,
  http_compress = True, # enables gzip compression for request bodies
  connection_class = RequestsHttpConnection,
  opensearch_url="https://" + billi_host
)


fam_vector = OpenSearchVectorSearch(
  embedding_function = bedrock_embeddings,
  index_name = 'fam-function-index',
  http_auth = awsauth,
  use_ssl = True,
  verify_certs = True,
  http_compress = True, # enables gzip compression for request bodies
  connection_class = RequestsHttpConnection,
  opensearch_url="https://" + fam_host
)


def get_llm(claude_version):
    
    if claude_version == 2:
        llm = Bedrock(model_id="anthropic.claude-v2",
                      client=bedrock,
                      model_kwargs={'max_tokens_to_sample':500})
    elif claude_version == 3:
        llm = BedrockChat(model_id="anthropic.claude-3-haiku-20240307-v1:0",
                          client=bedrock,
                          model_kwargs={'max_tokens': 500})
    else:
        exit("Invalid Claude Version. Select between 2 and 3.")

    return llm


def compare_code(fam_data, billi_data):
    llm = get_llm(3)
    chain = LLMChain(llm=llm,prompt=CODE_COMPARAISON_FR)
    code_comparaion = chain.run({'billi_code': billi_data, 'fam_code': fam_data})

    return code_comparaion


def compare_codes_with_description(fam_data, billi_data, claude_version):

    ### creating the LLM
    llm = get_llm(claude_version)

    chain = LLMChain(llm=llm,
                     prompt=CODE_EXPLANATION)
    fam_description = chain.run({'context': fam_data})

    chain = LLMChain(llm=llm,
                     prompt=CODE_EXPLANATION)
    billi_description = chain.run({'context': billi_data})

    chain = LLMChain(llm=llm,
                     prompt=CODE_COMPARAISON_FR)
    code_comparaion = chain.run({'billi_code': billi_data, 'fam_code': fam_data})


    return fam_description, billi_description, code_comparaion

def extract_code(description, code):

    ### creating the LLM
    llm = get_llm(claude_version=3)

    # llm = Bedrock(model_id="anthropic.claude-v2", client=bedrock, model_kwargs={'max_tokens_to_sample':1024})

    chain = LLMChain(llm=llm, prompt=CODE_EXTRACT)
    extracted_code = chain.run({'code': code, 'description':description})

    return extracted_code



def compare_code_based_on_description(description):

    embedding_vector = bedrock_embeddings.embed_query(description)

    fam_docs = fam_vector.similarity_search_by_vector(
        embedding_vector,
        vector_field="nominee_vector",
        text_field="text",
        metadata_field="metadata",
    )    
    
    billi_docs = billi_vector.similarity_search_by_vector(
        embedding_vector,
        vector_field="nominee_vector",
        text_field="text",
        metadata_field="metadata",
    )

    docs_dict = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in fam_docs]
    fam_data = ""
    for doc in docs_dict:
        fam_data += doc['page_content'] + "\n\n"

    
    docs_dict = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in billi_docs]
    billi_data = ""
    for doc in docs_dict:
        billi_data += doc['page_content'] + "\n\n"

    claude_version = 3

    fam_description, billi_description, code_comparaion = compare_codes_with_description(fam_data,
                                                                        billi_data,
                                                                        claude_version=claude_version)

    print("\n\n---- FAM code description:\n")
    print(fam_description)

    print("\n\n---- BILLI code description:\n")
    print(billi_description)

    print("\n\n---- Code comparison:\n")
    print(code_comparaion)

    print(f"\n\n---- Claude version used: {claude_version}\n")
    
    return fam_description, billi_description, code_comparaion


def extract_code_based_on_description(description):
  

    embedding_vector = bedrock_embeddings.embed_query(description)

    fam_docs = fam_vector.similarity_search_by_vector(
        embedding_vector,
        vector_field="nominee_vector",
        text_field="text",
        metadata_field="metadata",
    )    
    
    billi_docs = billi_vector.similarity_search_by_vector(
        embedding_vector,
        vector_field="nominee_vector",
        text_field="text",
        metadata_field="metadata",
    )

    docs_dict = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in fam_docs]
    fam_data = ""
    for doc in docs_dict:
        fam_data += doc['page_content'] + "\n\n"

    
    docs_dict = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in billi_docs]
    billi_data = ""
    for doc in docs_dict:
        billi_data += doc['page_content'] + "\n\n"


    fam_code = extract_code(description, fam_data)
    billi_code = extract_code(description, billi_data)


    print(fam_code)

    print(billi_code)
    
    return fam_code, billi_code


# compare_code_based_on_description("Bonus malus")


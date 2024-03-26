from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import os
import numpy as np
import json

from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_community.embeddings import BedrockEmbeddings
from langchain.llms.bedrock import Bedrock

from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)


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


def get_matching_billi_code(document):


    content = document.page_content
    print(len(content))

    embedded_vectors = []

    if (len(content) >= 10000):
        java_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.JAVA, chunk_size=5000, chunk_overlap=100
        )

        chunks = java_splitter.split_documents([document])

        for chunk in chunks:
            if (chunk.metadata['content_type'] == 'functions_classes'):
                embedded_vectors.append(bedrock_embeddings.embed_query(chunk.page_content))

    else:
        embedded_vectors.append(bedrock_embeddings.embed_query(content))


    result_dic = {}

    for embedded_vector in embedded_vectors:
        billi_docs = billi_vector.similarity_search_with_score_by_vector(
            embedded_vector,
            vector_field="nominee_vector",
            text_field="text",
            metadata_field="metadata",
        )

        for document in billi_docs:
            similarity_score = document[-1]
            metadata = document[0].metadata
            page_content = document[0].page_content
            source_path = document[0].metadata['source']
            source = os.path.basename(source_path)

            if source not in result_dic.keys():
                result_dic[source] = similarity_score
            elif result_dic[source] < similarity_score:
                result_dic[source] = similarity_score

    
    print(result_dic)
    return result_dic

                
    # text = ""

    # for embedded_vector in embedded_vectors:

    #     billi_docs = billi_vector.similarity_search_with_score_by_vector(
    #         embedded_vector,
    #         vector_field="nominee_vector",
    #         text_field="text",
    #         metadata_field="metadata",
    #     )

    #     # print(billi_docs)


    #     for document in billi_docs:
    #         similarity_score = document[-1]
    #         metadata = document[0].metadata
    #         page_content = document[0].page_content

    #         print(document[-1])
    #         print(metadata)

    #         text += f"\n\nSource code: {metadata['source']}\nSimilarity:{similarity_score}\n\nCode :\n```\n{page_content}\n```\n\n"

    #         # docs_dict = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in billi_docs]
    #         # billi_data = ""
    #         # for doc in docs_dict:
    #         #     billi_data += doc['metadata'] + "\n\n"
    #         #     billi_data += doc['page_content'] + "\n\n"

 
    # return text


def generate_matching_files(root_folder, output_folder):
    
    loader = GenericLoader.from_filesystem(
        root_folder,
        suffixes=[".java"],
        parser=LanguageParser(language=Language.JAVA, parser_threshold=0),
    )

    docs = loader.load()
    len(docs)

    document_dict = {}

    for document in docs:

        document_path = document.metadata['source']
        document_name = document_path.split("/")[-1]
        class_name = document_name.split(".")[0]

        file_path = output_folder + class_name + ".json"

        print("generating doc for: ", document_name)

        if (('content_type' in document.metadata.keys()) and (document.metadata['content_type'] == 'functions_classes')):


            result = get_matching_billi_code(document)

            document_dict[class_name] = result

            # f = open(file_path,"a")
            # f.write(result)
            # f.close()

            with open(file_path, "w") as outfile: 
                json.dump(result, outfile, indent=4)

    with open(output_folder + "_ALL.json", "w") as outfile: 
        json.dump(document_dict, outfile,indent = 4)


generate_matching_files(
    root_folder="/Users/maximegillot/Desktop/Hackathon/Cleaned_FAM",
    output_folder="/Users/maximegillot/Desktop/Hackathon/Code_mapping/"
    )




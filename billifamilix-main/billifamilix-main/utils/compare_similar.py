import json
from prompts import DOCUMENTATION_SUMMARY, GAP_SUMMARY
from compare_vdb import compare_codes_with_description, compare_code, get_llm
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import os

from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_community.embeddings import BedrockEmbeddings
from langchain.llms.bedrock import Bedrock

from langchain.chains import LLMChain
from markdown_pdf import MarkdownPdf, Section



def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


json_file_path = 'data/FAM_BILLI_similarity.json'
data_dictionary = read_json_file(json_file_path)

FAM_dir = "/Users/maximegillot/Desktop/Hackathon/Cleaned_FAM/"
BILLI_dir = "/Users/maximegillot/Desktop/Hackathon/Cleaned_BILLI/"

Output_folder = "/Users/maximegillot/Desktop/Projects/AudioTranscriptAndSynthesis/Hackathon/MD_Comparaison/"

similarity_list = []
dic = {}


for fam_funct, billi_classes in data_dictionary.items():
    for billi_class, similarity in billi_classes.items():

        if(similarity in similarity_list):
            print(similarity, "already in list")
        else:
            similarity_list.append(similarity)
            dic[similarity] = [fam_funct,billi_class]

        # print(similarity)
            

similarity_list.sort(reverse=True)
# print(similarity_list)


for i in range(50):
    similarity = similarity_list[i]
    # print(similarity)
    print(similarity, "-", dic[similarity])



header = "# RAPPORT DE GAP ANALYSIS\n\n"
result = "## Compariasons\n\n"

for i in range(50):
    similarity = similarity_list[i]
    # print(similarity)
    print(similarity, "-", dic[similarity])

    fam_path = FAM_dir + dic[similarity][0] + ".java"
    billi_path = BILLI_dir + dic[similarity][1]


    with open(fam_path, 'r') as fam:
            fam_code = fam

    with open(billi_path, 'r') as billi:
            billi_code = billi

    # fam_description, billi_description, code_comparaion = compare_codes_with_description(fam_code, billi_code)
    code_comparaion = compare_code(fam_code, billi_code)
    

    # print(fam_description)

    # print(billi_description)

    print(code_comparaion)


    # result = f"## FAM DESCRIPTION\n\n{dic[similarity][0]}.java\n\n{fam_description}\n\n"
    # result += f"## BILLI DESCRIPTION\n\n{dic[similarity][1]}\n\n{billi_description}\n\n"
    result += f"### Comparaison {i+1}\n\nFAM source : _{dic[similarity][0]}.java_\n\nBILLI source: _{dic[similarity][1]}_\n\n{code_comparaion}\n\n"


    # file_path = Output_folder + dic[similarity][0] + ".md"

    # f = open(file_path,"a")
    # f.write(result)
    # f.close()


llm = get_llm(3)                
chain = LLMChain(llm=llm, prompt=GAP_SUMMARY)
summary = chain.run({'documentation': result})

final_doc = f"{header}## Résumé\n\n{summary}\n\n{result}"

file_path_pdf = Output_folder + "Rapport de GAP.pdf"

pdf = MarkdownPdf(toc_level=2)
pdf.add_section(Section(final_doc))
pdf.save(file_path_pdf)

from utils.prompts import CODE_DOCUMENTATION, DOCUMENTATION_SUMMARY
from utils.compare_vdb import get_llm

# from prompts import CODE_DOCUMENTATION, DOCUMENTATION_SUMMARY
# from compare_vdb import get_llm

from requests_aws4auth import AWS4Auth
import boto3
import os
import asyncio

from langchain.llms.bedrock import Bedrock
from langchain_community.chat_models import BedrockChat

from langchain.chains import LLMChain
from langchain_community.callbacks import get_openai_callback

from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
from markdown_pdf import MarkdownPdf, Section

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


def split_string(input_string, size=80000):
    return [input_string[i:i + size] for i in range(0, len(input_string), size)]




class DoucmentationBuilder:

    def __init__(self,docs,llm, target_audience, input_folder, output_folder) -> None:
        self.docs = docs
        self.llm = llm
        self.target_audience = target_audience
        self.input_folder = input_folder
        self.output_folder = output_folder
        

    async def async_generate(self, chain, code, target, metadata):
        with get_openai_callback() as cb:
            resp = await chain.arun({'code': code, 'target': target})
        return metadata, resp, cb.total_cost

        
    # async def generate_documentation(self):

    #     chain = LLMChain(llm=self.llm,prompt=CODE_DOCUMENTATION)

    #     task = []

    #     for document in self.docs:
    #         if (('content_type' not in document.metadata.keys()) or (document.metadata['content_type'] == 'functions_classes')):
    #             metadata = document.metadata
    #             code = document.page_content

    #             task.append(self.async_generate(chain=chain, code=code, target=self.target_audience, metadata=metadata))

    #     results = await asyncio.gather(*task)

        
    #     pdf = MarkdownPdf(toc_level=2)


    #     # markdown_doc =  "# Documentation pour " + self.target_audience + "\n\n" 
    #     markdown_doc =  "# Documentation de FAM\n\n" 


    #     documentation = ""

    #     for metadata, resp, cost in results:

    #         path = metadata['source'].replace(self.input_folder, "")
    #         id = os.path.basename(path)

    #         documentation += f"## {id}\n\n`File path: {path}`\n\n{resp}\n\n"

    #         # print(id)
    #         # print(resp)

    #     # file_path = f"{self.output_folder}/TOD documentation.md"

    #     # f = open(file_path,"w")
    #     # f.write(markdown_doc)
    #     # f.close()



    #     file_path_pdf = f"{self.output_folder}/TOD documentation.pdf"

    #     pdf.add_section(Section(markdown_doc))

    #     pdf.save(file_path_pdf)

        
    def generate_doccumentation_seq(self):

        chain = LLMChain(llm=self.llm,prompt=CODE_DOCUMENTATION)


        documentation = ""

        table_of_content = ""

        for document in self.docs:
            if (('content_type' not in document.metadata.keys()) or (document.metadata['content_type'] == 'functions_classes')):
                metadata = document.metadata
                code = document.page_content

                result = chain.run({'code': code, 'target': self.target_audience})
                path = metadata['source'].replace(self.input_folder, "")
                id = os.path.basename(path)

                table_of_content += f'[{id}](#{id})\n'

                print(id)
                print(result)
                documentation += f'### {id} <a name="{id}"></a> \n\n_File path: {path}_\n\n{result}\n\n'


                    
        chain = LLMChain(llm=self.llm, prompt=DOCUMENTATION_SUMMARY)
        summary = chain.run({'documentation': documentation, 'target': self.target_audience})


        markdown_doc =  f"# DOCUMENTATION DE FAM\n\n## Résumé\n\n{summary}\n\n## Description des fonctions\n\n{documentation}" 


        file_path_pdf = f"{self.output_folder}/FAM documentation.pdf"

        pdf = MarkdownPdf(toc_level=2)
        pdf.add_section(Section(markdown_doc))
        pdf.save(file_path_pdf)

        return summary



def describe_codebase(input_folder, target, output_folder):

    loader = GenericLoader.from_filesystem(
        input_folder,
        suffixes=[".java"],
        parser=LanguageParser(language=Language.JAVA, parser_threshold=0),
    )

    docs = loader.load()
    len(docs)
    llm = get_llm(3)

    documentation_builder = DoucmentationBuilder(
        docs=docs,
        llm=llm,
        target_audience=target,
        input_folder=input_folder,
        output_folder=output_folder,
        )
    
    # asyncio.run(documentation_builder.generate_documentation())
    return documentation_builder.generate_doccumentation_seq()



    # code = ""

    # for document in docs:
    #     if (('content_type' not in document.metadata.keys()) or (document.metadata['content_type'] == 'functions_classes')):
    #         code += document.page_content + "\n\n"


    # description = ""

    # print(len(code))

    # if len(code) > 80000:
    #     code_list = split_string(code)
    #     descriptions = []
    #     for code_piece in code_list:
    #         chain = LLMChain(llm=llm,prompt=CODE_BASE_DESCRIPTION)
    #         temp_description = chain.run({'code': code_piece, 'question': question})
    #         print(temp_description)
    #         descriptions.append(temp_description)
        
    #     global_description = ""
    #     for description_piece in descriptions:
    #         global_description += description_piece + "\n\n"

    #     chain = LLMChain(llm=llm,prompt=CODE_BASE_DESCRIPTION)
    #     description = chain.run({'code': global_description, 'question': question})

    # else:
    #     chain = LLMChain(llm=llm,
    #                  prompt=CODE_BASE_DESCRIPTION)
    #     description = chain.run({'code': code, 'question': question})




    # return description



# describe_codebase(
#     input_folder="/Users/maximegillot/Desktop/Hackathon/FAM_doc_test",
#     target="un businessman qui ne s'y connait pas en programmation",
#     output_folder="/Users/maximegillot/Desktop/Projects/AudioTranscriptAndSynthesis/Hackathon/MD_Comparaison"
# )
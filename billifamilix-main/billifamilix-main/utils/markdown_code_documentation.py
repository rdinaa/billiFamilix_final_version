# from utils.bedrock import ask_llm
from bedrock import ask_llm
import os
import warnings

warnings.filterwarnings("ignore")
from pprint import pprint

from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)

BASIC_PROMPT = "Give a quick summary of the function goal. Then explain functionalities of the following Java code segment in a couple of bullet points"



def generate_documentation(
        root_folder,
        output_folder,
        ):
    
    loader = GenericLoader.from_filesystem(
        root_folder,
        suffixes=[".java"],
        parser=LanguageParser(language=Language.JAVA, parser_threshold=0),
    )

    docs = loader.load()
    len(docs)

    for document in docs:

        document_path = document.metadata['source']
        document_name = os.path.basename(document_path)
        class_name = document_name.split(".")[0]

        file_path = output_folder + class_name + ".md"
        
            
        if (('content_type' in document.metadata.keys()) and (document.metadata['content_type'] == 'simplified_code')):
            # print(document.page_content)
            content = document.page_content

            libraries = []
            splits = content.split(";")
            # print(split)
            for split in splits:
                if ("import com" in split):
                    lib = split.split(" ")[-1]
                    lib = lib.split(".")[-1]
                    libraries.append(lib)
                    # print(lib)

            result = "\n".join(["[[" + lib + "]]" for lib in libraries])
            

        # if (document.metadata['content_type'] == 'functions_classes'):

        #     print("generating doc for: ", document_name)

        #     content = document.page_content


        #     reponse = ask_llm(
        #         instruction=BASIC_PROMPT,
        #         data=content
        #         )
        #     result = reponse + "\n\n"

            # print(reponse)

            f = open(file_path,"a")
            f.write(result)
            f.close()


# generate_documentation(
#     root_folder="/Users/maximegillot/Desktop/Hackathon/Cleaned_FAM",
#     output_folder="/Users/maximegillot/Desktop/LogSeq Data/pages/"
# )
        
# generate_documentation(
#     root_folder="/Users/maximegillot/Desktop/Hackathon/BILLI - invoiceCalculation/bc/src/main/java/com/coface/corp/invoiceCalculation",
#     output_folder="/Users/maximegillot/Desktop/LogSeq Data/pages/"
# )
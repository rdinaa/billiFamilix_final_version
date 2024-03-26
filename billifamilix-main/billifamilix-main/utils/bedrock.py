import boto3
import os
import json
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv('.env',
            verbose=False)

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')


# Define a function to call the bedrock API for code summarization
def explain_code(code):
    # Call the Bedrock client
    bedrock = boto3.client(service_name='bedrock-runtime',
                           region_name='us-east-1',
                           aws_access_key_id=AWS_ACCESS_KEY_ID,
                           aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    # Tweak your preferred model parameters, prompt and assistant information
    body = json.dumps({
        "prompt": f"\n\nHuman: Explain functionalities of the following Java code segment in a couple of bullet points {code}\n\nAssistant: Explain well to a non-technical person what is happening within the provided code",
        "max_tokens_to_sample": 500,
        "temperature": 0.2,
        "top_p": 0.9,})

    # Define the type of model that will be used
    # modelId = 'anthropic.claude-v2'
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    accept = 'application/json'
    contentType = 'application/json'

    # Call the Bedrock API
    response = bedrock.invoke_model(body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"type": "text",
                                         "text": f"\n\nHuman: Donne une courte phrase qui résume ce que fait ce code puis Explique les fonctions en quelques bullet point : {code}\n\nAssistant:"}],
                        }
                    ],
                }
            ),
                                    modelId=model_id,
                                    accept=accept,
                                    contentType=contentType)
    result = json.loads(response.get('body').read())
    input_tokens = result["usage"]["input_tokens"]
    output_tokens = result["usage"]["output_tokens"]
    output_list = result.get("content", [])

    print("Invocation details:")
    print(f"- The input length is {input_tokens} tokens.")
    print(f"- The output length is {output_tokens} tokens.")

    print(f"- The model returned {len(output_list)} response(s):")
    for output in output_list:
        print(output["text"])

    return result["content"][0]["text"]


def ask_llm(
        instruction="",
        data="",
        question="",
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        service_name="bedrock-runtime",
        region_name="us-east-1",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
):
    bedrock = boto3.client(service_name=service_name,
                           region_name=region_name,
                           aws_access_key_id=aws_access_key_id,
                           aws_secret_access_key=aws_secret_access_key)

    try:
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"type": "text",
                                         "text": f"\n\nHuman: {instruction}\n\n{data}\n\n{question} \n\n Assistant:"}],
                        }
                    ],
                }
            ),
        )

        # Process and print the response
        result = json.loads(response.get("body").read())
        input_tokens = result["usage"]["input_tokens"]
        output_tokens = result["usage"]["output_tokens"]
        output_list = result.get("content", [])

        print("Invocation details:")
        print(f"- The input length is {input_tokens} tokens.")
        print(f"- The output length is {output_tokens} tokens.")

        print(f"- The model returned {len(output_list)} response(s):")
        for output in output_list:
            print(output["text"])

        return result["content"][0]["text"]

    except ClientError as err:
        print(f"Couldn't invoke Claude 3 Haiku. Here's why: %s: %s",
              err.response["Error"]["Code"],
              err.response["Error"]["Message"])
        raise

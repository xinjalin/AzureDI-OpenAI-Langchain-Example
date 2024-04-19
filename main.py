from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate

from output_pasers import document_intel_parser

import os
from dotenv import load_dotenv


def document_review(analysis_result) -> str:
    """
    Takes in an analysed document from Azure DI and parses the content to an OpenAI LLM.
    The LLM is asked to give a summary (300 characters Max) and an interesting fact about the document
    Model: gpt-3.5-turbo
    """
    print("""
    Sending scanned document to OpenAI
    ----------------------------------""")
    # Extract content from the analysis result
    content = ""
    for page in analysis_result.pages:
        for line in page.lines:
            content += line.content + "\n"

    # template
    document_review_template = """
    given this document {document_content} I want you to analyse and give a:
    1: summary (300 characters Maximum)
    2: interesting fact
    \n{format_instructions}
    """

    # prompt template config
    document_prompt_template = PromptTemplate(
        input_variables=["document_content"],
        template=document_review_template,
        partial_variables={"format_instructions": document_intel_parser.get_format_instructions()}
    )

    # create an instance of OpenAI
    llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')
    # creates a chain passing in the llm and template
    chain = LLMChain(llm=llm, prompt=document_prompt_template)
    # calls the invoke method on the chain to execute the template on the llm
    res = chain.invoke(input={"document_content": content})

    print("""
    OpenAI Response
    ---------------""")
    # res is a dictionary with 2 indexes ["document_content"] and ["text"].
    # document is the information sent to the llm and text is the response from the llm.
    return res["text"]


def analyse_document(url: str):
    """
    Passes an image of scanned document to Azure Document Intelligence and returns the OCR result
    model: prebuilt-read
    """
    print("""
    Sending document image to Azure DI
    ----------------------------------""")

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )  # using AzureKeyCredential ensures encryption of API keys when communicating with Azure Document Intelligence

    poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-read", url)
    return poller.result()


def azure_document_summary(result):
    """
    Takes an analysed document and displays summary information in terminal
    """
    print("""
    Document Summary
    ----------------""")

    total_confidence = 0
    total_words = 0

    for page in result.pages:
        print(f"Document Page {page.page_number} has {len(page.lines)} lines and {len(page.words)} words.")

        for word in page.words:
            total_confidence += word.confidence
            total_words += 1

        if total_words > 0:
            average_confidence = total_confidence / total_words
            print(f"Average Confidence: {round(average_confidence, 2)}%")

        total_confidence = 0
        total_words = 0


if __name__ == "__main__":
    # environment variables
    load_dotenv()

    # Azure Document Intelligence Connection Credentials
    key = os.getenv("AZURE_KEY")
    endpoint = os.getenv("AZURE_ENDPOINT")

    # document for analysis
    documentURL = "https://idodata.com/wp-content/uploads/2024/02/MASArticle-scaled.jpg"

    # send the document to Azure Document Intelligence
    azure_analysis_result = analyse_document(documentURL)

    # display a summary of the analysed document
    azure_document_summary(azure_analysis_result)

    # send the analysed document to OpenAI LLM
    llm_response = document_review(azure_analysis_result)
    print(llm_response)

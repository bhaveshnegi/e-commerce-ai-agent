from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from dotenv import load_dotenv
import os
from langchain_aws import ChatBedrock

load_dotenv()
llm_provider = os.getenv("LLM", "HF").upper()

def get_llm():

    # llm = HuggingFaceEndpoint(
    #     repo_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    #     temperature=0.3,
    #     max_new_tokens=50,
    #     huggingfacehub_api_token=os.getenv("HF_TOKEN"),
    # )

    # chat_model = ChatHuggingFace(llm=llm)

    # return chat_model

    if llm_provider == "AWS":
        
        # Initialize AWS Bedrock model
        model_base = ChatBedrock(
            model_id="mistral.mistral-7b-instruct-v0:2",
            region_name="ap-south-1",
        )
        print("--- LLM initialized with AWS Bedrock ---")
        return model_base

    else:
        # Default to Hugging Face
        from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
        
        hf_token = os.getenv("HUGGINGFACE_API_KEY")
        if hf_token:
            os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token
            os.environ["HF_TOKEN"] = hf_token
            os.environ["HUGGINGFACE_API_TOKEN"] = hf_token

        # llm = HuggingFaceEndpoint(
        #     repo_id="mistralai/Mistral-7B-Instruct-v0.2",
        #     huggingfacehub_api_token=hf_token,
        #     temperature=0.1,
        #     max_new_tokens=1024,
        # )
        llm = HuggingFaceEndpoint(
            repo_id="Qwen/Qwen2.5-Coder-32B-Instruct",
            temperature=0.3,
            max_new_tokens=512,
            huggingfacehub_api_token=hf_token,
        )
        model_base = ChatHuggingFace(llm=llm)
        print(f"--- LLM initialized with Hugging Face (Qwen/Qwen2.5-Coder-32B-Instruct) ---")
        return model_base

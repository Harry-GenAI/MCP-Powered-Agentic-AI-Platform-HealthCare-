from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
import os
from logger import logger
from dotenv import load_dotenv

load_dotenv()

login(os.getenv("HF_token"))

#download the model and save to the local folder
name="meta-llama/Llama-3.2-1B-Instruct"
tokenizer=AutoTokenizer.from_pretrained(name)
model=AutoModelForCausalLM.from_pretrained(name)

tokenizer.save_pretrained("./local_model")
model.save_pretrained("./local_model")

logger.info("model saved to ./local_model")

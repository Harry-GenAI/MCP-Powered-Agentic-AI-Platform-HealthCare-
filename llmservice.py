import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from logger import logger
import asyncio
import os


# EKS/Kubernetes can mount the model here from an init container or persistent volume.
MODEL_PATH = os.getenv("MODEL_PATH", "./local_model")

logger.info(f"Loading model from {MODEL_PATH}")

#CUDA
if torch.cuda.is_available():
    MODEL_DEVICE = "cuda"
    MODEL_DTYPE = torch.float16
else:
    MODEL_DEVICE = "cpu"
    MODEL_DTYPE = torch.float32

#Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)

#Load model
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=MODEL_DTYPE,
    local_files_only=True
).to(MODEL_DEVICE)

model.eval()
logger.info(f"Model loaded on {MODEL_DEVICE}")

def generate_reply_sync(prompt: str):
    # Llama 3.2 uses different tags, let's use the tokenizer's built-in tool
    inputs = tokenizer(prompt, return_tensors="pt").to(MODEL_DEVICE)
    
    with torch.inference_mode(): # Faster than no_grad()
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            do_sample=True,      # Small models need a little "creative" room to not loop
            temperature=0.1,     # But keep it low for accuracy
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id
        )

    prompt_length = len(inputs["input_ids"][0])#explanation-II
    answer = tokenizer.decode(outputs[0][prompt_length:], skip_special_tokens=True).strip()
    
    return answer

async def generate_reply(prompt: str):
    return await asyncio.to_thread(generate_reply_sync, prompt)

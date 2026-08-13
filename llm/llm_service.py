import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from utils.logger import logger
import asyncio
import os

from middleware.retry import retry
from middleware.timeout import timeout
from middleware.rate_limit import rate_limit


MODEL_PATH = os.getenv("MODEL_PATH", "./local_model")

logger.info(f"Loading model from {MODEL_PATH}")


# CUDA / CPU
if torch.cuda.is_available():
    MODEL_DEVICE = "cuda"
    MODEL_DTYPE = torch.float16
else:
    MODEL_DEVICE = "cpu"
    MODEL_DTYPE = torch.float32


# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH,
    local_files_only=True
)


# Load model
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=MODEL_DTYPE,
    local_files_only=True
).to(MODEL_DEVICE)

model.eval()

logger.info(f"Model loaded on {MODEL_DEVICE}")


def generate_reply_sync(prompt: str):

    inputs = tokenizer(
        prompt,
        return_tensors="pt"
    ).to(MODEL_DEVICE)

    with torch.inference_mode():

        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            do_sample=True,
            temperature=0.1,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id
        )

    prompt_length = len(inputs["input_ids"][0])

    answer = tokenizer.decode(
        outputs[0][prompt_length:],
        skip_special_tokens=True
    ).strip()

    return answer


@retry
@timeout(60)
@rate_limit(1,1)
async def generate_reply(prompt: str):

    return await asyncio.to_thread(
        generate_reply_sync,
        prompt
    )
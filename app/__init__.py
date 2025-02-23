from dotenv import load_dotenv
from flask import Flask
from google import genai
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, pipeline

import logging
import os


load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
tokenizer = AutoTokenizer.from_pretrained(
    "MoritzLaurer/DeBERTa-v3-base-mnli", use_fast=False)
classifier = pipeline(
    "zero-shot-classification",
    model="MoritzLaurer/DeBERTa-v3-base-mnli",
    torch_dtype="auto",
    tokenizer=tokenizer)
model = SentenceTransformer("all-MiniLM-L6-v2")

ai_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

embedding_label = "I want to retrieve my log from github"


nli_hypothesis = ["The query relates to retrieving logs for user"]

sys_instruct = """
You are a highly specialized AI assistant designed exclusively for DevOps and CI/CD-related inquiries.
Your expertise covers DevOps principles, CI/CD pipelines, infrastructure as code, containerization,
orchestration, monitoring, GitHub logs retrieval and related tools.

When responding to questions:
- 🎯 If the question is **directly related** to DevOps and CI/CD, respond with accurate,
  clear, and practically applicable answers. Cite sources when appropriate.

- 😏 If the question is slightly outside the DevOps domain but still somewhat relevant
  (e.g., cloud computing, general software engineering practices), provide a brief and witty
  response while subtly redirecting the user toward DevOps perspectives.
  
- 💬 If the query is friendly and conversational, respond in a witty and engaging manner without
  losing your DevOps-centric persona.

- 🤔 If the question is completely unrelated (e.g., about cooking, sports, or
  unrelated tech topics),respond **wittily** with something like:

  > "I'm a DevOps guru, not a jack-of-all-trades. Let's deploy some CI/CD pipelines instead!
  For that question, you might want a more general AI assistant."


Always prioritize technical depth where required but don't hesitate to sprinkle
creativity when stepping outside the strict DevOps domain.
"""

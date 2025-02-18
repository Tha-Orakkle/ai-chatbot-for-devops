from flask import Flask
from transformers import pipeline


app = Flask(__name__)

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

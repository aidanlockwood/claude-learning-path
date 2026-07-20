import re
from anthropic import Anthropic

import voyageai

from dotenv import load_dotenv

load_dotenv()

## From the multi turn conversations lesson
def api_client_setup(model = "claude-haiku-4-5"):
    client = Anthropic()

    print(f'Initialised {client} with the model: {model}')
    return client, model

client, model = api_client_setup()
voyage_client = voyageai.Client()

# Embedding Generation
def generate_embedding(chunks, model="voyage-3-large", input_type="query"):
    is_list = isinstance(chunks, list)
    input = chunks if is_list else [chunks]
    result = voyage_client.embed(input, model=model, input_type=input_type)
    return result.embeddings if is_list else result.embeddings[0]

# Chunk by a set number of charactesr
def chunk_by_char(text, chunk_size=150, chunk_overlap=20):
    chunks = []
    start_idx = 0

    while start_idx < len(text):
        end_idx = min(start_idx + chunk_size, len(text))

        chunk_text = text[start_idx:end_idx]
        chunks.append(chunk_text)

        start_idx = (
            end_idx - chunk_overlap if end_idx < len(text) else len(text)
        )

    return chunks

# Chunk by sentence
def chunk_by_sentence(text, max_sentences_per_chunk=5, overlap_sentences=1):
    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks = []
    start_idx = 0

    while start_idx < len(sentences):
        end_idx = min(start_idx + max_sentences_per_chunk, len(sentences))

        current_chunk = sentences[start_idx:end_idx]
        chunks.append(" ".join(current_chunk))

        start_idx += max_sentences_per_chunk - overlap_sentences

        if start_idx < 0:
            start_idx = 0

    return chunks

# Chunk by section
def chunk_by_section(document_text):

    # Looks for a newline character to separate the chunks 
    pattern = r"\n## "
    return re.split(pattern, document_text)
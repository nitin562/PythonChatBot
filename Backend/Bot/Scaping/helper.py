import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
import numpy as np

# model_name = "all-MiniLM-L6-v2"  # it is small, fast and good for embedding and tokens
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")


# Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[
        0
    ]  # First element of model_output contains all token embeddings
    input_mask_expanded = (
        attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    )
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9
    )


def embedd_a_chunk(chunk):
    encoded_input = tokenizer(chunk, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        model_output = model(**encoded_input)
    sentence_embedding = mean_pooling(model_output, encoded_input["attention_mask"])
    normalized_embedding = F.normalize(sentence_embedding, p=2, dim=1)
    return normalized_embedding.squeeze().numpy()


def embedd(scrapedContent):  # a list =text
    try:
        tokenLimit = tokenizer.model_max_length
        print(tokenLimit)
        embeddings = {}

        for key in scrapedContent:
            value = scrapedContent[key]
            text = " ".join(value)

            # Step 1: Tokenize full text
            tokens = tokenizer.encode(text, add_special_tokens=False)

            # Step 2: Chunk into segments of max_tokens
            chunks = []
            if len(tokens) < tokenLimit:
                chunks = [tokens]
            else:
                chunks = [
                    tokens[i : i + tokenLimit] for i in range(0, len(tokens), tokenLimit)
                ]

            # Step 3: Decode each chunk back to text
            texts = [
                tokenizer.decode(chunk, clean_up_tokenization_spaces=True)
                for chunk in chunks
            ]

            # Step 4: Encode each chunk
            all_embeddings = []
            for t in texts:
                print("Hey this is the line", t)
                print("\n")
                embedding_chunk = embedd_a_chunk(t)
                all_embeddings.append(embedding_chunk)

            # Average pooling across all chunks

            embeddings[key] = {"final": all_embeddings, "text": texts}

        return (True,embeddings)
    except Exception as e:
        print("Transformer Error - ",e)
        return (False,str(e))
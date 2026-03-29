from sentence_transformers import CrossEncoder

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
model.save("models/cross-encoder-ms-marco-MiniLM-L-6-v2")
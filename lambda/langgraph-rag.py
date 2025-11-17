import os
import google.generativeai as genai
from langgraph.graph import StateGraph, END
from db import search_docs

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

class RAGState(dict):
    pass

def embed(q: str):
    res = genai.embed_content(
        model=os.environ["GEMINI_EMBED_MODEL"],
        content=q
    )
    return res["embedding"]

def step_embed(state: RAGState):
    return {"query_embedding": embed(state["question"])}

def step_retrieve(state: RAGState):
    emb = state["query_embedding"]
    docs = search_docs(emb)
    return {"docs": docs}

def step_answer(state: RAGState):
    ctx = "\n\n".join([d["text"] for d in state["docs"]])

    model = genai.GenerativeModel(os.environ["GEMINI_MODEL"])
    prompt = f"Use this context to answer:\n\n{ctx}\n\nQuestion: {state['question']}"
    ans = model.generate_content(prompt)

    return {"answer": ans.text}

def run_rag(question: str):
    builder = StateGraph(RAGState)

    builder.add_node("embed", step_embed)
    builder.add_node("retrieve", step_retrieve)
    builder.add_node("answer", step_answer)

    builder.set_entry_point("embed")
    builder.add_edge("embed", "retrieve")
    builder.add_edge("retrieve", "answer")
    builder.add_edge("answer", END)

    graph = builder.compile()
    out = graph.invoke({"question": question})

    return out["answer"]

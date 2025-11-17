from datetime import datetime
from ganga_ai.vector_store import vector_store
from ganga_ai.config import config

RESULT_FILE = "eval_results.md"


def append_to_markdown(question: str, answer: str):
    """
    Append question and answer to the results file
    """
    header = f"## Question: {question}\n"
    answer_block = f"**Answer:**\n\n{answer}\n\n---\n"
    with open(RESULT_FILE, "a") as f:
        f.write(header)
        f.write(answer_block)


def evaluate_rag():
    """
    Runs the two evaluation queries against the Vector_Store
    and stores results in eval_results.md
    """
    now = datetime.now().isoformat()
    metadata = (
        f"\n# Evaluation Run – {now}\n\n"
        f"- **LLM model:** {config.llm_model}\n"
        f"- **Embedding model:** {config.embedding_model}\n"
        f"- **Embedding / transformer dimensions:** {config.transformer_dimension}\n\n"
    )
    with open(RESULT_FILE, "a", encoding="utf-8") as f:
        f.write(metadata)
    questions = [
        "/no_think What is ganga?",
        "/no_think Write a script for a simple ganga job that executes on a local backend and prints hello world",
        '/no_think Write a script using the ganga software that takes a pdf called lhc.pdf and splits it into individual pages. It then uses ArgSplittter to submit one subjob per page. Each subjob will count the number of times the word "it" occurs in the page. Then finally merge the subjobs to get the total number of "it" in the whole pdf',
        "Write tests for the above script",
    ]
    for question in questions:
        print(f"\nQuestion: {question}\n")
        response = vector_store.query_vector_store(question)
        print(f"\n Response: {response}")
        append_to_markdown(question, str(response))
    print(f"\nEvaluation completed. Results available in {RESULT_FILE}\n")

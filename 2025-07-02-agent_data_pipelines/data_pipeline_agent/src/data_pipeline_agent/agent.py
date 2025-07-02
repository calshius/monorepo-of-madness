import os
import asyncio
import time
from langgraph.graph import StateGraph, END, START
from langchain_google_genai import ChatGoogleGenerativeAI
from data_pipeline_agent.tools.fetch_pdfs import fetch_pdfs_node
from data_pipeline_agent.tools.cleanup_tmp import cleanup_tmp_node

NO_LLM = os.getenv("NO_LLM", "false").lower() == "true"

if NO_LLM:
    from data_pipeline_agent.tools.pdf_to_csv_no_llm import pdf_to_csv_node
    from data_pipeline_agent.tools.transpose_no_llm import transpose_node
    from data_pipeline_agent.tools.to_json_no_llm import to_json_node
else:
    from data_pipeline_agent.tools.pdf_to_csv import pdf_to_csv_node
    from data_pipeline_agent.tools.transpose import transpose_node
    from data_pipeline_agent.tools.to_json import to_json_node

DATA_PDF_PATH = os.getenv("DATA_PDF_PATH", "../../data.pdf")


async def main():
    start_time = time.time()
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    llm = (
        ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            google_api_key=gemini_api_key,
        )
        if not NO_LLM
        else None
    )

    workflow = StateGraph(dict)
    workflow.add_node("fetch_pdfs", fetch_pdfs_node)
    workflow.add_node("extract_pdf_to_csv", pdf_to_csv_node)
    workflow.add_node("transpose_and_geolocate", transpose_node)
    workflow.add_node("output_json", to_json_node)
    workflow.add_node("cleanup_tmp", cleanup_tmp_node)
    workflow.add_edge(START, "fetch_pdfs")
    workflow.add_edge("fetch_pdfs", "extract_pdf_to_csv")
    workflow.add_edge("extract_pdf_to_csv", "transpose_and_geolocate")
    workflow.add_edge("transpose_and_geolocate", "output_json")
    workflow.add_edge("output_json", "cleanup_tmp")
    workflow.add_edge("cleanup_tmp", END)

    app = workflow.compile()
    state = {"pdf_path": DATA_PDF_PATH}
    if llm:
        state["llm"] = llm

    await app.ainvoke(state)

    elapsed = time.time() - start_time
    print(f"\nWorkflow completed in {elapsed:.2f} seconds.")


if __name__ == "__main__":
    asyncio.run(main())

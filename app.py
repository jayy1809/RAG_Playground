import asyncio
import streamlit as st


def initialize_session_state():

    if "search_performed_1" not in st.session_state:

    if "search_performed_1" not in st.session_state:
        st.session_state.search_performed_1 = False
    if "search_performed_2" not in st.session_state:
    if "search_performed_2" not in st.session_state:
        st.session_state.search_performed_2 = False
    if "reranking_performed_1" not in st.session_state:
    if "reranking_performed_1" not in st.session_state:
        st.session_state.reranking_performed_1 = False
    if "reranking_performed_2" not in st.session_state:
    if "reranking_performed_2" not in st.session_state:
        st.session_state.reranking_performed_2 = False
    if "search_results" not in st.session_state:
        st.session_state.search_results = {"_1": {}, "_2": {}}
    if "reranking_results" not in st.session_state:
        st.session_state.reranking_results = {"_1": False, "_2": False}
    if "file_uploaded" not in st.session_state:
        st.session_state.file_uploaded = False
    if "index_button_2_clicked" not in st.session_state:
    if "index_button_2_clicked" not in st.session_state:
        st.session_state.index_button_2_clicked = False
    if "index_button_1_clicked" not in st.session_state:
    if "index_button_1_clicked" not in st.session_state:
        st.session_state.index_button_1_clicked = False
        
def get_embedding_models():
    return [
        "",
        "llama-text-embed-2",
        "multilingual-e5-large",
        "embed-english-v3.0",
        "embed-multilingual-v3.0",
        "embed-english-light-v3.0",
        "embed-multilingual-light-v3.0",
        "embed-english-v2.0",
        "embed-english-light-v2.0",
        "embed-multilingual-v2.0",
        "jina-embeddings-v3",
    ]
    

def get_dimensions(dense_embedding_model: str) -> list:
    model_to_dimensions = {
        "llama-text-embed-2": [1024, 2048, 768, 512, 384],
        "multilingual-e5-large": [1024],
        "embed-english-v3.0": [1024],
        "embed-multilingual-v3.0": [1024],
        "embed-english-light-v3.0": [384],
        "embed-multilingual-light-v3.0": [384],
        "embed-english-v2.0": [4096],
        "embed-multilingual-v2.0": [768],
        "jina-embeddings-v3": [1024],
    }
    return model_to_dimensions.get(dense_embedding_model, [])

def reset_first_stage_result(pipeline_key):

    if pipeline_key == "_1":

    if pipeline_key == "_1":
        st.session_state.search_performed_1 = False
        st.session_state.search_results[pipeline_key] = {}
    else:
        st.session_state.search_performed_2 = False
        st.session_state.search_results[pipeline_key] = {}


def reset_second_stage_result(pipeline_key):

    if pipeline_key == "_1":

    if pipeline_key == "_1":
        st.session_state.reranking_performed_1 = False
        st.session_state.reranking_results[pipeline_key] = False
    else:
        st.session_state.reranking_performed_2 = False
        st.session_state.reranking_results[pipeline_key] = False


def perform_search_callback(pipeline_key):

    if pipeline_key == "_1":

    if pipeline_key == "_1":
        st.session_state.search_performed_1 = True

    else:
        st.session_state.search_performed_2 = True



def perform_reranking_callback(pipeline_key):

    if pipeline_key == "_1":

    if pipeline_key == "_1":
        st.session_state.reranking_performed_1 = True

    else:
        st.session_state.reranking_performed_2 = True


def display_results_tabs(key: str):


    tab1, tab2 = st.tabs(["Search Results", "Reranking Results"])


    with tab1:
        if key == "_1" and st.session_state.search_performed_1:
            display_search_results(st.session_state.search_results[key])

        elif key == "_2" and st.session_state.search_performed_2:
            display_search_results(st.session_state.search_results[key])

        else:
            st.info("Run a search to see results here.")


    with tab2:
        if key == "_1" and st.session_state.reranking_performed_1:
            display_reranking_results(st.session_state.reranking_results[key])

        elif key == "_2" and st.session_state.reranking_performed_2:
            display_reranking_results(st.session_state.reranking_results[key])

        else:
            st.info("Run reranking to see results here.")




def display_search_results(results):


    if not results:
        st.info("No search results available.")
        return

    st.json(results)


def display_reranking_results(results):


    if not results:
        st.info("No reranking results available.")
        return


    st.success("Here are the reranking results:")



async def hybrid_search_pipeline(key: str, filename: str):

    st.warning(
        "By default, dot product similarity is used for the hybrid search."
    )

    dense_embedding_model = st.selectbox(
        "Select Dense Embedding Model:",
        get_embedding_models(),
        key="dense_embedding_model" + key,
    )

    dimensions = get_dimensions(dense_embedding_model)

    dense_dimension = st.selectbox(
        "Enter Dimension of the Dense Model:",
        dimensions,
        key="dense_dimension" + key,
        key="dense_dimension" + key,
    )


    if dense_embedding_model and dense_dimension:

        if st.button("Create Index and Upsert Dataset", key="create_index" + key):
            
            payload = {
                "file_name" : filename,
                "embed_model" : dense_embedding_model,
                "similarity_metric" : "dotproduct",
                "dimension" : dense_dimension,
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://127.0.0.1:8000/index-upsert",
                    json = payload,
                )
                
                if response.status_code == 200:
                    st.success("Index created and dataset upserted successfully!")
                    st.json(response.json())
                else:
                    st.error(f"Index creation and dataset upsert failed")
            
            st.session_state.index_button_1_clicked = True

        if st.session_state.index_button_1_clicked:
            query = st.text_area(
                "Enter your query or question:", key="query" + key
            )
            top_k = st.text_input(
                "Enter the value for top_k:", key="top_k" + key
            )
            alpha = st.slider(
                "Select alpha value (between 0 and 1):",
                min_value=0.0,
                max_value=1.0,
                step=0.1,
                value=0.5,
                key="alpha" + key,
            )

            if query and top_k and alpha:
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Perform Similarity Search", key="perform_search" + key, on_click=perform_search_callback, args=(key,)):
                        
                        payload = {
                            "is_hybrid" : True,
                            "file_name" : filename,
                            "embedding_model" : dense_embedding_model,
                            "dimension" : dense_dimension,
                            "query" : query,
                            "top_k" : top_k,
                            "alpha" : alpha,
                        }
                        
                        async with httpx.AsyncClient() as client:
                            response = await client.post(
                                "http://127.0.0.1:8000/query",
                                json = payload,
                            )
                            
                            if response.status_code == 200:
                                st.success("Search performed successfully!")
                                st.json(response.json())
                            else:
                                st.error(f"First stage retrieval failed")

                            st.session_state.search_results[key] = response.json()

                with col2:
                    if st.button("Reset Results", key="reset_similarity" + key, on_click=reset_first_stage_result, args=(key,)):
                        pass

            if st.session_state.search_results[key]:
                reranking_model = st.selectbox(
                    "Select Reranking Model:",
                    [
                        "",
                        "pinecone-rerank-v0",
                        "cohere-rerank-3.5",
                        "bge-reranker-v2-m3",
                        "rerank-v3.5",
                        "rerank-english-v3.0",
                        "rerank-multilingual-v3.0",
                        "jina-reranker-v2-base-multilingual",
                    ],
                    key="reranking_model" + key,
                )

                top_n = st.text_input(
                    "Enter the value for top_n:", key="top_n" + key
                )

                if reranking_model and top_n:
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("Perform Reranking", key="perform_reranking" + key, on_click=perform_reranking_callback, args=(key,)):
                            st.session_state.reranking_results[key] = True

                    with col2:
                        if st.button("Reset Results", key="reset_renaked" + key, on_click=reset_second_stage_result, args=(key,)):
                            pass
                else:
                    st.warning(
                        "Please select the reranking model and enter the top_n value."
                    )
    else:
        st.warning("Please select the required models and dimensions.")


async def dense_search_pipeline(key: str, filename: str):

    dense_embedding_model = st.selectbox(
        "Select Dense Embedding Model:",
        get_embedding_models(),
        key="dense_embedding_model" + key,
    )

    dimensions = get_dimensions(dense_embedding_model)

    dense_dimension = st.selectbox(
        "Enter Dimension of the Dense Model:",
        dimensions,
        key="dense_dimension" + key,
        key="dense_dimension" + key,
    )


    if dense_embedding_model and dense_dimension:

        similarity_metric = st.selectbox(
            "Enter Similarity Metric:",
            ["dotproduct", "cosine", "euclidean"],
            key="similarity_metric" + key,
            ["dotproduct", "cosine", "euclidean"],
            key="similarity_metric" + key,
        )

        if st.button("Create Index and Upsert Dataset", key="create_index" + key):
            
            payload = {
                "file_name" : filename,
                "embed_model" : dense_embedding_model,
                "similarity_metric" : similarity_metric,
                "dimension" : dense_dimension,
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://127.0.0.1:8000/index-upsert",
                    json = payload,
                )
                
                if response.status_code == 200:
                    st.success("Index created and dataset upserted successfully!")
                    st.json(response.json())
                else:
                    st.error(f"Index creation and dataset upsert failed")
            
            st.session_state.index_button_2_clicked = True

        if st.session_state.index_button_2_clicked:
            query = st.text_area(
                "Enter your query or question:", key="query" + key
            )
            top_k = st.text_input(
                "Enter the value for top_k:", key="top_k" + key
            )

            if query and top_k:
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Perform Similarity Search", key="perform_search" + key, on_click=perform_search_callback, args=(key,)):
                        
                        payload = {
                            "is_hybrid" : False,
                            "file_name" : filename,
                            "embedding_model" : dense_embedding_model,
                            "dimension" : dense_dimension,
                            "similarity_metric" : similarity_metric,
                            "query" : query,
                            "top_k" : top_k,
                        }
                        
                        async with httpx.AsyncClient() as client:
                            response = await client.post(
                                "http://127.0.0.1:8000/query",
                                json = payload,
                            )
                            
                            if response.status_code == 200:
                                st.success("Search performed successfully!")
                                st.json(response.json())
                            else:
                                st.error(f"First stage retrieval failed")
                                
                            st.session_state.search_results[key] = response.json()

                with col2:
                    if st.button("Reset Results", key="reset_similarity" + key, on_click=reset_first_stage_result, args=(key,)):
                        pass

            if st.session_state.search_results[key]:
                reranking_model = st.selectbox(
                    "Select Reranking Model:",
                    [
                        "",
                        "pinecone-rerank-v0",
                        "cohere-rerank-3.5",
                        "bge-reranker-v2-m3",
                        "rerank-v3.5",
                        "rerank-english-v3.0",
                        "rerank-multilingual-v3.0",
                        "jina-reranker-v2-base-multilingual",
                    ],
                    key="reranking_model" + key,
                )

                top_n = st.text_input(
                    "Enter the value for top_n:", key="top_n" + key
                )

                if reranking_model and top_n:
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("Perform Reranking", key="perform_reranking" + key, on_click=perform_reranking_callback, args=(key,)):
                            st.session_state.reranking_results[key] = True

                    with col2:
                        if st.button("Reset Results", key="reset_reranked" + key, on_click=reset_second_stage_result, args=(key,)):
                            pass
                else:
                    st.warning(
                        "Please select the reranking model and enter the top_n value."
                    )

    else:
        st.warning("Please select the required models and dimensions.")



async def main():


    initialize_session_state()


    st.set_page_config(
        page_title="RAG Pipeline Comparison Tool | Pinecone",
        layout="wide",
        page_icon="🧊",
        page_title="RAG Pipeline Comparison Tool | Pinecone",
        layout="wide",
        page_icon="🧊",
    )


    st.title("RAG Pipeline Comparison Tool")
    st.markdown(
        """
    st.markdown(
        """
        This tool allows you to configure and compare the results of two different RAG pipelines. 
        The left and right sides of the screen will display different pipelines, their configuration, and the resulting comparison.
    """
    )

    uploaded_file = st.file_uploader("Upload a file:", type=["json"])
    """
    )

    uploaded_file = st.file_uploader("Upload a file:", type=["json"])
    if uploaded_file:
        if not st.session_state.file_uploaded:

            input_data = uploaded_file.read().decode("utf-8")
            payload = {"input_data": input_data}

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://127.0.0.1:8000/upload-files",
                    json=payload,
                    timeout=75.0,
                )
                if response.status_code == 200:
                    st.success("Files uploaded successfully!")
                    st.session_state.file_uploaded = True
                else:
                    st.error(f"Upload failed")

    if not st.session_state.file_uploaded:
        st.warning("Please upload the JSON files for the pipelines to compare.")

    else:

    else:
        col1, col2 = st.columns(2)
        with col1:
            hybrid_search = st.radio(
                "Do you want to perform a hybrid search?",
                "Do you want to perform a hybrid search?",
                ("Yes", "No"),
                key=f"hybrid_search_1",
            )


            if hybrid_search == "Yes":
                await hybrid_search_pipeline(key="_1", filename = uploaded_file.name)
            else:
                await dense_search_pipeline(key="_1", filename = uploaded_file.name)

            st.subheader("Results")
            display_results_tabs("_1")

            display_results_tabs("_1")

        with col2:


            hybrid_search = st.radio(
                "Do you want to perform a hybrid search?",
                "Do you want to perform a hybrid search?",
                ("Yes", "No"),
                key="hybrid_search_2",
                key="hybrid_search_2",
            )


            if hybrid_search == "Yes":
                await hybrid_search_pipeline(key="_2", filename = uploaded_file.name)
            else:
                await dense_search_pipeline(key="_2", filename = uploaded_file.name)

            st.subheader("Results")
            display_results_tabs("_2")

            display_results_tabs("_2")


if __name__ == "__main__":
    asyncio.run(main())


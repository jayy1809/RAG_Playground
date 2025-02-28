import streamlit as st
import httpx
import asyncio

def initialize_session_state():
  
    if 'search_performed_1' not in st.session_state:
        st.session_state.search_performed_1 = False
    if 'search_performed_2' not in st.session_state:
        st.session_state.search_performed_2 = False
    if 'reranking_performed_1' not in st.session_state:
        st.session_state.reranking_performed_1 = False
    if 'reranking_performed_2' not in st.session_state:
        st.session_state.reranking_performed_2 = False
    if 'search_results_1' not in st.session_state:
        st.session_state.search_results_1 = None
    if 'search_results_2' not in st.session_state:
        st.session_state.search_results_2 = None
    if 'reranking_results_1' not in st.session_state:
        st.session_state.reranking_results_1 = None
    if 'reranking_results_2' not in st.session_state:
        st.session_state.reranking_results_2 = None
    if 'file_uploaded' not in st.session_state:
        st.session_state.file_uploaded = False
    if 'index_button_2_clicked' not in st.session_state:
        st.session_state.index_button_2_clicked = False
    if 'index_button_1_clicked' not in st.session_state:
        st.session_state.index_button_1_clicked = False
        
def reset_first_stage_result(pipeline_key):
    
    if pipeline_key == '_1':
        st.session_state.search_performed_1 = False
        st.session_state.search_results_1 = None
    else:
        st.session_state.search_performed_2 = False
        st.session_state.search_results_2 = None
        
def reset_second_stage_result(pipeline_key):
    
    if pipeline_key == '_1':
        st.session_state.reranking_performed_1 = False
        st.session_state.reranking_results_1 = None
    else:
        st.session_state.reranking_performed_2 = False
        st.session_state.reranking_results_2 = None
        
def perform_search_callback(pipeline_key):
    
    if pipeline_key == '_1':
        st.session_state.search_performed_1 = True
        
        st.session_state.search_results_1 = {}
    else:
        st.session_state.search_performed_2 = True
        
        st.session_state.search_results_2 = {}

def perform_reranking_callback(pipeline_key):
    
    if pipeline_key == '_1':
        st.session_state.reranking_performed_1 = True
        
        st.session_state.reranking_results_1 = {}
    else:
        st.session_state.reranking_performed_2 = True
        
        st.session_state.reranking_results_2 = {}
        
def display_results_tabs(key: str):
    
    tab1, tab2 = st.tabs(["Search Results", "Reranking Results"])
    
    with tab1:
        if key == '_1' and st.session_state.search_performed_1:
            display_search_results(st.session_state.search_results_1)
            
        elif key == '_2' and st.session_state.search_performed_2:
            display_search_results(st.session_state.search_results_2)
            
        else:
            st.info("Run a search to see results here.")
    
    with tab2:
        if key == '_1' and st.session_state.reranking_performed_1:
            display_reranking_results(st.session_state.reranking_results_1)
            
        elif key == '_2' and st.session_state.reranking_performed_2:
            display_reranking_results(st.session_state.reranking_results_2)
            
        else:
            st.info("Run reranking to see results here.")
        
        
def display_search_results(results):
    
    if not results:
        st.info("No search results available.")
        return
        
    st.success("Here are the search results:")
        
def display_reranking_results(results):
   
    if not results:
        st.info("No reranking results available.")
        return
        
    st.success("Here are the reranking results:")
    

def hybrid_search_pipeline(key: str):
        
    st.warning("By default, dot product similarity is used for the hybrid search.")
    
    dense_embedding_model = st.selectbox(
        "Select Dense Embedding Model:",
        ['', 'llama-text-embed-2'],
        key = 'dense_embedding_model' + key
    )
    dimensions = []
    if dense_embedding_model == 'llama-text-embed-2':
        dimensions = ['1024', '2048', '768', '512', '384']
    
    dense_dimension = st.selectbox(
        "Enter Dimension of the Dense Model:",
        dimensions,
        key = 'dense_dimension' + key
    )
    
    if dense_embedding_model and dense_dimension:

        index_name = st.text_input("Enter Index Name:", key = 'index_name' + key)
        cloud_provider = st.selectbox(
            "Enter Cloud Provider:", 
            ['aws', 'gcp', 'azure'],
            key = 'cloud_provider' + key
        )
        
        if cloud_provider == 'aws':
            regions = ['us-east-1', 'eu-west-1', 'us-west-2']
        elif cloud_provider == 'gcp':
            regions = ['us-central1', 'europe-west1']
        else:
            regions = ['eastus2']
        
        region = st.selectbox(
            "Enter Region:",
            regions,
            key = 'region' + key
        )
        
        if index_name and cloud_provider and region:
        
            create_index_button = st.button("Create Index and Upsert Dataset", key = 'create_index' + key)
            if create_index_button:
                st.write(f"Index '{index_name}' created and dataset upserted successfully!")
                st.session_state.index_button_1_clicked = True
        
            if st.session_state.index_button_1_clicked:
                query = st.text_area("Enter your query or question:", key = 'query' + key)
                top_k = st.text_input("Enter the value for top_k:", key = 'top_k' + key)
                alpha = st.slider("Select alpha value (between 0 and 1):", min_value=0.0, max_value=1.0, step = 0.1, value=0.5, key = 'alpha' + key)
                        
                col1, col2 = st.columns([1, 1])
                with col1:
                    similarity_search_button = st.button("Perform Similarity Search", key = 'perform_search' + key, on_click=perform_search_callback, args=(key,))
                    if similarity_search_button:
                        pass 
                        
                with col2:
                    reset_results_button = st.button("Reset Results", key = 'reset_similarity' + key, on_click=reset_first_stage_result, args=(key,))
                    if reset_results_button:
                        pass

                reranking_model = st.selectbox(
                    "Select Reranking Model:",
                    ["pinecone-rerank-v0"],
                    key = 'reranking_model' + key
                )
                        
                top_n = st.text_input("Enter the value for top_n:", key = 'top_n' + key)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    reranking_button = st.button("Perform Reranking", key = 'perform_reranking' + key, on_click=perform_reranking_callback, args=(key,))
                    if reranking_button:
                        pass
                
                with col2:
                    reset_results_button = st.button("Reset Results", key = 'reset_renaked' + key, on_click=reset_second_stage_result, args=(key,))
                    if reset_results_button:
                        pass
        else:
            st.warning("Please enter the required index details.")
        
    else:
        st.warning("Please select the required models and dimensions.")

def dense_search_pipeline(key: str):
        
    dense_embedding_model = st.selectbox(
        "Select Dense Embedding Model:",
        ['', 'llama-text-embed-2'],
        key = 'dense_embedding_model' + key
    )
    
    dimensions = []
    if dense_embedding_model == 'llama-text-embed-2':
        dimensions = ['1024', '2048', '768', '512', '384']
    
    dense_dimension = st.selectbox(
        "Enter Dimension of the Dense Model:",
        dimensions,
        key = 'dense_dimension' + key
    )
    
    if dense_embedding_model and dense_dimension:

        similarity_metric = st.selectbox(
            "Enter Similarity Metric:",
            ['dotproduct', 'cosine', 'euclidean'],
            key = 'similarity_metric' + key
        )
        
        index_name = st.text_input("Enter Index Name:", key = 'index_name' + key)
        
        cloud_provider = st.selectbox(
            "Enter Cloud Provider:", 
            ['aws', 'gcp', 'azure'],
            key = 'cloud_provider' + key
        )
        
        if cloud_provider == 'aws':
            regions = ['us-east-1', 'eu-west-1', 'us-west-2']
        elif cloud_provider == 'gcp':
            regions = ['us-central1', 'europe-west1']
        else:
            regions = ['eastus2']
        
        region = st.selectbox(
            "Enter Region:",
            regions,
            key = 'region' + key
        )
        
        if index_name and cloud_provider and region and similarity_metric:
        
            create_index_button = st.button("Create Index and Upsert Dataset", key = 'create_index' + key)
            if create_index_button:
                st.write(f"Index '{index_name}' created and dataset upserted successfully!")
                st.session_state.index_button_2_clicked = True
        
            if st.session_state.index_button_2_clicked:
                query = st.text_area("Enter your query or question:", key = 'query' + key)
                top_k = st.text_input("Enter the value for top_k:", key = 'top_k' + key)
                    
                col1, col2 = st.columns([1, 1])
                with col1:
                    similarity_search_button = st.button("Perform Similarity Search", key = 'perform_search' + key, on_click=perform_search_callback, args=(key,))
                    if similarity_search_button:
                        pass 
                    
                with col2:
                    reset_results_button = st.button("Reset Results", key = 'reset_similarity' + key, on_click=reset_first_stage_result, args=(key,))
                    if reset_results_button:
                        pass
                        
                reranking_model = st.selectbox(
                    "Select Reranking Model:",
                    ["pinecone-rerank-v0"],
                    key = 'reranking_model' + key
                )
                    
                top_n = st.text_input("Enter the value for top_n:", key = 'top_n' + key)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    reraking_button = st.button("Perform Reranking", key = 'perform_reranking' + key, on_click=perform_reranking_callback, args=(key,))  
                    if reraking_button:
                        pass
                
                with col2:
                    reset_results_button = st.button("Reset Results", key = 'reset_reranked' + key, on_click=reset_second_stage_result, args=(key,))
                    if reset_results_button:
                        pass
    
    else:
        st.warning("Please select the required models and dimensions.")

async def main():
    
    initialize_session_state()
    
    st.set_page_config(
        page_title = "RAG Pipeline Comparison Tool | Pinecone",
        layout = "wide",
        page_icon = "🧊"
    )
    
    st.title("RAG Pipeline Comparison Tool")
    st.markdown("""
        This tool allows you to configure and compare the results of two different RAG pipelines. 
        The left and right sides of the screen will display different pipelines, their configuration, and the resulting comparison.
    """)
    
    uploaded_file = st.file_uploader("Upload a file:", type=['json'])
    if uploaded_file:
        input_data = uploaded_file.read().decode("utf-8")
        payload = {
            "input_data": input_data
        }
        async with httpx.AsyncClient() as client:
            response = await client.post('http://127.0.0.1:8000/upload-files', json = payload)
            if response.status_code == 200:
                st.success("Files uploaded successfully!")
                st.json(response.json())
                st.session_state.file_uploaded = True
            else:
                st.error(f"Upload failed")
    
    if not st.session_state.file_uploaded:
        st.warning("Please upload the JSON files for the pipelines to compare.")
        
    else:       
        col1, col2 = st.columns(2)

        with col1:
            
            hybrid_search = st.radio(
                "Do you want to perform a hybrid search?", 
                ("Yes", "No"),
                key = "hybrid_search_1"
            )
            
            if hybrid_search == "Yes":
                hybrid_search_pipeline(key = '_1')
            else:
                dense_search_pipeline(key = '_1')
                
            st.subheader("Results")
            display_results_tabs('_1')
        
        with col2:
            
            hybrid_search = st.radio(
                "Do you want to perform a hybrid search?", 
                ("Yes", "No"),
                key = 'hybrid_search_2'
            )
            
            if hybrid_search == "Yes":
                hybrid_search_pipeline(key = '_2')
            else:
                dense_search_pipeline(key = '_2')
                
            st.subheader("Results")
            display_results_tabs('_2')

if __name__ == "__main__":
    asyncio.run(main())
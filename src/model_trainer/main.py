from src.utils.llmLangChain import LLMLangchainBanking

def train_model():
    llm_langchain_banking = LLMLangchainBanking()
    llm_langchain_banking.index_chunks()

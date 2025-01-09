from src.utils.llmLangChain import LLMLangchainBanking

async def train_model():
    llm_langchain_banking = LLMLangchainBanking()
    await llm_langchain_banking.index_chunks()
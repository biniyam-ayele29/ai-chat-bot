import getpass
import os
import pickle
import sqlite3
from langchain_openai import OpenAIEmbeddings
import bs4, re
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from langchain_community.vectorstores import SQLiteVSS
from typing import Literal
from typing_extensions import Annotated
from langgraph.graph import MessagesState, StateGraph
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import requests 
from openai import OpenAI

class LLMLangchainBanking:
    def __init__(self):
        if not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")
        self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.db_path = "src/database/vector_store.db"
        self.connection = SQLiteVSS.create_connection(db_file=self.db_path)
        self.vector_store = None
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.blog_posts = [
            "https://oromiabank.com/who-we-are/#corporate-statement",
            "https://oromiabank.com/conventional/",
            "https://oromiabank.com/oroodigital-banking-services/",
        ]

    def load_and_chunk_contents(self):
        loader = WebBaseLoader(
            web_paths=(self.blog_posts),
            bs_kwargs=dict(
                parse_only=bs4.SoupStrainer(
                    class_=("dsm-advanced-tabs-content-wrapper","dsm-inner-content", "et_pb_column et_pb_column_3_4 et_pb_column_2  et_pb_css_mix_blend_mode_passthrough et-last-child")
                )
            ),
        )
        docs = loader.load()
        print(docs)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        all_splits = text_splitter.split_documents(docs)
        total_documents = len(all_splits)
        print("Total documents: ", total_documents)
        return total_documents, all_splits
    
    def index_chunks(self):
        total_documents, all_splits = self.load_and_chunk_contents()
        third = total_documents // 3

        for i, document in enumerate(all_splits):
            if i < third:
                document.metadata["section"] = "beginning"
            elif i < 2 * third:
                document.metadata["section"] = "middle"
            else:
                document.metadata["section"] = "end"

        vector_store = SQLiteVSS(embedding=self.embeddings, table="state_union",connection=self.connection)
        # Index chunks
        _ = vector_store.add_documents(documents=all_splits)
        print("Indexing completed")
        return vector_store
    
    def load_vector_store(self):
        try:
            self.vector_store = SQLiteVSS(embedding=self.embeddings, table="state_union",connection=self.connection)
        except Exception as e:
            print(e)
            return []
    
    def retrieve_docs(self, query: str):
        try:
            if self.vector_store is None:
                self.load_vector_store()
            return self.vector_store.similarity_search(query, k=2)
        except Exception as e:
            print(e)
            return []
    
    
    # Step 1: Generate an AIMessage that may include a tool-call to be sent.
    def query_or_respond(self, state: MessagesState):
        """Generate tool call for retrieval or respond."""
        llm_with_tools = self.llm.bind_tools([retrieve])
        system_message_content = (
            "You are a professional Oromia Bank assistant"
            "You can answer any questions related to Oromia Bank"
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "when you are asked about the exchange rate, you should call the get_exchange_rate tool"
            "don't know politely, don't try to make up an answer. Use the following pieces of context to answer the question at the end."
            "Use three sentences maximum and keep the answer as concise as possible"
            "when you are asked about the history of the bank, you should mention the beginning, middle and end of the bank"
            "when you are asked about yourself, you should tell the user that you are trained professional AI Ormomian Banking service assistant"
            "when you receive greetings, mention that you are Oromia Bank assistant, and glad to help"
            "\n\n"
        )
        prompt = [SystemMessage(system_message_content)] + state["messages"]
        response = llm_with_tools.invoke(prompt)
        # MessagesState appends messages to state instead of overwriting
        return {"messages": [response]}
    
    # Step 3: Generate a response using the retrieved content.
    def generate(self, state: MessagesState):
        """Generate answer."""
        # Get generated ToolMessages
        recent_tool_messages = []
        for message in reversed(state["messages"]):
            if message.type == "tool":
                recent_tool_messages.append(message)
            else:
                break
        tool_messages = recent_tool_messages[::-1]
        # Format into prompt
        docs_content = "\n\n".join(doc.content for doc in tool_messages)
        system_message_content = (
            "You are a professional Oromia Bank assistant"
            "You can answer any questions related to Oromia Bank"
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know politely, don't try to make up an answer. Use the following pieces of context to answer the question at the end."
            "Use three sentences maximum and keep the answer as concise as possible"
            "when you are asked about the history of the bank, you should mention the beginning, middle and end of the bank"
            "when you are asked about yourself, you should tell the user that you are trained professional AI Ormomian Banking service assistant"
            "when you recive greetings, mention that you are Oromia Bank assistant, and glad to help"
            "\n\n"
            f"{docs_content}"
        )
        conversation_messages = [
            message
            for message in state["messages"]
            if message.type in ("human", "system")
            or (message.type == "ai" and not message.tool_calls)
        ]
        prompt = [SystemMessage(system_message_content)] + conversation_messages
        # Run
        response = self.llm.invoke(prompt)
        return {"messages": [response]}

    
    def run(self, input_messages):
        tools = ToolNode([retrieve])
        graph_builder = StateGraph(MessagesState)
        graph_builder.add_node(self.query_or_respond)
        graph_builder.add_node(tools)
        graph_builder.add_node(self.generate)
        graph_builder.add_node(self.get_exchange_rate)

        graph_builder.set_entry_point("query_or_respond")
        graph_builder.add_conditional_edges(
            "query_or_respond",
            tools_condition,
            {END: END, "tools": "tools"},
        )
        graph_builder.add_edge("tools", "get_exchange_rate")
        graph_builder.add_edge("get_exchange_rate", END)
        graph_builder.add_edge("generate", END)

        memory = MemorySaver()
        graph = graph_builder.compile(checkpointer=memory)
        # Specify an ID for the thread
        config = {"configurable": {"thread_id": "abc12443"}}
        response = graph.invoke({"messages": input_messages}, config=config)
        return response["messages"][-1].content
    
    def get_exchange_rate(self, state: MessagesState):
        try:
            query = state["messages"][-1].content
            patterns = {
                'EUR': r'\b(EUR|euro[s]?)\b',
                'USD': r'\b(USD|dollar[s]?|usd)\b',
                'GBP': r'\b(GBP|pound[s]?)\b',
                'JPY': r'\b(JPY|yen)\b',
                'ETB': r'\b(ETB|birr)\b'
            }
            
            base_currency = None
            for code, pattern in patterns.items():
                if re.search(pattern, query, re.IGNORECASE):
                    base_currency = code
                    break
                    
            if not base_currency:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{
                        "role": "system",
                        "content": "Extract the currency code from: 'what is the exchange rate of EUR today' → EUR"
                    }, {
                        "role": "user",
                        "content": query
                    }],
                    temperature=0,
                    max_tokens=3
                )
                extracted = response.choices[0].message.content.strip().upper()
                base_currency = extracted if extracted in patterns else 'EUR'
            
            target_currency = 'ETB'
            api_url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            rate = response.json()['rates'][target_currency]
            return {"messages": [f"1 {base_currency} = {rate:.2f} {target_currency}"]}
            
        except requests.RequestException as e:
            return {"messages": [f"Error fetching exchange rate: {str(e)}"]}
        except (ValueError, KeyError) as e:
            return {"messages": [f"Error processing request: {str(e)}"]}
        except Exception as e:
            return {"messages": [f"Unexpected error: {str(e)}"]}
            


@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""
    try:
        llm_langchain_banking = LLMLangchainBanking()
        retrieved_docs = llm_langchain_banking.retrieve_docs(query)
        serialized = "\n\n".join(
            (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
            for doc in retrieved_docs
        )
        return serialized, retrieved_docs
    except Exception as e:
        print(e)
        return [], []



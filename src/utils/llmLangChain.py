import getpass
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import bs4
from langchain_community.document_loaders import WebBaseLoader, JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, END, StateGraph
from langchain_community.vectorstores import SQLiteVSS
from langgraph.graph import MessagesState
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from src.utils.dbConnection import DBConnection
import requests, json

class LLMLangchainBanking:
    def __init__(self):
        if not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")
        self.llm = ChatOpenAI(model="gpt-4o")
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.dbConnection = DBConnection()
        self.blog_posts = [
            "https://oromiabank.com/who-we-are/#corporate-statement",
            "https://oromiabank.com/conventional/",
            "https://oromiabank.com/oroodigital-banking-services/",
            "https://oromiabank.com/board-of-directors/",
            "https://oromiabank.com/obs-executive-managements/",
            "https://oromiabank.com/directorate-directors/",
            "https://oromiabank.com/oroodigital-banking-services/",
            "https://oromiabank.com/merchant-services/",
            "https://oromiabank.com/agent-banking/",
            "https://oromiabank.com/card-banking/"
        ]

    def get_branch_details(self):
        url = 'https://oromiabank.com/wp-admin/admin-ajax.php?action=get_wdtable&table_id=7'
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': '_clck=145xc05%7C2%7Cfs9%7C0%7C1816; newsletter_leads=36; _clsk=x03qax%7C1735913808716%7C1%7C1%7Cz.clarity.ms%2Fcollect',
            'origin': 'https://oromiabank.com',
            'priority': 'u=1, i',
            'referer': 'https://oromiabank.com/branch-information/',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        data = {
            'draw': '2',
            'columns[0][data]': '0',
            'columns[0][name]': 'wdt_ID',
            'columns[0][searchable]': 'false',
            'columns[0][orderable]': 'false',
            'columns[0][search][value]': '',
            'columns[0][search][regex]': 'false',
            'columns[1][data]': '1',
            'columns[1][name]': 'wdt_created_by',
            'columns[1][searchable]': 'false',
            'columns[1][orderable]': 'false',
            'columns[1][search][value]': '',
            'columns[1][search][regex]': 'false',
            'columns[2][data]': '2',
            'columns[2][name]': 'wdt_created_at',
            'columns[2][searchable]': 'false',
            'columns[2][orderable]': 'false',
            'columns[2][search][value]': '',
            'columns[2][search][regex]': 'false',
            'columns[3][data]': '3',
            'columns[3][name]': 'wdt_last_edited_by',
            'columns[3][searchable]': 'false',
            'columns[3][orderable]': 'false',
            'columns[3][search][value]': '',
            'columns[3][search][regex]': 'false',
            'columns[4][data]': '4',
            'columns[4][name]': 'wdt_last_edited_at',
            'columns[4][searchable]': 'false',
            'columns[4][orderable]': 'false',
            'columns[4][search][value]': '',
            'columns[4][search][regex]': 'false',
            'columns[5][data]': '5',
            'columns[5][name]': 'branch',
            'columns[5][searchable]': 'true',
            'columns[5][orderable]': 'false',
            'columns[5][search][value]': '',
            'columns[5][search][regex]': 'false',
            'columns[6][data]': '6',
            'columns[6][name]': 'wdtcolumn',
            'columns[6][searchable]': 'true',
            'columns[6][orderable]': 'false',
            'columns[6][search][value]': '',
            'columns[6][search][regex]': 'false',
            'columns[7][data]': '7',
            'columns[7][name]': 'region',
            'columns[7][searchable]': 'true',
            'columns[7][orderable]': 'false',
            'columns[7][search][value]': '',
            'columns[7][search][regex]': 'false',
            'columns[8][data]': '8',
            'columns[8][name]': 'location',
            'columns[8][searchable]': 'true',
            'columns[8][orderable]': 'false',
            'columns[8][search][value]': '',
            'columns[8][search][regex]': 'false',
            'columns[9][data]': '9',
            'columns[9][name]': 'district',
            'columns[9][searchable]': 'true',
            'columns[9][orderable]': 'false',
            'columns[9][search][value]': '',
            'columns[9][search][regex]': 'false',
            'columns[10][data]': '10',
            'columns[10][name]': 'email',
            'columns[10][searchable]': 'false',
            'columns[10][orderable]': 'false',
            'columns[10][search][value]': '',
            'columns[10][search][regex]': 'false',
            'columns[11][data]': '11',
            'columns[11][name]': 'phone',
            'columns[11][searchable]': 'true',
            'columns[11][orderable]': 'false',
            'columns[11][search][value]': '',
            'columns[11][search][regex]': 'false',
            'start': '0',
            'length': '600',
            'search[value]': 'a',
            'search[regex]': 'false',
            'wdtNonce': 'dca58721ad'
        }

        try: 
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()  # Ensure we notice bad responses

            # Assuming the response is JSON
            data = response.json()
            with open("src/data/branch_details.json", "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(e)
        return "src/data/branch_details.json"

    async def load_and_chunk_contents(self):
        web_loader = WebBaseLoader(
            web_paths=(self.blog_posts),
            bs_kwargs=dict(
                parse_only=bs4.SoupStrainer(
                    class_=(
                            "dsm-advanced-tabs-content-wrapper","dsm-inner-content", 
                            "et_pb_column et_pb_column_3_4 et_pb_column_2  et_pb_css_mix_blend_mode_passthrough et-last-child",
                            "et_builder_inner_content et_pb_gutters3",
                            "et_pb_section et_pb_section_0 et_section_regular",
                            "et_builder_inner_content et_pb_gutters3",
                            "et_pb_section et_pb_section_0 et_section_regular",
                            )
                )
            ),
        )
        branch_details = self.get_branch_details()
        json_loader = JSONLoader(
                file_path=branch_details,
                jq_schema='.data',
                text_content=False,
                json_lines=True
            )
        docs = web_loader.load() + json_loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        all_splits = text_splitter.split_documents(docs)
        total_documents = len(all_splits)
        print("Total documents: ", total_documents)
        return total_documents, all_splits
    
    async def index_chunks(self) -> None:
        total_documents, all_splits = await self.load_and_chunk_contents()
        third = total_documents // 3

        for i, document in enumerate(all_splits):
            if i < third:
                document.metadata["section"] = "beginning"
            elif i < 2 * third:
                document.metadata["section"] = "middle"
            else:
                document.metadata["section"] = "end"

        vector_store = await self.dbConnection.get_vector_store()
        vector_store.add_documents(documents=all_splits)
        await self.dbConnection.close_connection()
    
    async def retrieve_docs(self, query: str):
        try:
            vector_store = await self.dbConnection.get_vector_store()
            similar_docs = vector_store.similarity_search(query, k=2)
            self.dbConnection.close_connection()
            return similar_docs
        except Exception as e:
            print(e)
            return []
    
    def query_or_respond(self, state: MessagesState):
        llm_with_tools = self.llm.bind_tools([retrieve])
        system_message_content = """You are a professional Oromia Bank assistant. 
        You are multilingual professional banking assistant, you can interact with Ethiopian majour languages.
        You can speak Amharic, Oromo, English and Tigrinya.
        You can answer questions related to Oromia Bank. Use retrieved context to answer questions. 
        For exchange rates, use the get_exchange_rate tool. Keep answers concise and within three sentences. 
        For Account opening and related questions answer with basic infomation and provice this link to file the online form https://oromiabank.com/open-account/.
        For bank history, mention beginning, middle and end. Identify yourself as an AI Oromian Banking assistant."""
        
        prompt = [SystemMessage(content=system_message_content)] + state["messages"]
        response = llm_with_tools.invoke(prompt)
        return {"messages": [response]}
    
    def generate(self, state: MessagesState):
        recent_tool_messages = [msg for msg in reversed(state["messages"]) if msg.type == "tool"]
        docs_content = "\n\n".join(doc.content for doc in recent_tool_messages[::-1])
        
        system_message_content = f"""You are a professional Oromia Bank assistant.
        You are multilingual professional banking assistant, you can interact with Ethiopian majour languages.
        You can speak Amharic, Oromo, English and Tigrinya. If the user asks in the local langueges please respond in the same language.
        For exchange rates, use the exchange tool. Keep answers concise and within three sentences.
        For exchange rate questions you have realtime data from the exchange tool.
        For questions related to conversion, calculation of exchange rates with currencies, get the exchange rate from the exchange tool and do the math.
        For exchange rate related questions, respond with the data you get from the exchange tool.
        For any other questions, use the following context to answer questions:\n\n{docs_content}"""
        
        conversation_messages = [msg for msg in state["messages"] 
                               if msg.type in ("human", "system") 
                               or (msg.type == "ai" and not msg.tool_calls)]
        
        prompt = [SystemMessage(content=system_message_content)] + conversation_messages
        response = self.llm.invoke(prompt)
        return {"messages": [response]}
    
    def extract_currency(self, query: str) -> tuple[str, str]:
        try:
            base_template = f"""Extract the first mentioned 3-letter ISO currency code.
                Return ONLY the code in capitals. If no valid code found, return 'XXX'.
                For queries with multiple currencies, extract the first one.

                Examples:
                convert 50 USD to EUR result should be USD
                JPY rate today result should be JPY
                what is the exchange rate of USD to ETB result should be USD
                what is the exchange rate of EUR to ETB result should be EUR
                what is the exchange rate of US dollars to ethiopian birr the result should be USD

                {query}"""
            base = self.llm.invoke(input=base_template)
            if not base or base.content == "XXX":
                return None, "ETB"
                
            # Extract target currency after "to", default to ETB
            target_template = f"""Extract the target currency after 'to'.
            Return only the 3-letter code. If none found, return 'ETB'.
            Query: {query}"""
            
            target = self.llm.invoke(input=target_template)
            return base.content, target.content
        except Exception as e:
            print(f"Currency extraction error: {e}")
            return None, None
        
    def get_exchange_rate_api(self, base: str, target: str = "ETB") -> float:
        try:
            response = requests.get(
                f"https://api.exchangerate-api.com/v4/latest/{base}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()['rates'][target]
        except Exception as e:
            print(f"Exchange rate error: {e}")
            return None
           
    def get_exchange_rate(self, state: MessagesState):
        """Process exchange rate queries"""
        try:
            query = state["messages"][0].content
            base, target = self.extract_currency(query)
            if not base:
                return {"messages": ["Could not identify currency in your query."]}
                
            rate = self.get_exchange_rate_api(base, target)
            if not rate:
                return {"messages": ["Error fetching exchange rate."]}
                
            return {"messages": [f"1 {base} = {rate:.2f} {target}"]}
            
        except Exception as e:
            return {"messages": [f"Unexpected error: {str(e)}"]}

    def run(self, input_messages):
        tools = ToolNode([retrieve])
        graph = StateGraph(MessagesState)
        
        graph.add_node("query", self.query_or_respond)
        graph.add_node("tools", tools)
        graph.add_node("generate", self.generate)
        graph.add_node("exchange", self.get_exchange_rate)

        graph.set_entry_point("query")
        graph.add_conditional_edges(
            "query",
            tools_condition,
            {END: END, "tools": "tools"}
        )
        graph.add_conditional_edges(
            "tools",
            tools_condition,
            {END: END, "exchange": "exchange"}
        )
        graph.add_edge("tools", "exchange")
        graph.add_edge("exchange", "generate")
        graph.add_edge("exchange", END)
        graph.add_edge("generate", END)

        memory = MemorySaver()
        chain = graph.compile(checkpointer=memory)
        config = {"configurable": {"thread_id": "abc12443"}}
        response = chain.invoke({"messages": input_messages}, config=config)
        return response["messages"][-1].content

@tool(response_format="content_and_artifact")
async def retrieve(query: str):
    """Retrieve information related to a query."""
    try:
        llm = LLMLangchainBanking()
        docs = await llm.retrieve_docs(query)
        content = "\n\n".join(f"Source: {doc.metadata}\nContent: {doc.page_content}" for doc in docs)
        return content, docs
    except Exception as e:
        print(e)
        return [], []
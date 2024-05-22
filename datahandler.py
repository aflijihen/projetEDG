import os
import json
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores.faiss import FAISS
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_community.document_loaders import DirectoryLoader, Docx2txtLoader
import docx2txt
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.schema.output_parser import StrOutputParser
from llama_index_client import PgVectorStore
from langchain_openai import ChatOpenAI
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from publisher_handler import Publisher
import http.client, urllib
from pushbullet import Pushbullet

load_dotenv()
class DataHandler:
    def __init__(self):
        self.docs_dir = "./handbook/"
        self.persist_dir = "./handbook_faiss"
        self.embedding = SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2")
        self.llm = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'), temperature=0.6)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.API_KEY = os.getenv('PUSHBULLET_API_KEY')
        self.pb = Pushbullet(self.API_KEY)
        
        self.load_or_build_faiss()
        self.initialize_qa_chain()
        self.build_faiss_index()
        
    def load_or_build_faiss(self):
        if os.path.exists(self.persist_dir):
            print(f"Loading FAISS index from {self.persist_dir}")
            self.vectorstore = FAISS.load_local(self.persist_dir, self.embedding, allow_dangerous_deserialization=True)
            print("Done.")
        else:
            print(f"Building FAISS index from documents in {self.docs_dir}")
            pass

    def initialize_qa_chain(self):
        #utilisée pour initialiser une chaîne de traitement de récupération conversationnelle 
        self.qa_chain = ConversationalRetrievalChain.from_llm(
             llm=self.llm,
             memory=self.memory,
             retriever=self.vectorstore.as_retriever()
   
        )
    def build_faiss_index(self):
        # Construction de l'index FAISS à partir des documents
        loader = DirectoryLoader(
            self.docs_dir,
            loader_cls=Docx2txtLoader,
            recursive=True,
            silent_errors=True,
            show_progress=True,
            glob="**/*.docx"
        )
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=75)
        frags = text_splitter.split_documents(docs)
        print(f"Populating vector store with {len(docs)} docs in {len(frags)} fragments")
        self.vectorstore = FAISS.from_documents(frags, self.embedding)
        print(f"Persisting vector store to: {self.persist_dir}")
        self.vectorstore.save_local(self.persist_dir)
        print(f"Saved FAISS index to {self.persist_dir}")
      
    def execute(self, data):
            
            self.API_KEY = os.getenv('PUSHBULLET_API_KEY')
            self.pb = Pushbullet(self.API_KEY)
        
            user_input = (f"Utiliser les valeurs actuelles : temperature: {data['temperature']} - Ph : {data['Ph_value']} - Niveau_deau : {data['water_level']} - Conductivité : {data['conductivity']} - Luminosité : {data['brightness']}, donner des recommandations spécifiques à chaque mesure : ")
            # Ajout d'une prompt pour guider la génération des recommandations
            sys_prompt = (
            f"Pour chaque mesure, veuillez fournir une recommandation détaillée en suivant le format ci-dessous :\n"
            f"1. Température ({data['temperature']}°C) :\n"
            f"   - Recommandation : *idéale ou non idéale*, suivi d'une explication détaillée.\n"
            f"2. pH ({data['Ph_value']}) :\n"
            f"   - Recommandation : *idéale ou non idéale*, suivi d'une explication détaillée.\n"
            f"3. Niveau d'eau ({data['water_level']} mètres) :\n"
            f"   - Recommandation : *idéale ou non idéale*, suivi d'une explication détaillée.\n"
            f"4. Conductivité ({data['conductivity']} µS/cm) :\n"
            f"   - Recommandation : *idéale ou non idéale*, suivi d'une explication détaillée.\n"
            f"5. Luminosité ({data['brightness']} lux) :\n"
            f"   - Recommandation : *idéale ou non idéale*, suivi d'une explication détaillée.\n"
        "{user_input}" 
)
        

            
            if user_input.lower() == "exit":
                return
            else:
                result = self.qa_chain.invoke({"question": user_input})
                generated_response = result["answer"]
                print("Recommendations:", generated_response)
                title="recommendations"
                self.pb.push_note(title, generated_response)
                # Extract codes from recommendations
                publisher = Publisher()
                recommandations = publisher.generate_recommendation(data) 
                publisher.publish_recommendations(recommandations)
        
           
    
               
        
               

                
                    
                
                    
                



import json
import ollama
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import tkinter as tk
from tkinter import scrolledtext
import threading

# Load and process the data
def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# Create text chunks for embedding and retrieval
def create_chunks(data):
    chunks = []
    for item in data:
        # Basic info chunk
        basic_info = f"Offre: {item['Offre']}\n{item['Contenu']}"
        chunks.append({
            "text": basic_info,
            "metadata": {"offer": item['Offre'], "category": item['SOUS-RUBRIQUE']}
        })
        
        # Add table data if available and not "N/A"
        if item['Tableau'] != "N/A":
            for table_name, table_rows in item['Tableau'].items():
                for row in table_rows:
                    table_info = f"Offre: {item['Offre']} - {table_name}:\n"
                    for key, value in row.items():
                        table_info += f"{key}: {value}\n"
                    chunks.append({
                        "text": table_info,
                        "metadata": {"offer": item['Offre'], "category": table_name}
                    })
    
    return chunks

# Embedding model for text similarity
class EmbeddingModel:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
    def get_embedding(self, text):
        return self.model.encode(text)

# Vector Database for storing and retrieving embeddings
class VectorDatabase:
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.documents = []
        self.embeddings = []
        
    def add_documents(self, chunks):
        for chunk in chunks:
            self.documents.append(chunk)
            self.embeddings.append(self.embedding_model.get_embedding(chunk["text"]))
        
    def retrieve(self, query, top_k=3):
        query_embedding = self.embedding_model.get_embedding(query)
        
        # Calculate similarity scores
        similarities = cosine_similarity([query_embedding], self.embeddings)[0]
        
        # Get top k most similar documents
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        results = []
        
        for idx in top_indices:
            results.append({
                "document": self.documents[idx],
                "score": similarities[idx]
            })
            
        return results

# LLM interface using Ollama
class LlamaModel:
    def __init__(self, model_name="llama3.2"):
        self.model_name = model_name
        
    def generate_response(self, prompt, context=""):
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        "role": "system", 
                        "content": """Tu es un assistant virtuel de Tunisie Telecom qui fournit des informations 
                        précises sur les offres mobiles. Réponds aux questions des clients en utilisant uniquement 
                        le contexte fourni. Si tu ne connais pas la réponse, dis simplement que tu n'as pas cette 
                        information et suggère de contacter le service client au 1298."""
                    },
                    {"role": "user", "content": f"Contexte :\n{context}\n\nQuestion du client: {prompt}"}
                ]
            )
            return response['message']['content']
        except Exception as e:
            return f"Erreur de génération: {str(e)}"

# RAG Pipeline
class RAGPipeline:
    def __init__(self, data_path):
        print("Initialisation du RAG Pipeline...")
        self.data = load_data(data_path)
        self.chunks = create_chunks(self.data)
        self.embedding_model = EmbeddingModel()
        self.vector_db = VectorDatabase(self.embedding_model)
        self.vector_db.add_documents(self.chunks)
        self.llm = LlamaModel()
        print("RAG Pipeline initialisé!")
        
    def answer_question(self, query):
        print(f"Question reçue: {query}")
        
        # 1. Retrieve relevant documents
        results = self.vector_db.retrieve(query)
        
        # 2. Create context from retrieved documents
        context = "\n\n".join([doc["document"]["text"] for doc in results])
        
        # 3. Generate response using LLM
        response = self.llm.generate_response(query, context)
        
        return response

# GUI Application for the chatbot
class ChatbotApp:
    def __init__(self, root, rag_pipeline):
        self.root = root
        self.rag_pipeline = rag_pipeline
        
        root.title("Tunisie Telecom Assistant")
        root.geometry("600x700")
        
        # Chat history display
        self.chat_history = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=30)
        self.chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_history.config(state=tk.DISABLED)
        
        # Input frame
        input_frame = tk.Frame(root)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # User input field
        self.user_input = tk.Entry(input_frame, width=50)
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.user_input.bind("<Return>", self.send_message)
        
        # Send button
        send_button = tk.Button(input_frame, text="Envoyer", command=self.send_message)
        send_button.pack(side=tk.RIGHT, padx=5)
        
        # Initial welcome message
        self.add_message("Assistant", "Bonjour ! Je suis l'assistant virtuel de Tunisie Telecom. Comment puis-je vous aider aujourd'hui ?")
        
    def add_message(self, sender, message):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_history.see(tk.END)
        self.chat_history.config(state=tk.DISABLED)
        
    def send_message(self, event=None):
        user_message = self.user_input.get().strip()
        if user_message:
            self.add_message("Vous", user_message)
            self.user_input.delete(0, tk.END)
            
            # Process in a separate thread to keep UI responsive
            threading.Thread(target=self.process_message, args=(user_message,), daemon=True).start()
    
    def process_message(self, user_message):
        # Get response from RAG pipeline
        response = self.rag_pipeline.answer_question(user_message)
        self.add_message("Assistant", response)

# Main application
if __name__ == "__main__":
    # Path to your dataset
    data_path = "chatbot/tunisie_telecom_data.json"
    
    # Initialize RAG pipeline
    rag_pipeline = RAGPipeline(data_path)
    
    # Start the GUI
    root = tk.Tk()
    app = ChatbotApp(root, rag_pipeline)
    root.mainloop()
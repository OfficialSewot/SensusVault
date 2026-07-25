import json
import uuid
from src.models.models import Note, Metadata
from src.database.manager import DatabaseManager
from src.ingestor.ingestor import Ingestor

import os
import json
import uuid
from typing import Optional
from src.models.models import Note
from src.database.manager import DatabaseManager
from src.ingestor.ingestor import Ingestor

def generate_test_data():
    db_manager = DatabaseManager(db_path="test_vault.db", chroma_path="test_chroma")
    ingestor = Ingestor(db_manager)

    # Define a rich set of knowledge
    knowledge_base = [
    {
        "title": "Project Phoenix",
        "content": "Project Phoenix is a next-generation AI research initiative focused on autonomous agents. Key stakeholders include Dr. Aris and the Robotics Lab. It uses LLMs and reinforcement learning. The goal is to create agents capable of complex reasoning and tool use."
    },
    {
        "title": "Robotics Lab Overview",
        "content": "The Robotics Lab is located in Berlin. It specializes in humanoid robotics and autonomous navigation. Led by Dr. Aris. The lab received funding from the European Research Council in 2023."
    },
    {
        "title": "LLM Research",
        "content": "Large Language Models (LLMs) are transforming NLP. We are exploring transformer architectures and attention mechanisms. Our focus is on reducing hallucination in long-context windows."
    },
    {
        "title": "Project Helios",
        "content": "Project Helios is a solar power management system for industrial use. It involves IoT sensors and grid synchronization. It was designed to optimize energy distribution in large factories."
    },
    {
        "title": "Dr. Aris Bio",
        "content": "Dr. Aris is a leading researcher in AI and robotics. She has published over 50 papers on autonomous systems. She is currently the head of the Robotics Lab in Berlin."
    },
    {
        "title": "Transformer Architecture",
        "content": "Transformers rely on the self-attention mechanism to weigh the importance of different parts of the input data. They are the backbone of most modern LLMs."
    },
    {
        "title": "Reinforcement Learning",
        "content": "Reinforcement Learning (RL) involves training agents to make decisions by maximizing a reward signal. It is crucial for autonomous navigation and robotics."
    },
    {
        "title": "Computer Vision",
        "content": "Computer Vision (CV) enables machines to interpret visual information. We use CNNs and Vision Transformers for object detection and segmentation."
    },
    {
        "title": "NLP Techniques",
        "content": "Natural Language Processing (NLP) includes tasks like translation, summarization, and sentiment analysis. LLMs have revolutionized these tasks."
    },
    {
        "title": "IoT Sensors",
        "content": "IoT sensors are used in Project Helios to monitor real-time solar output and power consumption. They transmit data via LoRaWAN protocols."
    },
    {
        "title": "Grid Synchronization",
        "content": "Grid synchronization ensures that industrial power systems remain stable while integrating intermittent solar power. Project Helios handles this via advanced control theory."
    },
    {
        "title": "Humanoid Robotics",
        "content": "Humanoid robotics focuses on creating robots that mimic human movement and interaction. The Robotics Lab is developing a prototype called 'Ares'."
    },
    {
        "title": "Autonomous Navigation",
        "content": "Autonomous navigation involves planning paths and avoiding obstacles in dynamic environments. This is a key focus of the Robotics Lab in Berlin."
    },
    {
        "title": "Hallucination Mitigation",
        "content": "Hallucination mitigation is a priority in our LLM research. We use RAG (Retrieval-Augmented Generation) and fact-checking loops to improve reliability."
    },
    {
        "title": "LoRaWAN Protocol",
        "content": "LoRaWAN is a long-range, low-power wide-area network protocol. It is ideal for industrial IoT applications like Project Helios."
    },
    {
        "title": "European Research Council",
        "content": "The European Research Council (ERC) provides significant funding for high-impact research in AI and robotics, including the Robotics Lab."
    },
    {
        "title": "Attention Mechanisms",
        "content": "Attention mechanisms allow models to focus on specific parts of the input sequence. Scaled Dot-Product Attention is the standard in transformer models."
    },
    {
        "title": "Object Detection",
        "content": "Object detection identifies and locates objects within images. We use YOLO and Faster R-CNN for various CV tasks."
    },
    {
        "title": "Vision Transformers",
        "content": "Vision Transformers (ViT) apply the transformer architecture to image patches, competing with and often surpassing CNNs in many CV tasks."
    },
    {
        "title": "Sentiment Analysis",
        "content": "Sentiment analysis classifies text as positive, negative, or neutral. It's a core NLP task we use for social media monitoring."
    },
    {
        "title": "Summarization",
        "content": "Summarization condenses long documents into concise versions. We use abstractive summarization techniques based on large language models."
    },
    {
        "title": "Translation",
        "content": "Machine translation converts text from one language to another. We focus on high-quality, low-latency translation for technical manuals."
    },
    {
        "title": "Path Planning",
        "content": "Path planning is the computational problem of finding a valid path from start to goal. It's essential for autonomous navigation."
    },
    {
        "title": "Obstacle Avoidance",
        "content": "Obstacle avoidance ensures that robots can navigate safely in cluttered environments. We use LIDAR and depth cameras for this."
    },
    {
        "title": "Transformer Models",
        "content": "Transformer models have replaced RNNs and LSTMs as the state-of-the-art for almost all NLP tasks due to their parallelizable nature."
    },
    {
        "title": "RNNs and LSTMs",
        "content": "Recurrent Neural Networks (RNNs) and Long Short-Term Memory (LSTMs) were the previous standard for sequential data but struggle with long-range dependencies."
    },
    {
        "title": "Transformer Architectures",
        "content": "Transformer architectures utilize multi-head attention and position encoding to process sequences of varying lengths efficiently."
    },
    {
        "title": "Long-Context Windows",
        "content": "Long-context windows allow models to process massive amounts of text in a single pass, but they require efficient attention mechanisms like FlashAttention."
    },
    {
        "title": "Fact-Checking Loops",
        "content": "Fact-checking loops involve verifying the generated output against a trusted source of truth, such as our internal knowledge base."
    },
    {
        "title": "RAG (Retrieval-Augmented Generation)",
        "content": "RAG provides LLMs with external knowledge by retrieving relevant documents before generating a response. This is the core of SensusVault."
    },
    {
        "title": "Industrial Power Systems",
        "content": "Industrial power systems require high reliability and safety. Project Helios aims to modernize these with renewable energy."
    },
    {
        "title": "Renewable Energy",
        "content": "Renewable energy, particularly solar and wind, is key to sustainable industrial growth. Helios is our flagship project in this space."
    },
    {
        "title": "Solar Power Management",
        "content": "Solar power management involves regulating the flow of energy from solar panels to the grid or storage systems."
    },
    {
        "title": "Advanced Control Theory",
        "content": "Advanced control theory is used in Project Helios to manage the complex dynamics of solar power distribution."
    },
    {
        "title": "Real-Time Solar Output",
        "content": "Monitoring real-time solar output allows for dynamic adjustment of power distribution, which is critical for Helios's success."
    },
    {
        "title": "Dynamic Adjustment",
        "content": "Dynamic adjustment of power distribution prevents system overloads and ensures consistent power to industrial equipment."
    },
    {
        "title": "Grid Stability",
        "content": "Maintaining grid stability while integrating fluctuating power sources like solar is a major engineering challenge for Project Helios."
    },
    {
        "title": "LoRaWAN Networks",
        "content": "LoRaWAN networks are highly scalable and efficient for long-distance communication of small data packets, perfect for IoT."
    },
    {
        "title": "IoT Applications",
        "content": "IoT applications in industrial settings often require robust connectivity and low power consumption, making LoRaWAN a primary choice."
    },
    {
        "title": "Transformer Architectures",
        "content": "Transformer architectures use encoder and decoder stacks to process information in parallel across various modalities."
    },
    {
        "title": "Multi-Head Attention",
        "content": "Multi-head attention allows the model to attend to different parts of the input simultaneously from different representation subspaces."
    },
    {
        "title": "Self-Attention",
        "content": "Self-attention computes a weighted sum of the values in the input, where the weights are determined by the similarity between the query and the keys."
    },
    {
        "title": "Neural Networks",
        "content": "Neural networks are the fundamental building blocks of deep learning, inspired by the structure and function of the human brain."
    },
    {
        "title": "Deep Learning",
        "content": "Deep learning is a subset of machine learning that uses multi-layered neural networks to learn complex patterns from data."
    },
    {
        "title": "Machine Learning",
        "content": "Machine learning is the science of getting computers to act without being explicitly programmed, by training them on data."
    },
    {
        "title": "Autonomous Systems",
        "content": "Autonomous systems are machines capable of performing tasks independently without human intervention, a core focus of Dr. Aris."
    },
    {
        "title": "Humanoid Interaction",
        "content": "Humanoid interaction focuses on how robots can work alongside humans in shared spaces. The Robotics Lab is developing safe interaction protocols."
    },
    {
        "title": "Robot Prototype 'Ares'",
    "content": "The Robotics Lab is developing a prototype called 'Ares', a humanoid robot designed for warehouse logistics."
    },
    {
        "title": "Warehouse Logistics",
        "content": "Warehouse logistics involves the efficient movement and storage of goods. 'Ares' is designed to automate these tasks."
    },
    {
        "title": "Reinforcement Learning",
        "content": "Reinforcement Learning (RL) is used to train robots to walk and navigate complex environments by trial and error."
    },
    {
        "title": "Project Helios",
        "content": "Project Helios is a solar power management system for industrial use. It involves IoT sensors and grid synchronization."
    }
    ]

    for note_data in knowledge_base:
        # We use ingest_content directly to avoid file I/O in this test script
        ingestor.ingest_content(note_data["content"], note_data["title"])
        
    print(f"Successfully ingested {len(knowledge_base)} notes.")

if __name__ == "__main__":
    generate_test_data()

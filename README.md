# News Summarizer using Azure and Hugging Face

A serverless Python-based backend using Azure Functions integrated with **Hugging Face Transformers API** for summarizing online news articles.
This project demonstrates the deployment of an AI-powered summarization API on Azure, integrated with a simple HTML frontend hosted on Vercel.

# Objective

This project was built to:
-> Create a serverless summarization API using Azure Functions.
-> Integrate Hugging Face API models to summarize lengthy news articles.
-> Demonstrate secure handling of API keys using Azure Application Settings.
-> Deploy a functional AI backend and connect it to a web-based frontend.

# Features

-> Accepts any news article URL from the frontend.
-> Extracts and summarizes the article content using Hugging Face Transformers.
-> Built as a lightweight and serverless backend using Azure Functions.
-> Fully deployed on Azure with live endpoints for global access.
-> Serverless Backend can be accessed by using a sSimple HTML Page (deployed in vercel) and using a CURL command.

# Setup steps

### Step 1 : Setting up the Project Repository

        mkdir news-summarizer
        mkdir backend frontend

### Step 2: Configuring the Backend

        cd backend
        func init --worker-runtime python
        func new --name summarize_news --template "HTTP trigger"

    Install dependencies:
        pip install azure-functions requests werkzeug

    Then create the main backend file:
        "function_app.py"

    Add a file "requirements.txt" with the installed dependencies.

### Step 3: Hugging Face API Setup

    Visit Hugging Face > Settings > Access Tokens
    Create a new API token and copy it.

    Store it securely in Azure:
    Go to Azure Portal → Function App →  Security → Environmental Variables
    Add a new key-value pair:
    HUGGINGFACE_API_KEY = <YOUR_HUGGINGFACE_TOKEN>

### Step 4: Testing Locally

    Run the Azure Function locally:
        func start

    Test the endpoint:
        curl -X POST http://localhost:7071/api/summarize_news -H "Content-Type: application/json" -d "{\"url\":\"<ARTICLE_URL>\"}"

    Example:
        curl -X POST http://localhost:7071/api/summarize_news -H "Content-Type: application/json" -d "{\"url\":\"https://www.bbc.com/news/articles/c3w9378xp03o\"}"

### Step 5: Creating Azure Resources

        az group create --name NewsSummarizerGroup --location "centralindia"
        az storage account create --name newssummarizerstorage --location "centralindia" --resource-group NewsSummarizerGroup --sku Standard_LRS
        az functionapp create --resource-group NewsSummarizerGroup --consumption-plan-location "centralindia" --runtime python --runtime-version 3.10 --functions-version 4 --name news-summarizer-app --storage-account newssummarizerstorage --os-type Linux

### Step 6: Deploying the Function to Azure

    func azure functionapp publish <Summarizer-App-Name> --python

    Once deployed successfully, the invoke URL will appear:
        https://<Summarizer-App-Name>.azurewebsites.net/api/summarize_news

# Tech Stack

-> Backend: Python (Azure Functions)
-> API: Hugging Face Transformers
-> Frontend: HTML + JavaScript
-> Cloud Services: Azure Functions, Azure Storage
-> Deployment: Azure Function App (Backend), Vercel (Frontend)

# Reflection of What I Have Learnt

-> Learnt how to deploy and manage Python-based Azure Functions.
-> Learnt integration of Hugging Face API with Azure Functions.
-> Understood the process of managing environment variables securely in Azure.
-> Gained hands-on experience with serverless deployment pipelines.

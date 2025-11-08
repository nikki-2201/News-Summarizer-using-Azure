import azure.functions as func
import logging
import requests
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")
HUGGINGFACE_MODEL = "facebook/bart-large-cnn"  # Fast summarization model

@app.route(route="summarize_news", methods=["POST", "OPTIONS"])
def summarize_news(req: func.HttpRequest) -> func.HttpResponse:
    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(
            "",
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

    try:
        data = req.get_json()
        url = data.get("url")

        if not url:
            return func.HttpResponse(
                '{"error": "Missing URL."}',
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )

        # Fetch article text
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return func.HttpResponse(
                '{"error": "Failed to fetch article."}',
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )

        article_text = response.text[:4000]  # Keep within model limits

        # Summarize using Hugging Face API
        hf_response = requests.post(
            "https://api-inference.huggingface.co/models/" + HUGGINGFACE_MODEL,
            headers={
                "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"inputs": article_text},
            timeout=30,
        )

        if hf_response.status_code != 200:
            logging.error(f"Hugging Face API error: {hf_response.text}")
            return func.HttpResponse(
                '{"error": "Summarization failed."}',
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )

        summary = hf_response.json()[0]["summary_text"]

        return func.HttpResponse(
            f'{{"summary": "{summary}"}}',
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
        )

    except Exception as e:
        logging.error(f"Error: {e}")
        return func.HttpResponse(
            f'{{"error": "{str(e)}"}}',
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
        )

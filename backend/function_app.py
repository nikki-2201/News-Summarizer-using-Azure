import azure.functions as func
import requests
import os
import logging
import re

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")
PRIMARY_MODEL = "facebook/bart-large-cnn"
FALLBACK_MODEL = "sshleifer/distilbart-cnn-12-6"  # Lighter backup model

def clean_text(text):
    text = re.sub(r"<[^>]+>", "", text)  # Remove HTML tags
    text = re.sub(r"\s+", " ", text).strip()  # Normalize whitespace
    return text

@app.route(route="summarize_news", methods=["POST", "OPTIONS"])
def summarize_news(req: func.HttpRequest) -> func.HttpResponse:
    # Handle CORS
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

        # ✅ Step 1: Extract clean article text from Jina Reader API
        jina_url = f"https://r.jina.ai/{url}"
        jina_response = requests.get(jina_url, timeout=15)

        if jina_response.status_code != 200:
            return func.HttpResponse(
                f'{{"error": "Failed to fetch article (status {jina_response.status_code})."}}',
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )

        article_text = clean_text(jina_response.text)
        if len(article_text) < 300:
            return func.HttpResponse(
                '{"error": "Article too short or invalid."}',
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )

        article_text = article_text[:3000]  # Trim for model safety

        # ✅ Step 2: Summarize using Hugging Face API
        def summarize_with_model(model_name):
            response = requests.post(
                f"https://router.huggingface.co/hf-inference/models/{model_name}",
                headers={
                    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={"inputs": article_text},
                timeout=30,
            )
            return response

        hf_response = summarize_with_model(PRIMARY_MODEL)

        # Try fallback model if main one fails
        if hf_response.status_code != 200 or "error" in hf_response.text:
            logging.warning(f"Primary model failed, retrying with fallback: {FALLBACK_MODEL}")
            hf_response = summarize_with_model(FALLBACK_MODEL)

        # If still failed, return error
        if hf_response.status_code != 200:
            logging.error(f"Hugging Face error: {hf_response.text}")
            return func.HttpResponse(
                '{"error": "Summarization failed."}',
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )

        json_resp = hf_response.json()
        summary = json_resp[0].get("summary_text", "No summary available.") if isinstance(json_resp, list) else json_resp.get("summary_text", "No summary available.")

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

# AI Quiz Generator

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Run: `pip install -r requirements.txt`
4. Create `.streamlit/secrets.toml` and add:

```toml
OPENAI_API_KEY = "your_api_key_here"
```

5. Run: `streamlit run app.py`

## Deploy on Streamlit Community Cloud
1. Create a GitHub repository and upload `app.py` and `requirements.txt`.
2. Open https://share.streamlit.io/ and deploy the repository.
3. In the deployed app, open App settings → Secrets.
4. Add `OPENAI_API_KEY = "your_api_key_here"` and save.
5. Reboot the app.

Never paste your API key into public GitHub files or share it in chat.
API usage may incur charges. Have a parent/guardian handle account and billing if needed.

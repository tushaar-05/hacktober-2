"""SellSmart Mini - AI Product Listing Generator.

A bold, punchy Neo-Brutalism themed Streamlit application that generates
high-converting product titles, descriptions, and SEO tags for online sellers
and side hustlers using open-weight AI models.

Built for the DEV Community Hacktoberfest Open-Source AI Challenge: Week 2 ("Side Hustle").
"""

import os
import re
import time
from typing import Dict, List, Optional, Tuple
import requests
import streamlit as st
from dotenv import load_dotenv

# Load local environment variables from .env if available
load_dotenv()

# -----------------------------------------------------------------------------
# Configuration & Supported Open-Weight Models
# -----------------------------------------------------------------------------
OPEN_WEIGHT_MODELS: Dict[str, Dict[str, str]] = {
    "google/gemma-2-2b-it": {
        "name": "Google Gemma 2 2B Instruct",
        "license": "Gemma Terms of Use (Open Weights)",
        "params": "2.6B Parameters",
        "description": "Ultra-fast instruction following. Featured Hacktoberfest partner model.",
        "badge": "⚡ FEATURED GEMMA",
        "color": "#FFE600",
    },
    "meta-llama/Llama-3.2-3B-Instruct": {
        "name": "Meta Llama 3.2 3B Instruct",
        "license": "Llama 3.2 Community License",
        "params": "3.2B Parameters",
        "description": "Edge-optimized reasoning with high-conversion e-commerce copywriting.",
        "badge": "🔥 POPULAR PICK",
        "color": "#00F5A0",
    },
    "Qwen/Qwen2.5-7B-Instruct": {
        "name": "Qwen 2.5 7B Instruct",
        "license": "Apache 2.0 (Permissive)",
        "params": "7.6B Parameters",
        "description": "High-capacity creative storytelling and structured SEO tag generation.",
        "badge": "💎 APACHE 2.0",
        "color": "#FF66C4",
    },
}

SAMPLE_PRESETS = {
    "Artisan Leather Journal": {
        "name": "Handcrafted Vintage Leather Journal",
        "features": (
            "- Hand-stitched full-grain Italian leather cover\n"
            "- 200 pages of 120gsm unlined recycled cotton paper (fountain pen friendly)\n"
            "- Antique brass wrap-around C-clasp\n"
            "- Compact 7x5 inch size, travel ready\n"
            "- Refillable design with natural distressed finish"
        ),
        "audience": "Journalers, artists, travelers, writers, thoughtful gift shoppers",
        "tone": "Artisan & Storytelling (Etsy / Heritage)",
        "platform": "Etsy Marketplace",
        "price": "48.00",
    },
    "Ergonomic Ceramic Mug": {
        "name": "Nordic Matte Ceramic Desk Mug",
        "features": (
            "- 14oz capacity with heat-retaining double wall stoneware\n"
            "- Ergonomic thumb-rest comfort handle\n"
            "- Splash-proof sliding silicone lid\n"
            "- Microwave and dishwasher safe\n"
            "- Minimalist matte slate grey finish"
        ),
        "audience": "Remote workers, coffee enthusiasts, minimalists",
        "tone": "Modern & Conversion-Focused",
        "platform": "Shopify / Direct Store",
        "price": "29.50",
    },
}

# -----------------------------------------------------------------------------
# Streamlit Page Setup & Neo-Brutalism Design System
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SellSmart Mini ⚡ Neo-Brutalist AI Copywriter",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Bulletproof Neo-Brutalism CSS Injection
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700;900&display=swap');

    /* Global Typography & Canvas */
    html, body, [class*="css"], .stApp {
        font-family: 'Space Grotesk', -apple-system, sans-serif !important;
        background-color: #FEFCE8 !important;
        color: #000000 !important;
    }

    /* Force all text, paragraphs, spans, and labels to pure bold black */
    p, span, div, h1, h2, h3, h4, h5, h6, strong, em {
        color: #000000 !important;
    }

    /* Streamlit Widget Labels */
    label, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span {
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.02em !important;
        text-transform: uppercase !important;
    }

    /* Radio Buttons in Sidebar */
    [data-testid="stRadio"] label p, [data-testid="stRadio"] span {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 0.9rem !important;
    }

    /* Sidebar Background and Borders */
    section[data-testid="stSidebar"] {
        background-color: #FFFBEB !important;
        border-right: 4px solid #000000 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #000000 !important;
    }

    /* All Text Inputs, Textareas, and Dropdown Boxes - Force Solid White with Thick Black Borders */
    input, textarea, [data-baseweb="input"] input, [data-baseweb="textarea"] textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }
    input::placeholder, textarea::placeholder {
        color: #555555 !important;
        font-weight: 600 !important;
    }
    div[data-baseweb="input"], div[data-baseweb="textarea"] {
        background-color: #FFFFFF !important;
        border: 3.5px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #000000 !important;
    }
    div[data-baseweb="base-input"] {
        background-color: #FFFFFF !important;
    }

    /* Dropdown / Selectbox Containers */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 3.5px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #000000 !important;
        color: #000000 !important;
        font-weight: 800 !important;
    }
    div[data-baseweb="select"] * {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    ul[data-baseweb="menu"], [data-baseweb="menu"] li {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        font-weight: 700 !important;
    }

    /* Streamlit Containers with Border */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 3.5px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 6px 6px 0px #000000 !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
    }

    /* Neo-Brutalist Hero Banner */
    .nb-hero {
        background-color: #FFE600;
        border: 4px solid #000000;
        box-shadow: 8px 8px 0px #000000;
        padding: 24px 28px;
        margin-bottom: 24px;
    }
    .nb-hero-title {
        font-size: 2.6rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        text-transform: uppercase;
        color: #000000;
        margin: 0;
        line-height: 1.1;
    }
    .nb-hero-subtitle {
        font-size: 1.05rem;
        font-weight: 800;
        color: #000000;
        margin-top: 10px;
        margin-bottom: 0;
        background-color: #FFFFFF;
        display: inline-block;
        padding: 6px 14px;
        border: 2.5px solid #000000;
        box-shadow: 3px 3px 0px #000000;
    }
    .nb-badge-pill {
        display: inline-block;
        background-color: #FF66C4;
        color: #000000;
        font-weight: 900;
        font-size: 0.9rem;
        padding: 8px 16px;
        border: 3px solid #000000;
        box-shadow: 4px 4px 0px #000000;
        text-transform: uppercase;
        transform: rotate(-1.5deg);
    }

    /* Section Headers */
    .nb-card-header {
        font-size: 1.3rem;
        font-weight: 900;
        text-transform: uppercase;
        padding: 8px 16px;
        border: 3px solid #000000;
        display: inline-block;
        margin-bottom: 16px;
        box-shadow: 4px 4px 0px #000000;
    }
    .nb-card-header-yellow { background-color: #FFE600; }
    .nb-card-header-cyan { background-color: #00E5FF; }
    .nb-card-header-pink { background-color: #FF66C4; }
    .nb-card-header-green { background-color: #00F5A0; }

    /* Sticker Tags */
    .nb-sticker {
        display: inline-block;
        background-color: #FFFFFF;
        color: #000000;
        border: 2.5px solid #000000;
        box-shadow: 3px 3px 0px #000000;
        padding: 6px 14px;
        margin: 5px;
        font-weight: 900;
        font-size: 0.88rem;
        text-transform: uppercase;
    }
    .nb-sticker:nth-child(4n+1) { background-color: #FFE600; }
    .nb-sticker:nth-child(4n+2) { background-color: #00F5A0; }
    .nb-sticker:nth-child(4n+3) { background-color: #FF66C4; }
    .nb-sticker:nth-child(4n+4) { background-color: #00E5FF; }

    /* Neo-Brutalist Storefront Live Preview Card */
    .nb-store-preview {
        background-color: #FFFFFF;
        border: 4px solid #000000;
        box-shadow: 8px 8px 0px #000000;
        padding: 26px;
        margin-top: 10px;
    }
    .nb-store-title {
        font-size: 1.85rem;
        font-weight: 900;
        line-height: 1.2;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    .nb-store-price-tag {
        display: inline-block;
        background-color: #00F5A0;
        border: 3px solid #000000;
        box-shadow: 3.5px 3.5px 0px #000000;
        font-size: 1.4rem;
        font-weight: 900;
        padding: 4px 14px;
        margin-bottom: 16px;
    }
    .nb-btn-cart {
        background-color: #FFE600;
        color: #000000 !important;
        font-weight: 900;
        font-size: 1.15rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        text-align: center;
        padding: 14px;
        border: 3.5px solid #000000;
        box-shadow: 5px 5px 0px #000000;
        margin-bottom: 12px;
        cursor: pointer;
        display: block;
    }
    .nb-btn-cart:hover {
        transform: translate(2px, 2px);
        box-shadow: 3px 3px 0px #000000;
    }

    /* All Buttons */
    div.stButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 3.5px solid #000000 !important;
        box-shadow: 5px 5px 0px #000000 !important;
        border-radius: 0px !important;
        font-weight: 900 !important;
        font-size: 0.95rem !important;
        text-transform: uppercase !important;
        transition: all 0.1s ease !important;
    }
    div.stButton > button:hover {
        transform: translate(2px, 2px) !important;
        box-shadow: 2px 2px 0px #000000 !important;
        background-color: #FFE600 !important;
    }
    div.stButton > button[kind="primary"] {
        background-color: #00F5A0 !important;
        font-size: 1.25rem !important;
        padding: 16px 28px !important;
        box-shadow: 6px 6px 0px #000000 !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #FFE600 !important;
        transform: translate(3px, 3px) !important;
        box-shadow: 3px 3px 0px #000000 !important;
    }

    /* Expanders */
    details {
        background-color: #FFFFFF !important;
        border: 3px solid #000000 !important;
        box-shadow: 4px 4px 0px #000000 !important;
        border-radius: 0px !important;
    }
    summary {
        font-weight: 900 !important;
        color: #000000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Helper Functions: Credentials & Generation Logic
# -----------------------------------------------------------------------------
def resolve_api_token(user_provided_token: str) -> Optional[str]:
    """Resolve the Hugging Face API token from user input, Streamlit secrets, or environment."""
    if user_provided_token and user_provided_token.strip():
        return user_provided_token.strip()

    try:
        if "HF_TOKEN" in st.secrets:
            return st.secrets["HF_TOKEN"]
        if "HUGGINGFACEHUB_API_TOKEN" in st.secrets:
            return st.secrets["HUGGINGFACEHUB_API_TOKEN"]
    except Exception:
        pass

    env_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if env_token and env_token.strip():
        return env_token.strip()

    return None


def get_installed_ollama_models(host: str = "http://localhost:11434") -> List[str]:
    """Fetch list of locally installed models from Ollama."""
    try:
        resp = requests.get(f"{host.rstrip('/')}/api/tags", timeout=2.0)
        if resp.status_code == 200:
            data = resp.json()
            return [m["name"] for m in data.get("models", []) if "name" in m]
    except Exception:
        pass
    return []


def build_prompt(
    product_name: str,
    features: str,
    audience: str,
    tone: str,
    platform: str,
) -> Tuple[str, str]:
    """Construct system and user prompts to guide structured generation."""
    system_prompt = (
        "You are an expert e-commerce copywriter and SEO growth hacker. "
        "Your mission is to write high-converting, irresistible product copy for independent sellers and side hustlers. "
        "Always respond formatted with these exact delimiters:\n\n"
        "### TITLE:\n"
        "<A punchy, keyword-optimized e-commerce product title under 90 characters>\n\n"
        "### DESCRIPTION:\n"
        "<A persuasive, well-structured product narrative (2 to 3 paragraphs) highlighting benefits, craftsmanship, and specifications>\n\n"
        "### KEYWORDS:\n"
        "<10 to 15 high-volume search tags separated by commas>\n\n"
        "Do not include conversational filler, greetings, or meta-comments."
    )

    user_prompt = (
        f"Product Name: {product_name}\n"
        f"Storefront Platform: {platform}\n"
        f"Copywriting Tone: {tone}\n"
    )
    if audience.strip():
        user_prompt += f"Target Audience: {audience}\n"
    user_prompt += (
        f"Product Specifications & Details:\n{features}\n\n"
        "Generate the listing following the requested ### TITLE:, ### DESCRIPTION:, and ### KEYWORDS: format."
    )

    return system_prompt, user_prompt


def call_huggingface_model(
    model_id: str,
    system_prompt: str,
    user_prompt: str,
    token: str,
) -> str:
    """Invoke Hugging Face Serverless Inference API using huggingface_hub InferenceClient."""
    try:
        from huggingface_hub import InferenceClient

        client = InferenceClient(api_key=token)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=650,
                temperature=0.7,
            )
            return response.choices[0].message.content or ""
        except Exception:
            combined_prompt = f"{system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"
            return client.text_generation(
                prompt=combined_prompt,
                model=model_id,
                max_new_tokens=650,
                temperature=0.7,
            )

    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "authorization" in error_msg.lower():
            raise RuntimeError(
                "Authentication failed: The provided Hugging Face token is invalid. "
                "Check your token at https://huggingface.co/settings/tokens."
            ) from e
        if "503" in error_msg or "currently loading" in error_msg.lower():
            raise RuntimeError(
                f"Model '{model_id}' is warming up on the free tier. Please wait 20 seconds and click Generate again."
            ) from e
        if "429" in error_msg or "rate limit" in error_msg.lower():
            raise RuntimeError(
                "Hugging Face rate limit reached. Please wait a moment before trying again."
            ) from e
        raise RuntimeError(f"Inference error: {error_msg}") from e


def call_local_ollama(
    model_name: str,
    system_prompt: str,
    user_prompt: str,
    host: str = "http://localhost:11434",
) -> str:
    """Invoke local Ollama runtime for 100% offline, local inference."""
    endpoint = f"{host.rstrip('/')}/api/chat"
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {"temperature": 0.7},
    }
    try:
        resp = requests.post(endpoint, json=payload, timeout=90)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("message", {}).get("content", "")
        raise RuntimeError(f"Ollama returned HTTP status {resp.status_code}: {resp.text}")
    except requests.exceptions.ConnectionError as ce:
        raise RuntimeError(
            f"Could not connect to Ollama at '{host}'. "
            "Please ensure Ollama is running (`ollama serve`)."
        ) from ce


def parse_model_output(raw_text: str) -> Dict[str, str]:
    """Parse output into Title, Description, and Keywords sections."""
    parsed = {"title": "", "description": "", "keywords": "", "raw": raw_text}
    text = raw_text.strip()

    title_match = re.search(r"###?\s*TITLE:?\s*\n?(.*?)(?=###?\s*DESCRIPTION:?|\Z)", text, re.IGNORECASE | re.DOTALL)
    desc_match = re.search(r"###?\s*DESCRIPTION:?\s*\n?(.*?)(?=###?\s*KEYWORDS:?|\Z)", text, re.IGNORECASE | re.DOTALL)
    kw_match = re.search(r"###?\s*KEYWORDS:?\s*\n?(.*?)(?=\Z)", text, re.IGNORECASE | re.DOTALL)

    if title_match:
        parsed["title"] = title_match.group(1).strip().strip('"').strip("'")
    if desc_match:
        parsed["description"] = desc_match.group(1).strip()
    if kw_match:
        parsed["keywords"] = kw_match.group(1).strip()

    if not parsed["title"] and not parsed["description"]:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if lines:
            parsed["title"] = lines[0]
            parsed["description"] = "\n\n".join(lines[1:])

    return parsed


# -----------------------------------------------------------------------------
# Neo-Brutalist Sidebar: AI Engine & Provider Controls
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="background-color: #00F5A0; border: 3.5px solid #000; box-shadow: 4px 4px 0px #000; padding: 12px 14px; margin-bottom: 20px;">
            <h2 style="margin: 0; font-size: 1.5rem; font-weight: 900; text-transform: uppercase; color: #000;">⚡ AI ENGINE</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    provider = st.radio(
        "CHOOSE INFERENCE MODE",
        options=["Hugging Face Serverless (Cloud)", "Local Ollama (100% Offline)"],
        help="Select between free cloud serverless inference or 100% offline local inference.",
    )

    if provider == "Hugging Face Serverless (Cloud)":
        model_choice = st.selectbox(
            "SELECT OPEN-WEIGHT MODEL",
            options=list(OPEN_WEIGHT_MODELS.keys()),
            index=0,
            format_func=lambda m: f"{OPEN_WEIGHT_MODELS[m]['name']}",
        )
        selected_model_meta = OPEN_WEIGHT_MODELS[model_choice]

        st.markdown(
            f"""
            <div style="background-color: {selected_model_meta['color']}; border: 3px solid #000; box-shadow: 3.5px 3.5px 0px #000; padding: 10px 14px; margin: 12px 0;">
                <div style="font-weight: 900; font-size: 0.9rem; color: #000;">{selected_model_meta['badge']}</div>
                <div style="font-size: 0.85rem; font-weight: 800; color: #000; margin-top: 4px;">{selected_model_meta['params']} • {selected_model_meta['license']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown(
            '<div style="font-weight: 900; font-size: 1.1rem; margin-bottom: 8px;">🔑 API TOKEN</div>',
            unsafe_allow_html=True,
        )

        detected_token = resolve_api_token("")
        if detected_token:
            st.markdown(
                '<div class="nb-sticker" style="background-color: #00F5A0; width: 100%; text-align: center; margin: 0 0 10px 0;">✅ TOKEN DETECTED (.env / secrets)</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="nb-sticker" style="background-color: #FFE600; width: 100%; text-align: center; margin: 0 0 10px 0;">⚠️ NO TOKEN FOUND</div>',
                unsafe_allow_html=True,
            )

        manual_token = st.text_input(
            "OVERRIDE SESSION TOKEN",
            type="password",
            placeholder="hf_xxxxxxxxxxxxxxxxxxxxxxxx",
            help="Session memory only. Never committed to git.",
        )

        with st.expander("❓ GET FREE HF TOKEN"):
            st.markdown(
                """
                1. Sign up at [huggingface.co](https://huggingface.co/join).
                2. Visit [Access Tokens](https://huggingface.co/settings/tokens).
                3. Create a **Read** token.
                4. Put `HF_TOKEN=hf_...` in `.env`.
                """
            )
        active_token = resolve_api_token(manual_token)
    else:
        st.markdown(
            '<div style="font-weight: 900; font-size: 1.1rem; margin-bottom: 8px;">💻 LOCAL OLLAMA</div>',
            unsafe_allow_html=True,
        )
        ollama_host = st.text_input("HOST URL", value="http://localhost:11434")

        installed_models = get_installed_ollama_models(ollama_host)
        if installed_models:
            st.markdown(
                f'<div class="nb-sticker" style="background-color: #00F5A0; width: 100%; text-align: center; margin-bottom: 10px;">● CONNECTED ({len(installed_models)} MODELS)</div>',
                unsafe_allow_html=True,
            )
            ollama_model = st.selectbox("INSTALLED MODEL", options=installed_models, index=0)
        else:
            st.markdown(
                '<div class="nb-sticker" style="background-color: #FF66C4; width: 100%; text-align: center; margin-bottom: 10px;">⚠️ OLLAMA OFFLINE / NO MODELS</div>',
                unsafe_allow_html=True,
            )
            ollama_model = st.text_input("MODEL TAG", value="gemma2:2b")

        active_token = None
        model_choice = ollama_model

    st.markdown("---")
    st.markdown(
        """
        <div style="font-weight: 900; font-size: 0.82rem; text-transform: uppercase; text-align: center; color: #000;">
            DEV Community Hacktoberfest 2026<br>
            <strong>Side Hustle Challenge • Week 2</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# Main Header: Neo-Brutalist Hero Banner
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="nb-hero">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
            <div>
                <h1 class="nb-hero-title">⚡ SELLSMART MINI</h1>
                <div class="nb-hero-subtitle">
                    AI-POWERED E-COMMERCE COPYWRITER FOR SIDE HUSTLERS & CREATORS
                </div>
            </div>
            <div>
                <span class="nb-badge-pill">NEO-BRUTALIST EDITION</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Sample Preset Controls (Sticker Style)
# -----------------------------------------------------------------------------
preset_cols = st.columns([2, 1, 1])
with preset_cols[0]:
    st.markdown(
        '<div style="font-weight: 900; font-size: 1.05rem; color: #000000; padding: 8px 0;">⚡ INSTANT PRESETS (1-CLICK FILL):</div>',
        unsafe_allow_html=True,
    )
with preset_cols[1]:
    if st.button("📓 LEATHER JOURNAL", use_container_width=True):
        st.session_state["prod_name"] = SAMPLE_PRESETS["Artisan Leather Journal"]["name"]
        st.session_state["prod_features"] = SAMPLE_PRESETS["Artisan Leather Journal"]["features"]
        st.session_state["prod_audience"] = SAMPLE_PRESETS["Artisan Leather Journal"]["audience"]
        st.session_state["prod_tone"] = SAMPLE_PRESETS["Artisan Leather Journal"]["tone"]
        st.session_state["prod_platform"] = SAMPLE_PRESETS["Artisan Leather Journal"]["platform"]
        st.session_state["prod_price"] = SAMPLE_PRESETS["Artisan Leather Journal"]["price"]
with preset_cols[2]:
    if st.button("☕ CERAMIC DESK MUG", use_container_width=True):
        st.session_state["prod_name"] = SAMPLE_PRESETS["Ergonomic Ceramic Mug"]["name"]
        st.session_state["prod_features"] = SAMPLE_PRESETS["Ergonomic Ceramic Mug"]["features"]
        st.session_state["prod_audience"] = SAMPLE_PRESETS["Ergonomic Ceramic Mug"]["audience"]
        st.session_state["prod_tone"] = SAMPLE_PRESETS["Ergonomic Ceramic Mug"]["tone"]
        st.session_state["prod_platform"] = SAMPLE_PRESETS["Ergonomic Ceramic Mug"]["platform"]
        st.session_state["prod_price"] = SAMPLE_PRESETS["Ergonomic Ceramic Mug"]["price"]

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Input Form Section (Wrapped in Neo-Brutalist Boxed Containers)
# -----------------------------------------------------------------------------
form_col1, form_col2 = st.columns([3, 2], gap="large")

with form_col1:
    with st.container(border=True):
        st.markdown('<div class="nb-card-header nb-card-header-yellow">1. PRODUCT INTEL</div>', unsafe_allow_html=True)

        product_name = st.text_input(
            "PRODUCT TITLE / WORKING NAME *",
            value=st.session_state.get("prod_name", ""),
            placeholder="e.g. Handcrafted Vintage Leather Journal",
        )

        product_features = st.text_area(
            "KEY SPECIFICATIONS & FEATURES *",
            value=st.session_state.get("prod_features", ""),
            height=170,
            placeholder=(
                "- Hand-stitched full-grain Italian leather cover\n"
                "- 200 unlined cotton deckle-edge pages\n"
                "- Antique brass wrap-around C-clasp\n"
                "- Travel size 7x5 inches, fountain pen friendly"
            ),
        )

        target_audience = st.text_input(
            "TARGET AUDIENCE (OPTIONAL)",
            value=st.session_state.get("prod_audience", ""),
            placeholder="e.g. Writers, artists, travelers, thoughtful gift shoppers",
        )

with form_col2:
    with st.container(border=True):
        st.markdown('<div class="nb-card-header nb-card-header-cyan">2. STORE SETTINGS</div>', unsafe_allow_html=True)

        platform_options = [
            "Shopify / Brand Store",
            "Etsy Marketplace",
            "eBay Listing",
            "Amazon Store",
            "Social Commerce (Instagram / TikTok)",
        ]
        platform = st.selectbox(
            "TARGET STOREFRONT",
            options=platform_options,
            index=0,
        )

        tone_options = [
            "Modern & Conversion-Focused",
            "Artisan & Storytelling (Etsy / Heritage)",
            "Luxury, Elegant & Premium",
            "Bold & Punchy (Neo-Brutalist)",
            "Minimalist & Direct",
        ]
        tone = st.selectbox(
            "COPYWRITING TONE",
            options=tone_options,
            index=0,
        )

        price_input = st.text_input(
            "DISPLAY PRICE ($ USD)",
            value=st.session_state.get("prod_price", "45.00"),
            placeholder="45.00",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button("⚡ GENERATE LISTING NOW", type="primary", use_container_width=True)

# -----------------------------------------------------------------------------
# Execution & Validation Workflow
# -----------------------------------------------------------------------------
if generate_btn:
    if not product_name.strip():
        st.markdown(
            '<div style="background-color: #FFE600; border: 3.5px solid #000; box-shadow: 5px 5px 0px #000; padding: 14px 18px; font-weight: 900; margin: 16px 0;">⚠️ MISSING TITLE: Please provide a product title!</div>',
            unsafe_allow_html=True,
        )
    elif not product_features.strip():
        st.markdown(
            '<div style="background-color: #FFE600; border: 3.5px solid #000; box-shadow: 5px 5px 0px #000; padding: 14px 18px; font-weight: 900; margin: 16px 0;">⚠️ MISSING FEATURES: Please enter at least a few bullet points!</div>',
            unsafe_allow_html=True,
        )
    elif provider == "Hugging Face Serverless (Cloud)" and not active_token:
        st.markdown(
            '<div style="background-color: #FF66C4; border: 3.5px solid #000; box-shadow: 5px 5px 0px #000; padding: 14px 18px; font-weight: 900; margin: 16px 0;">🔑 TOKEN REQUIRED: Please provide your free Hugging Face token in the sidebar or in your .env file!</div>',
            unsafe_allow_html=True,
        )
    else:
        system_p, user_p = build_prompt(
            product_name=product_name,
            features=product_features,
            audience=target_audience,
            tone=tone,
            platform=platform,
        )

        with st.spinner(f"⚡ RUNNING OPEN-WEIGHT INFERENCE WITH {model_choice.upper()}..."):
            start_time = time.time()
            error_occurred = False
            raw_output = ""

            try:
                if provider == "Hugging Face Serverless (Cloud)":
                    raw_output = call_huggingface_model(
                        model_id=model_choice,
                        system_prompt=system_p,
                        user_prompt=user_p,
                        token=active_token,  # type: ignore
                    )
                else:
                    raw_output = call_local_ollama(
                        model_name=ollama_model,
                        system_prompt=system_p,
                        user_prompt=user_p,
                        host=ollama_host,
                    )
            except Exception as exc:
                error_occurred = True
                st.markdown(
                    f'<div style="background-color: #FF66C4; border: 3.5px solid #000; box-shadow: 5px 5px 0px #000; padding: 14px 18px; font-weight: 900; margin: 16px 0;">❌ ERROR: {exc}</div>',
                    unsafe_allow_html=True,
                )

            elapsed = round(time.time() - start_time, 2)

            if not error_occurred:
                if not raw_output or not raw_output.strip():
                    st.warning("Model returned empty response. Please retry.")
                else:
                    st.session_state["last_result"] = parse_model_output(raw_output)
                    st.session_state["last_elapsed"] = elapsed
                    st.session_state["last_model"] = model_choice
                    st.session_state["saved_price"] = price_input.strip() or "45.00"
                    st.markdown(
                        f'<div class="nb-sticker" style="background-color: #00F5A0; font-size: 1rem; padding: 10px 16px; margin: 16px 0;">⚡ GENERATED IN {elapsed}S WITH {model_choice}</div>',
                        unsafe_allow_html=True,
                    )

# -----------------------------------------------------------------------------
# Results Presentation (Neo-Brutalist Layout)
# -----------------------------------------------------------------------------
if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    elapsed_sec = st.session_state.get("last_elapsed", 0)
    used_model = st.session_state.get("last_model", "Open-Weight Model")
    item_price = st.session_state.get("saved_price", "45.00")

    title_text = result.get("title", product_name)
    desc_text = result.get("description", "")
    keywords_raw = result.get("keywords", "")

    clean_tags: List[str] = [
        tag.strip().strip("#").strip()
        for tag in keywords_raw.replace("\n", ",").split(",")
        if tag.strip()
    ]

    st.markdown("<br><hr style='border: 2.5px solid #000;'>", unsafe_allow_html=True)

    tab_preview, tab_copy, tab_seo = st.tabs(
        ["🛍️ LIVE STOREFRONT PREVIEW", "📋 MERCHANT CLIPBOARD", "🔍 GOOGLE SEO SNIPPET"]
    )

    # TAB 1: Live Storefront Mockup
    with tab_preview:
        st.markdown(
            f"""
            <div class="nb-store-preview">
                <div style="font-weight: 900; font-size: 0.88rem; text-transform: uppercase; margin-bottom: 8px; color: #000;">
                    HOME / CATALOG / <strong>{title_text}</strong>
                </div>
                <div class="nb-store-title">{title_text}</div>
                <div class="nb-store-price-tag">${item_price} USD</div>
                <div style="font-weight: 900; margin-bottom: 16px; color: #008060;">
                    ● IN STOCK — READY TO SHIP
                </div>
                <div class="nb-btn-cart">🛒 ADD TO CART</div>
                <div style="border-top: 3.5px solid #000; padding-top: 18px; margin-top: 18px; font-size: 1.05rem; line-height: 1.6; font-weight: 600; color: #000;">
                    {desc_text.replace(chr(10), '<br>')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="nb-card-header nb-card-header-pink">SEO STICKER TAGS</div>', unsafe_allow_html=True)
        if clean_tags:
            tag_html = "".join([f'<span class="nb-sticker">#{t}</span>' for t in clean_tags])
            st.markdown(tag_html, unsafe_allow_html=True)

    # TAB 2: Merchant Copy Tools
    with tab_copy:
        st.markdown('<div class="nb-card-header nb-card-header-yellow">1. PRODUCT TITLE</div>', unsafe_allow_html=True)
        st.text_input("Copy Title", value=title_text, label_visibility="collapsed")

        st.markdown('<div class="nb-card-header nb-card-header-cyan">2. PRODUCT DESCRIPTION</div>', unsafe_allow_html=True)
        st.text_area("Copy Description", value=desc_text, height=180, label_visibility="collapsed")

        st.markdown('<div class="nb-card-header nb-card-header-green">3. COMMA-SEPARATED TAGS</div>', unsafe_allow_html=True)
        st.text_input("Copy Tags", value=", ".join(clean_tags), label_visibility="collapsed")

        with st.expander("📄 EXPORT COMPLETE MARKDOWN"):
            full_export = (
                f"# {title_text}\n\n"
                f"**Price:** ${item_price} USD\n\n"
                f"## Description\n{desc_text}\n\n"
                f"## Tags\n{', '.join(clean_tags)}\n"
            )
            st.code(full_export, language="markdown")

    # TAB 3: Google SEO Snippet Preview
    with tab_seo:
        url_slug = re.sub(r"[^a-zA-Z0-9]+", "-", title_text.lower()).strip("-")
        truncated_desc = (desc_text[:155] + "...") if len(desc_text) > 155 else desc_text

        st.markdown(
            f"""
            <div style="background-color: #FFFFFF; border: 3.5px solid #000; box-shadow: 6px 6px 0px #000; padding: 22px;">
                <div style="color: #1A0DAB; font-size: 1.3rem; font-weight: 900; text-decoration: underline; margin-bottom: 6px;">
                    {title_text} | Official Store
                </div>
                <div style="color: #006621; font-size: 0.92rem; font-weight: 800; margin-bottom: 10px;">
                    https://your-store.com/products/{url_slug}
                </div>
                <div style="font-size: 1rem; font-weight: 600; color: #111111; line-height: 1.5;">
                    {truncated_desc}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

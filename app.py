"""SellSmart Mini - AI Product Listing Generator.

A lightweight, beginner-friendly Streamlit web application that generates
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
        "params": "2.6 Billion parameters",
        "description": "Ultra-lightweight, efficient, high-accuracy instruction-tuned open-weight model.",
        "badge": "Featured HF26 Partner",
    },
    "meta-llama/Llama-3.2-3B-Instruct": {
        "name": "Meta Llama 3.2 3B Instruct",
        "license": "Llama 3.2 Community License",
        "params": "3.2 Billion parameters",
        "description": "Edge-optimized reasoning and concise multilingual copywriting.",
        "badge": "Popular Open-Weight",
    },
    "Qwen/Qwen2.5-7B-Instruct": {
        "name": "Qwen 2.5 7B Instruct",
        "license": "Apache 2.0 (Fully Permissive)",
        "params": "7.6 Billion parameters",
        "description": "High-capacity creative copywriting and structured tag formatting.",
        "badge": "Permissive License",
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
        "tone": "Artisan & Storytelling (Etsy style)",
        "platform": "Etsy",
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
        "platform": "Shopify / General Store",
    },
}

# -----------------------------------------------------------------------------
# Streamlit Page Setup & Custom Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SellSmart Mini — AI Product Listing Generator",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom minimal CSS for clean visual hierarchy and badge chips
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        color: #1E293B;
    }
    .main-subtitle {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .badge-tag {
        display: inline-block;
        background-color: #EEF2F6;
        color: #1E293B;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 3px 4px;
        border: 1px solid #CBD5E1;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    .stCodeBlock {
        border-radius: 8px !important;
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

    # Check Streamlit secrets
    try:
        if "HF_TOKEN" in st.secrets:
            return st.secrets["HF_TOKEN"]
        if "HUGGINGFACEHUB_API_TOKEN" in st.secrets:
            return st.secrets["HUGGINGFACEHUB_API_TOKEN"]
    except Exception:
        pass

    # Check environment variables
    env_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if env_token and env_token.strip():
        return env_token.strip()

    return None


def build_prompt(
    product_name: str,
    features: str,
    audience: str,
    tone: str,
    platform: str,
) -> Tuple[str, str]:
    """Construct system and user prompts to guide structured generation."""
    system_prompt = (
        "You are an expert e-commerce copywriter and SEO specialist. "
        "Your mission is to help small independent online sellers and side hustlers "
        "create compelling, high-converting product listings. "
        "Always respond with exactly three distinct sections formatted as follows:\n\n"
        "### TITLE:\n"
        "<A catchy, keyword-rich product title (under 90 characters)>\n\n"
        "### DESCRIPTION:\n"
        "<A persuasive, well-structured product description (2 to 3 paragraphs) highlighting benefits, craftsmanship, and specifications>\n\n"
        "### KEYWORDS:\n"
        "<10 to 15 relevant, high-search-intent tags separated by commas>\n\n"
        "Do not include introductory pleasantries or trailing meta-chatter."
    )

    user_prompt = (
        f"Product Name: {product_name}\n"
        f"Target Platform: {platform}\n"
        f"Copywriting Tone: {tone}\n"
    )
    if audience.strip():
        user_prompt += f"Target Audience: {audience}\n"
    user_prompt += (
        f"Key Features & Specifications:\n{features}\n\n"
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

        # Use chat completions endpoint for instruction-tuned open-weight models
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=650,
                temperature=0.7,
            )
            return response.choices[0].message.content or ""
        except Exception as chat_err:
            # Fallback to direct conversational / text generation if chat completion isn't available
            combined_prompt = f"{system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"
            return client.text_generation(
                prompt=combined_prompt,
                model=model_id,
                max_new_tokens=650,
                temperature=0.7,
            )

    except Exception as e:
        error_msg = str(e)
        # Check for specific actionable HTTP status codes
        if "401" in error_msg or "Invalid username or password" in error_msg or "authorization" in error_msg.lower():
            raise RuntimeError(
                "Authentication failed: The provided Hugging Face token is invalid or unauthorized. "
                "Please verify your token at https://huggingface.co/settings/tokens."
            ) from e
        if "503" in error_msg or "currently loading" in error_msg.lower():
            raise RuntimeError(
                f"Model '{model_id}' is currently spinning up on Hugging Face free tier. "
                "Please wait 15–30 seconds and click Generate again."
            ) from e
        if "429" in error_msg or "rate limit" in error_msg.lower():
            raise RuntimeError(
                "Hugging Face rate limit reached. Please wait a moment before trying again."
            ) from e
        raise RuntimeError(f"Hugging Face inference error: {error_msg}") from e


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


def call_local_ollama(
    model_name: str,
    system_prompt: str,
    user_prompt: str,
    host: str = "http://localhost:11434",
) -> str:
    """Optionally invoke a local Ollama instance for 100% offline, local inference."""
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
            f"Could not connect to local Ollama at '{host}'. "
            "Please ensure Ollama is running (`ollama serve`) or switch back to the Hugging Face provider."
        ) from ce


def parse_model_output(raw_text: str) -> Dict[str, str]:
    """Parse output into Title, Description, and Keywords sections."""
    parsed = {"title": "", "description": "", "keywords": "", "raw": raw_text}

    # Normalize newlines
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

    # Fallback heuristic if markdown headers were not strictly followed
    if not parsed["title"] and not parsed["description"]:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if lines:
            parsed["title"] = lines[0]
            parsed["description"] = "\n\n".join(lines[1:])

    return parsed


# -----------------------------------------------------------------------------
# Sidebar: Model, Provider, & API Configuration
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ AI Configuration")

    provider = st.radio(
        "Inference Provider",
        options=["Hugging Face Serverless (Cloud)", "Local Ollama (100% Offline)"],
        help="Choose between free cloud serverless inference with open weights or local offline inference.",
    )

    if provider == "Hugging Face Serverless (Cloud)":
        model_choice = st.selectbox(
            "Open-Weight Model",
            options=list(OPEN_WEIGHT_MODELS.keys()),
            index=0,
            format_func=lambda m: f"{OPEN_WEIGHT_MODELS[m]['name']}",
        )
        selected_model_meta = OPEN_WEIGHT_MODELS[model_choice]

        st.caption(f"**License:** {selected_model_meta['license']}")
        st.caption(f"**Size:** {selected_model_meta['params']}")
        st.info(f"💡 {selected_model_meta['description']}")

        # API Token Resolution
        st.markdown("---")
        st.subheader("🔑 Hugging Face Token")

        detected_token = resolve_api_token("")
        token_status_msg = "✅ Detected from environment / secrets" if detected_token else "⚠️ Not detected"
        st.caption(f"Status: **{token_status_msg}**")

        manual_token = st.text_input(
            "Override Token (Optional)",
            type="password",
            placeholder="hf_xxxxxxxxxxxxxxxxxxxxxxxx",
            help="Your token is kept strictly in memory for this session and never saved or committed.",
        )

        with st.expander("❓ How to get a free HF Token"):
            st.markdown(
                """
                1. Sign up for free at [huggingface.co](https://huggingface.co/join).
                2. Navigate to [Settings → Access Tokens](https://huggingface.co/settings/tokens).
                3. Create a **Read** token.
                4. Paste it above or save it in `.env` as `HF_TOKEN=hf_...`.
                """
            )
        active_token = resolve_api_token(manual_token)
    else:
        st.subheader("💻 Local Ollama Settings")
        ollama_host = st.text_input("Host URL", value="http://localhost:11434")

        installed_models = get_installed_ollama_models(ollama_host)
        if installed_models:
            st.success(f"✅ Connected! Found {len(installed_models)} local model(s).")
            ollama_model = st.selectbox(
                "Select Installed Model",
                options=installed_models,
                index=0,
            )
        else:
            st.warning("⚠️ No installed models detected or Ollama server unreachable.")
            ollama_model = st.text_input("Ollama Model Tag", value="gemma2:2b")
            st.caption("Pull a model in terminal: `ollama pull gemma2:2b`")

        st.caption("Runs 100% locally on your machine. No API token required.")
        active_token = None
        model_choice = ollama_model

    st.markdown("---")
    st.markdown(
        "**Hacktoberfest 2026: Side Hustle**  \n"
        "Built with open-weight models for independent creators & online sellers. 🚀"
    )

# -----------------------------------------------------------------------------
# Main Application Header & Description
# -----------------------------------------------------------------------------
st.markdown('<div class="main-title">🛍️ SellSmart Mini</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="main-subtitle">AI-powered listing writer for Etsy, eBay, Shopify & Amazon sellers — '
    'built on open-weight language models.</div>',
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Sample Preset Fill Controls
# -----------------------------------------------------------------------------
preset_cols = st.columns([2, 1, 1])
with preset_cols[0]:
    st.write("💡 Need inspiration? Try a sample preset to test instantly:")
with preset_cols[1]:
    if st.button("Sample 1: Leather Journal", use_container_width=True):
        st.session_state["prod_name"] = SAMPLE_PRESETS["Artisan Leather Journal"]["name"]
        st.session_state["prod_features"] = SAMPLE_PRESETS["Artisan Leather Journal"]["features"]
        st.session_state["prod_audience"] = SAMPLE_PRESETS["Artisan Leather Journal"]["audience"]
        st.session_state["prod_tone"] = SAMPLE_PRESETS["Artisan Leather Journal"]["tone"]
        st.session_state["prod_platform"] = SAMPLE_PRESETS["Artisan Leather Journal"]["platform"]
with preset_cols[2]:
    if st.button("Sample 2: Ceramic Mug", use_container_width=True):
        st.session_state["prod_name"] = SAMPLE_PRESETS["Ergonomic Ceramic Mug"]["name"]
        st.session_state["prod_features"] = SAMPLE_PRESETS["Ergonomic Ceramic Mug"]["features"]
        st.session_state["prod_audience"] = SAMPLE_PRESETS["Ergonomic Ceramic Mug"]["audience"]
        st.session_state["prod_tone"] = SAMPLE_PRESETS["Ergonomic Ceramic Mug"]["tone"]
        st.session_state["prod_platform"] = SAMPLE_PRESETS["Ergonomic Ceramic Mug"]["platform"]

st.markdown("---")

# -----------------------------------------------------------------------------
# Input Form Section
# -----------------------------------------------------------------------------
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.subheader("1. Product Information")

    product_name = st.text_input(
        "Product Name *",
        value=st.session_state.get("prod_name", ""),
        placeholder="e.g. Handcrafted Vintage Leather Journal",
        help="Give your product a clear, descriptive working name.",
    )

    product_features = st.text_area(
        "Product Features & Key Details *",
        value=st.session_state.get("prod_features", ""),
        height=170,
        placeholder=(
            "- Material, dimensions, finish\n"
            "- Key benefits and unique handcrafted attributes\n"
            "- Use cases, included accessories, or care instructions"
        ),
        help="Bullet points or sentences describing materials, size, craftsmanship, and benefits.",
    )

    target_audience = st.text_input(
        "Target Audience (Optional)",
        value=st.session_state.get("prod_audience", ""),
        placeholder="e.g. Writers, travelers, art students, gift shoppers",
        help="Who is this product designed for? Helps the AI tailor vocabulary and tone.",
    )

with col_right:
    st.subheader("2. Tone & Platform Settings")

    platform_options = [
        "Etsy",
        "Shopify / General Store",
        "eBay",
        "Amazon",
        "Instagram / Social Shop",
    ]
    platform = st.selectbox(
        "Target Platform",
        options=platform_options,
        index=platform_options.index(st.session_state.get("prod_platform", "Etsy"))
        if st.session_state.get("prod_platform") in platform_options
        else 0,
        help="Optimizes copywriting conventions (e.g. storytelling for Etsy, bullet specifications for Amazon).",
    )

    tone_options = [
        "Artisan & Storytelling (Etsy style)",
        "Modern & Conversion-Focused",
        "Luxury & Elegant",
        "Casual & Friendly",
        "Technical & Feature-Driven",
    ]
    tone = st.selectbox(
        "Copywriting Tone",
        options=tone_options,
        index=tone_options.index(st.session_state.get("prod_tone", "Artisan & Storytelling (Etsy style)"))
        if st.session_state.get("prod_tone") in tone_options
        else 0,
        help="Adjust the voice and narrative mood of the generated listing.",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("✨ Generate Listing", type="primary", use_container_width=True)

# -----------------------------------------------------------------------------
# Generation & Validation Workflow
# -----------------------------------------------------------------------------
if generate_btn:
    # 1. Validation checks
    if not product_name.strip():
        st.warning("⚠️ Please provide a **Product Name** before generating.")
    elif not product_features.strip():
        st.warning("⚠️ Please provide at least a few **Product Features & Key Details**.")
    elif provider == "Hugging Face Serverless (Cloud)" and not active_token:
        st.error(
            "🔑 **Hugging Face API Token Required:**  \n"
            "An API token is needed to query the open-weight model through Hugging Face's free inference API.  \n"
            "Please enter your token in the sidebar (under **🔑 Hugging Face Token**) or add `HF_TOKEN=hf_...` "
            "to your `.env` file or Streamlit secrets."
        )
    else:
        # 2. Execution with timing and error handling
        system_p, user_p = build_prompt(
            product_name=product_name,
            features=product_features,
            audience=target_audience,
            tone=tone,
            platform=platform,
        )

        with st.spinner(f"Generating optimized listing using {model_choice}..."):
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
                st.error(f"❌ **Generation Failed:** {exc}")

            elapsed = round(time.time() - start_time, 2)

            if not error_occurred:
                if not raw_output or not raw_output.strip():
                    st.error("❌ The AI model returned an empty response. Please retry with slightly adjusted input.")
                else:
                    st.session_state["last_result"] = parse_model_output(raw_output)
                    st.session_state["last_elapsed"] = elapsed
                    st.session_state["last_model"] = model_choice
                    st.success(f"Listing generated in {elapsed}s with `{model_choice}`!")

# -----------------------------------------------------------------------------
# Results Presentation Section
# -----------------------------------------------------------------------------
if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    elapsed_sec = st.session_state.get("last_elapsed", 0)
    used_model = st.session_state.get("last_model", "Open-weight model")

    st.markdown("---")
    st.subheader("📦 Generated Listing Results")

    # Metrics row
    metric_cols = st.columns(3)
    with metric_cols[0]:
        st.caption(f"**Model:** `{used_model}`")
    with metric_cols[1]:
        st.caption(f"**Inference Latency:** {elapsed_sec} seconds")
    with metric_cols[2]:
        st.caption("**Format:** Ready for copy & paste")

    # 1. Product Title
    st.markdown("#### 1. Optimized Product Title")
    title_text = result.get("title", "")
    st.text_input("Title (Copy-Friendly)", value=title_text, label_visibility="collapsed")

    # 2. Product Description
    st.markdown("#### 2. Product Description")
    desc_text = result.get("description", "")
    st.markdown(desc_text)
    with st.expander("📋 View Raw Text for Copying"):
        st.code(desc_text, language="markdown")

    # 3. SEO Keywords & Search Tags
    st.markdown("#### 3. SEO Keywords & Search Tags")
    keywords_raw = result.get("keywords", "")
    # Parse tag chips
    clean_tags: List[str] = [
        tag.strip().strip("#").strip()
        for tag in keywords_raw.replace("\n", ",").split(",")
        if tag.strip()
    ]

    if clean_tags:
        tags_html = "".join([f'<span class="badge-tag">🏷️ {t}</span>' for t in clean_tags])
        st.markdown(tags_html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("📋 Copy Comma-Separated Tags"):
        st.code(", ".join(clean_tags) if clean_tags else keywords_raw, language="text")

    # Complete Listing Export
    with st.expander("📄 Export Full Listing (Markdown)"):
        full_export = (
            f"# {title_text}\n\n"
            f"## Description\n{desc_text}\n\n"
            f"## Tags\n{', '.join(clean_tags)}\n"
        )
        st.code(full_export, language="markdown")

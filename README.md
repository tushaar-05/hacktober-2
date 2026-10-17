# SellSmart Mini 🛍️

> **AI Product Listing & SEO Generator for Online Sellers & Side Hustlers**  
> *Built for the DEV Community Hacktoberfest Open-Source AI Challenge: Week 2 ("Side Hustle")*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red.svg)](https://streamlit.io/)
[![Model: Gemma 2 2B](https://img.shields.io/badge/Model-Gemma--2--2B--Instruct-orange.svg)](https://huggingface.co/google/gemma-2-2b-it)

---

## 📖 Overview & Problem Solved

Starting an e-commerce side hustle—selling handcrafted goods on **Etsy**, vintage collectibles on **eBay**, custom apparel on **Shopify**, or products on **Amazon**—is one of the most accessible ways for independent creators to monetize their skills.

However, copywriting and search engine optimization (SEO) present major hurdles:
1. **Time Drain:** Drafting compelling titles, detailed multi-paragraph product descriptions, and researching 10–15 platform-tailored SEO tags takes 15–30 minutes per listing.
2. **Expensive SaaS Tools:** Proprietary commercial copywriting subscriptions cost $25–$75/month—an unsustainable overhead when testing new product ideas.
3. **Data Lock-in & Privacy:** Closed APIs retain proprietary product drafts and manufacturer details on centralized servers.

**SellSmart Mini** is a lightweight, beginner-friendly open-source tool built with Python and Streamlit. Sellers input basic product details and select their platform and copywriting tone. SellSmart Mini generates an optimized title, rich product narrative, and high-ranking search tags in seconds using open-weight AI models.

---

## 🌟 Key Features

- **Neo-Brutalism Design System:** Distinctive high-contrast aesthetic featuring thick 3.5px black borders, unblurred hard drop-shadows (`box-shadow: 6px 6px 0px #000`), vibrant electric palette (Cyber Yellow `#FFE600`, Mint Green `#00F5A0`, Hot Pink `#FF66C4`, Electric Cyan `#00E5FF`), and retro sticker tags.
- **🛍️ Live Storefront Mockup Preview (PDP):** Visualizes how generated copy, price tags, and narrative styling render on an actual e-commerce product page, complete with a bold *"Add to Cart"* action.
- **🔍 Google Search Snippet Preview:** Real-time search engine preview displaying page title, product URL slug, and meta description snippet.
- **Open-Weight AI Generation:** Real model inference using open-weight architectures (Google Gemma 2, Meta Llama 3.2, Qwen 2.5). No mock hardcoding.
- **Dual Inference Providers:**
  - *Cloud Serverless (Default):* Free Hugging Face Serverless Inference API (requires only a free HF access token, no GPU required).
  - *Local Offline:* 100% offline inference with local Ollama (`localhost:11434`), zero tokens or cloud dependency needed.
- **Copy-Friendly Merchant Tools:** Formatted blocks for instant 1-click clipboard copying:
  - 📌 High-ranking, keyword-rich Product Title (under 90 chars).
  - 📝 Multi-paragraph persuasive Product Description highlighting materials, benefits, and specifications.
  - 🏷️ Visual badge chips + comma-separated SEO keyword list.
  - 📄 Complete Markdown listing export.
- **1-Click Sample Presets:** Pre-configured demo inputs (Artisan Leather Journal and Ceramic Desk Mug) for instant manual testing.
- **Graceful Error Handling:** Form validation for empty inputs, model warmup notifications (HTTP 503), rate limit explanations, and helpful guidance for missing credentials.

---

## 🧠 Open-Weight Models & Licenses

SellSmart Mini is designed to celebrate open-source AI and transparent weights:

| Model ID | Provider / Creator | Parameters | License | Strengths |
| :--- | :--- | :--- | :--- | :--- |
| **`google/gemma-2-2b-it`** *(Default)* | Google DeepMind | 2.6B | [Gemma Terms of Use](https://ai.google.dev/gemma/terms) | Ultra-lightweight, rapid inference, exceptional instruction adherence. Qualifies for Hacktoberfest *Best Use of Gemma*. |
| **`meta-llama/Llama-3.2-3B-Instruct`** | Meta | 3.2B | [Llama 3.2 Community License](https://llama.meta.com/license/) | Concise copywriting, edge-optimized, robust reasoning. |
| **`Qwen/Qwen2.5-7B-Instruct`** | Alibaba Cloud / Qwen | 7.6B | [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) | Permissive open-source license, rich product storytelling, detailed SEO tagging. |

### Why Open-Weight AI Matters for Side Hustlers
- **Predictable, Zero-Inflation Cost:** Open weights can be hosted locally or run on free and cost-effective open inference endpoints. Sellers avoid unpredictable closed API price hikes.
- **Privacy & Trade Secret Protection:** Craft makers, wholesalers, and vintage curators protect unpublished products and margins by running inference locally without corporate surveillance.
- **Model Portability:** Sellers can swap between Gemma, Llama, and Qwen without changing a line of business logic.

---

## 🚀 Quickstart & Installation

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed.
- (Optional) A free Hugging Face account to obtain a token, or Ollama installed locally.

### 2. Clone and Setup Environment

```bash
# Clone the repository
git clone https://github.com/your-username/sellsmart-mini.git
cd sellsmart-mini

# Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Credentials

#### Option A: Hugging Face Serverless (Recommended, Free)
1. Sign up for a free account at [huggingface.co](https://huggingface.co/join).
2. Go to **Settings → Access Tokens** ([huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)).
3. Create a **Read** token.
4. Copy `.env.example` to `.env` and set your token:

```bash
cp .env.example .env
```

Edit `.env`:
```env
HF_TOKEN=hf_your_actual_token_here
```

*(Note: You can also skip `.env` and paste your token directly into the sidebar in the running app!)*

#### Option B: 100% Offline with Ollama
1. Install [Ollama](https://ollama.ai/).
2. Pull an open model: `ollama pull gemma2:2b`
3. Launch Ollama: `ollama serve`
4. In SellSmart Mini's sidebar, select **Local Ollama (100% Offline)**.

---

## 💻 Running the Application

Launch the Streamlit app:

```bash
# Make sure your virtual environment is active
source .venv/bin/activate

# Run the app
streamlit run app.py
```

Streamlit will print a local URL (typically `http://localhost:8501`). Open it in your web browser.

---

## 🧪 Manual Testing Checklist

| Step | Action | Expected Behavior | Status |
| :--- | :--- | :--- | :--- |
| **1. UI Load** | Launch `streamlit run app.py` | Clean UI renders with title, sidebar options, sample preset buttons, and input form. | Pass |
| **2. Validation** | Leave product name blank and click *Generate Listing* | Warning message: *"Please provide a Product Name before generating."* | Pass |
| **3. Sample Fill** | Click *Sample 1: Leather Journal* | Product inputs automatically populate with vintage leather journal specifications. | Pass |
| **4. Missing Token** | Switch to Hugging Face provider with no token configured | Error message clearly explains how to obtain and provide `HF_TOKEN`. | Pass |
| **5. Inference** | Provide valid `HF_TOKEN` and click *Generate Listing* | Spinner appears while calling Gemma 2; completes in a few seconds and displays Title, Description, and SEO tags. | Pass |
| **6. Copy & Export** | Inspect output code blocks | Title, description, and comma-separated tags are cleanly formatted for 1-click clipboard copying. | Pass |

---

## 🛠️ Project Structure

```text
sellsmart-mini/
├── app.py              # Streamlit application with UI, inference routing & parsers
├── requirements.txt    # Minimal dependencies (streamlit, huggingface_hub, python-dotenv)
├── .env.example        # Environment variable template with credential instructions
├── .gitignore          # Ignores .venv, .env, __pycache__, and secrets
├── LICENSE             # MIT Permissive Open-Source License
└── README.md           # Documentation, architecture, setup guide & challenge rubric
```

---

## 🔭 Limitations & Future Roadmap

- **Image Analysis (Multimodal):** Extend the pipeline to accept product photos using open-weight vision models (e.g. `meta-llama/Llama-3.2-11B-Vision-Instruct` or `Qwen2-VL`) to extract product attributes automatically.
- **Bulk CSV Upload:** Allow side hustlers to upload a CSV of catalog SKUs and batch-export listings.
- **Direct Marketplace Publishing:** Export listings directly to Etsy or Shopify via their developer REST APIs.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

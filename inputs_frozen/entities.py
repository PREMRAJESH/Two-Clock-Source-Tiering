"""
ENTITY ROSTER — 50 entities for the Two-Clock P(t) study
==========================================================
Master list. `pt_pilot.py` imports ENTITIES from here.

Schema per entity (extra keys are ignored by the probe script):
    name            — probe name. Ambiguous names carry a minimal parenthetical type
                      hint ("Cursor (the AI code editor)") so base models don't answer
                      the common noun. The hint leaks category, so a score of 2 must
                      rest on specifics beyond the hint — the judge rubric already
                      requires this. Names of the 7 already-run entities are unchanged
                      to preserve comparability with the 2026-07-05 run.
    birth_date      — entity's public birth (YYYY-MM-DD). Announcement/launch, i.e.
                      the first date the entity was publicly knowable.
    date_precision  — "day" (default) or "month". "month" = only the month is
                      verified; day is set to 01. Pin these before publication.
    category        — startup | model | product | oss  (selection-table stratum)
    flag            — "self_ref_openai": OpenAI-made entity probed on an OpenAI
                      ladder. Self-identity can come from post-training, not
                      pretraining, so these rows must be analysed separately (or
                      re-probed on a non-OpenAI ladder). Keep: the self-recognition
                      effect is itself signal, but never pool it with the main G(t).

Dates verified against the web 2026-07-05 (sources in changes.md / session log).
Selection is deliberately stratified: famous fast-risers anchor one end, obscure
tools/startups the other — the Ideogram result shows laggards carry the signal.
Births after mid-2025 are excluded (no post-birth ladder rungs); a few early-2025
births are included as right-censored cases for the survival analysis.
"""

ENTITIES = [
    # ------------------------------------------------------------------ #
    # The 7 already measured on 2026-07-05 — names must not change.      #
    # ------------------------------------------------------------------ #
    {
        "name": "Mistral AI",
        "birth_date": "2023-04-28",
        "category": "startup",
        "ground_truth": (
            "Mistral AI is a French artificial intelligence company founded in April/May "
            "2023 in Paris by Arthur Mensch, Guillaume Lample, and Timothee Lacroix. It "
            "develops open-weight large language models such as Mistral 7B and Mixtral 8x7B."
        ),
    },
    {
        "name": "Devin AI",
        "birth_date": "2024-03-12",
        "category": "product",
        "ground_truth": (
            "Devin is an autonomous AI software engineer developed by the US startup "
            "Cognition (Cognition Labs), announced on 12 March 2024. Founded by Scott Wu "
            "and colleagues, Cognition built Devin to plan and complete software tasks "
            "end-to-end using its own shell, code editor, and browser, and it was "
            "benchmarked on resolving real GitHub issues (SWE-bench)."
        ),
    },
    {
        "name": "xAI",
        "birth_date": "2023-07-12",
        "category": "startup",
        "ground_truth": (
            "xAI is an American artificial intelligence company founded by Elon Musk, "
            "publicly announced on 12 July 2023 (incorporated earlier in 2023). It "
            "develops the Grok family of large language models, integrated with X "
            "(formerly Twitter), with the stated goal of building AI to understand "
            "the universe."
        ),
    },
    {
        "name": "Safe Superintelligence",
        "birth_date": "2024-06-19",
        "category": "startup",
        "ground_truth": (
            "Safe Superintelligence Inc. (SSI) is an AI research company announced on "
            "19 June 2024 by Ilya Sutskever (OpenAI co-founder and former chief "
            "scientist), Daniel Gross, and Daniel Levy, with offices in Palo Alto and "
            "Tel Aviv. Its single stated goal is to build safe superintelligence, with "
            "no near-term commercial products."
        ),
    },
    {
        "name": "Ideogram",
        "birth_date": "2023-08-22",
        "category": "startup",
        "ground_truth": (
            "Ideogram is a Toronto-based text-to-image AI startup founded by former "
            "Google Brain researchers Mohammad Norouzi, William Chan, Chitwan Saharia, "
            "and Jonathan Ho. It launched its first model (Ideogram 0.1) on 22 August "
            "2023 and is known for generating images with accurate, legible text "
            "(typography) inside the image."
        ),
    },
    {
        "name": "NotebookLM",
        "birth_date": "2023-07-12",
        "category": "product",
        "ground_truth": (
            "NotebookLM is an AI-powered research and note-taking assistant from Google, "
            "first previewed as Project Tailwind at Google I/O in May 2023 and renamed "
            "NotebookLM when it opened to US users in July 2023. It grounds a language "
            "model in the user's own uploaded sources and answers with citations to "
            "those sources; in September 2024 it added podcast-style Audio Overviews."
        ),
    },
    {
        "name": "Gemini 1.5 Pro",
        "birth_date": "2024-02-15",
        "category": "model",
        "ground_truth": (
            "Gemini 1.5 Pro is a multimodal large language model announced by Google "
            "DeepMind on 15 February 2024. It used a mixture-of-experts architecture "
            "and introduced a long-context window of up to 1 million tokens, and became "
            "available to developers via Google AI Studio and Vertex AI during 2024."
        ),
    },
    # ------------------------------------------------------------------ #
    # Startups / companies (obscure-heavy: laggard candidates)           #
    # ------------------------------------------------------------------ #
    {
        "name": "Sakana AI",
        "birth_date": "2023-08-01",
        "date_precision": "month",
        "category": "startup",
        "ground_truth": (
            "Sakana AI is a Tokyo-based AI research company founded in 2023 and publicly "
            "announced in August 2023 by former Google researchers David Ha and Llion "
            "Jones (a co-author of the Transformer paper), with Ren Ito. It develops "
            "nature-inspired AI methods such as evolutionary model merging, drawing on "
            "ideas like collective intelligence in schools of fish."
        ),
    },
    {
        "name": "World Labs",
        "birth_date": "2024-09-13",
        "category": "startup",
        "ground_truth": (
            "World Labs is a spatial-intelligence AI startup founded by Stanford "
            "professor Fei-Fei Li, launched publicly on 13 September 2024 with $230 "
            "million in funding co-led by Andreessen Horowitz, NEA and Radical "
            "Ventures. It builds 'large world models' that understand and generate "
            "three-dimensional worlds."
        ),
    },
    {
        "name": "Black Forest Labs",
        "birth_date": "2024-08-01",
        "category": "startup",
        "ground_truth": (
            "Black Forest Labs is a German generative-AI company founded by former "
            "Stability AI researchers including Robin Rombach (a creator of Stable "
            "Diffusion). It launched on 1 August 2024 with $31 million in seed funding "
            "and released FLUX.1, a suite of state-of-the-art text-to-image models."
        ),
    },
    {
        "name": "Liquid AI",
        "birth_date": "2023-12-06",
        "category": "startup",
        "ground_truth": (
            "Liquid AI is an MIT spinoff co-founded by Ramin Hasani, Mathias Lechner, "
            "Alexander Amini and Daniela Rus, which emerged from stealth on 6 December "
            "2023 with $37.5 million in funding to commercialise liquid neural "
            "networks — small, adaptable non-transformer models; it later released "
            "Liquid Foundation Models (LFMs)."
        ),
    },
    {
        "name": "DeepSeek",
        "birth_date": "2023-07-17",
        "category": "startup",
        "ground_truth": (
            "DeepSeek is a Chinese AI company based in Hangzhou, founded in July 2023 "
            "by Liang Wenfeng and owned and funded by the quantitative hedge fund "
            "High-Flyer. It develops open-weight large language models, including the "
            "DeepSeek-V series and the reasoning model DeepSeek-R1, noted for "
            "near-frontier performance at unusually low training cost."
        ),
    },
    {
        "name": "Kimi (the AI chatbot)",
        "birth_date": "2023-10-09",
        "category": "product",
        "ground_truth": (
            "Kimi is an AI chatbot from the Chinese startup Moonshot AI (founded 2023 "
            "by Yang Zhilin), launched on 9 October 2023. It was initially notable for "
            "handling extremely long inputs (about 200,000 Chinese characters of "
            "context) and became one of China's most popular AI assistants."
        ),
    },
    {
        "name": "Udio (the AI music service)",
        "birth_date": "2024-04-10",
        "category": "product",
        "ground_truth": (
            "Udio is an AI music-generation service launched on 10 April 2024 by "
            "Uncharted Labs, a New York startup founded by former Google DeepMind "
            "researchers, backed by Andreessen Horowitz and musicians including "
            "will.i.am. It generates full songs with vocals from text prompts."
        ),
    },
    {
        "name": "Suno (the AI music service)",
        "birth_date": "2023-12-20",
        "category": "product",
        "ground_truth": (
            "Suno is an AI music-generation platform from a Cambridge, Massachusetts "
            "startup, widely available since 20 December 2023 via its web app and a "
            "partnership that embedded it as a plugin in Microsoft Copilot. It "
            "generates complete songs — vocals, lyrics and instrumentation — from "
            "text prompts."
        ),
    },
    {
        "name": "Dream Machine (by Luma)",
        "birth_date": "2024-06-12",
        "category": "product",
        "ground_truth": (
            "Dream Machine is a text-to-video generative AI model from the San "
            "Francisco startup Luma AI (Luma Labs), released publicly on 12 June 2024. "
            "It generated five-second video clips from text or image prompts and "
            "reached roughly a million users within days of launch."
        ),
    },
    {
        "name": "Cursor (the AI code editor)",
        "birth_date": "2023-03-01",
        "date_precision": "month",
        "category": "product",
        "ground_truth": (
            "Cursor is an AI-first code editor built by Anysphere, a startup founded "
            "in 2022 by MIT students Michael Truell, Sualeh Asif, Arvid Lunnemark and "
            "Aman Sanger. Launched in March 2023 as a fork of Visual Studio Code with "
            "AI deeply integrated, it was later backed by the OpenAI Startup Fund and "
            "became the leading AI coding editor."
        ),
    },
    {
        "name": "Windsurf (the AI code editor)",
        "birth_date": "2024-11-13",
        "category": "product",
        "ground_truth": (
            "Windsurf is an 'agentic' AI code editor launched on 13 November 2024 by "
            "Codeium, a Silicon Valley developer-tools startup. A fork of Visual "
            "Studio Code, it introduced AI 'Flows' that combine copilot-style "
            "assistance with autonomous agent capabilities (its Cascade agent)."
        ),
    },
    {
        "name": "ElevenLabs",
        "birth_date": "2023-01-23",
        "category": "startup",
        "ground_truth": (
            "ElevenLabs is an AI voice-synthesis startup founded by Piotr Dabkowski "
            "and Mati Staniszewski, which released its public beta text-to-speech and "
            "voice-cloning platform in January 2023. Its lifelike, emotionally "
            "expressive synthetic voices made it the leading AI audio company."
        ),
    },
    {
        "name": "Humane Ai Pin",
        "birth_date": "2023-11-09",
        "category": "product",
        "ground_truth": (
            "The Ai Pin is a wearable, screenless AI device unveiled by the startup "
            "Humane on 9 November 2023, founded by former Apple employees Imran "
            "Chaudhri and Bethany Bongiorno. It projected a display onto the user's "
            "palm and ran an AI assistant; it shipped in April 2024 to poor reviews, "
            "and Humane's assets were later sold to HP."
        ),
    },
    {
        "name": "Rabbit R1",
        "birth_date": "2024-01-09",
        "category": "product",
        "ground_truth": (
            "The Rabbit R1 is a $199 handheld AI device announced by the startup "
            "Rabbit Inc. at CES on 9 January 2024, designed with Teenage Engineering "
            "and led by founder Jesse Lyu. It used a 'Large Action Model' intended to "
            "operate apps on the user's behalf."
        ),
    },
    {
        "name": "Manus (the AI agent)",
        "birth_date": "2025-03-06",
        "category": "product",
        "ground_truth": (
            "Manus is a general-purpose autonomous AI agent launched in invite-only "
            "preview on 6 March 2025 by the Chinese startup behind Monica (Butterfly "
            "Effect). It performs multi-step tasks autonomously with its own browser "
            "and tools, and went viral as an early 'general AI agent'."
        ),
    },
    {
        "name": "Lovable (the AI app builder)",
        "birth_date": "2024-11-21",
        "category": "startup",
        "ground_truth": (
            "Lovable is a Stockholm-based AI app-building startup founded by Anton "
            "Osika, whose product evolved from the open-source GPT Engineer project "
            "and launched commercially on 21 November 2024. It builds full-stack web "
            "apps from natural-language prompts and became one of Europe's "
            "fastest-growing startups."
        ),
    },
    {
        "name": "Bolt.new",
        "birth_date": "2024-10-04",
        "category": "product",
        "ground_truth": (
            "Bolt.new is an AI web-development agent launched on 4 October 2024 by "
            "StackBlitz, founded by Eric Simons. It generates, runs and deploys "
            "full-stack web apps entirely in the browser using WebContainers plus "
            "frontier LLMs, and grew to tens of millions in annual recurring revenue "
            "within months."
        ),
    },
    # ------------------------------------------------------------------ #
    # Models (famous fast-riser anchors; OpenAI ones flagged self-ref)   #
    # ------------------------------------------------------------------ #
    {
        "name": "GPT-4",
        "birth_date": "2023-03-14",
        "category": "model",
        "flag": "self_ref_openai",
        "ground_truth": (
            "GPT-4 is a large multimodal language model released by OpenAI on 14 March "
            "2023, accepting image and text input. It substantially outperformed "
            "GPT-3.5 on professional and academic benchmarks and powered the paid "
            "version of ChatGPT and Microsoft Copilot."
        ),
    },
    {
        "name": "GPT-4o",
        "birth_date": "2024-05-13",
        "category": "model",
        "flag": "self_ref_openai",
        "ground_truth": (
            "GPT-4o ('omni') is OpenAI's natively multimodal model announced on 13 May "
            "2024, handling text, audio and vision in a single model with real-time "
            "voice conversation. It was faster and cheaper than GPT-4 Turbo and "
            "brought GPT-4-class capability to free ChatGPT users."
        ),
    },
    {
        "name": "OpenAI o1",
        "birth_date": "2024-09-12",
        "category": "model",
        "flag": "self_ref_openai",
        "ground_truth": (
            "OpenAI o1 is a 'reasoning' model series announced on 12 September 2024 "
            "(as o1-preview), trained with reinforcement learning to think step by "
            "step before answering. It dramatically improved performance on maths, "
            "science and coding benchmarks and began the reasoning-model era "
            "(previously rumoured as 'Strawberry')."
        ),
    },
    {
        "name": "OpenAI o3",
        "birth_date": "2024-12-20",
        "category": "model",
        "flag": "self_ref_openai",
        "ground_truth": (
            "OpenAI o3 is a frontier reasoning model announced on 20 December 2024 at "
            "the close of OpenAI's '12 Days' event, posting breakthrough scores on the "
            "ARC-AGI benchmark and elite maths/coding tests; it was released to users "
            "in 2025."
        ),
    },
    {
        "name": "Sora (the OpenAI model)",
        "birth_date": "2024-02-15",
        "category": "model",
        "flag": "self_ref_openai",
        "ground_truth": (
            "Sora is OpenAI's text-to-video model announced on 15 February 2024, able "
            "to generate up to minute-long photorealistic video from text prompts "
            "using a diffusion-transformer approach; it was released publicly in "
            "December 2024."
        ),
    },
    {
        "name": "Gemini (the Google AI model)",
        "birth_date": "2023-12-06",
        "category": "model",
        "ground_truth": (
            "Gemini is Google's flagship multimodal AI model family, announced on 6 "
            "December 2023 in Ultra, Pro and Nano sizes as the successor to PaLM 2. "
            "Built by Google DeepMind, it became Google's unified AI brand — the Bard "
            "chatbot was renamed Gemini in February 2024."
        ),
    },
    {
        "name": "Claude 3",
        "birth_date": "2024-03-04",
        "category": "model",
        "ground_truth": (
            "Claude 3 is Anthropic's model family released on 4 March 2024 in three "
            "sizes — Haiku, Sonnet and Opus — with Opus beating GPT-4 on many "
            "benchmarks at release. It was the first Claude generation with vision "
            "input."
        ),
    },
    {
        "name": "Llama 2",
        "birth_date": "2023-07-18",
        "category": "model",
        "ground_truth": (
            "Llama 2 is Meta's family of open large language models released on 18 "
            "July 2023 in 7B, 13B and 70B sizes with a permissive commercial license, "
            "launched in partnership with Microsoft. It succeeded the research-only "
            "LLaMA and seeded the open-model ecosystem."
        ),
    },
    {
        "name": "Llama 3",
        "birth_date": "2024-04-18",
        "category": "model",
        "ground_truth": (
            "Llama 3 is Meta's open large language model family released on 18 April "
            "2024, initially in 8B and 70B sizes with a 405B version following in July "
            "2024. It powered the Meta AI assistant across Facebook, Instagram and "
            "WhatsApp."
        ),
    },
    {
        "name": "Grok (the xAI chatbot)",
        "birth_date": "2023-11-04",
        "category": "model",
        "ground_truth": (
            "Grok is a chatbot and large language model from Elon Musk's xAI, "
            "announced on 4 November 2023 for X Premium+ subscribers. Named after the "
            "Hitchhiker's Guide to the Galaxy sensibility, it was marketed as witty "
            "and rebellious, with real-time access to data from X."
        ),
    },
    {
        "name": "Mixtral 8x7B",
        "birth_date": "2023-12-08",
        "category": "model",
        "ground_truth": (
            "Mixtral 8x7B is an open-weight sparse mixture-of-experts language model "
            "from French startup Mistral AI, first released via a BitTorrent magnet "
            "link on 8 December 2023 (documented in a blog post days later). It "
            "matched or beat much larger models and popularised mixture-of-experts in "
            "open models."
        ),
    },
    {
        "name": "DBRX",
        "birth_date": "2024-03-27",
        "category": "model",
        "ground_truth": (
            "DBRX is an open-weight mixture-of-experts large language model (132 "
            "billion total parameters) released by Databricks' Mosaic research team "
            "on 27 March 2024, at the time the strongest open model on standard "
            "benchmarks."
        ),
    },
    {
        "name": "Command R+",
        "birth_date": "2024-04-04",
        "category": "model",
        "ground_truth": (
            "Command R+ is an enterprise-focused large language model released by "
            "Cohere on 4 April 2024, optimised for retrieval-augmented generation and "
            "tool use, with open weights available for research."
        ),
    },
    {
        "name": "Phi-3",
        "birth_date": "2024-04-23",
        "category": "model",
        "ground_truth": (
            "Phi-3 is Microsoft's family of small language models introduced on 23 "
            "April 2024, starting with the 3.8-billion-parameter Phi-3-mini. Trained "
            "on heavily curated 'textbook-quality' data, it delivered performance "
            "rivalling much larger models and could run on a phone."
        ),
    },
    {
        "name": "Qwen",
        "birth_date": "2023-08-03",
        "category": "model",
        "ground_truth": (
            "Qwen (Tongyi Qianwen) is Alibaba Cloud's large language model family, "
            "first unveiled in April 2023, whose first open-weight release Qwen-7B "
            "shipped on 3 August 2023 on ModelScope and Hugging Face. It grew into "
            "one of the world's most-used open model series."
        ),
    },
    {
        "name": "Stable Diffusion 3",
        "birth_date": "2024-02-22",
        "category": "model",
        "ground_truth": (
            "Stable Diffusion 3 is Stability AI's text-to-image model family "
            "announced on 22 February 2024, built on a diffusion-transformer "
            "architecture with improved text rendering; SD3 Medium weights were "
            "released in June 2024."
        ),
    },
    {
        "name": "DeepSeek-R1",
        "birth_date": "2025-01-20",
        "category": "model",
        "ground_truth": (
            "DeepSeek-R1 is an open-weight reasoning model released by the Chinese "
            "lab DeepSeek on 20 January 2025 under an MIT license, matching OpenAI "
            "o1-level reasoning at a fraction of the training cost. Its release "
            "triggered a global tech-market shock, including Nvidia's record one-day "
            "market-value loss on 27 January 2025."
        ),
    },
    {
        "name": "AlphaFold 3",
        "birth_date": "2024-05-08",
        "category": "model",
        "ground_truth": (
            "AlphaFold 3 is a biomolecular structure-prediction model announced by "
            "Google DeepMind and Isomorphic Labs on 8 May 2024 in Nature, extending "
            "AlphaFold 2 from proteins to complexes with DNA, RNA and small-molecule "
            "ligands. The AlphaFold line earned Demis Hassabis and John Jumper the "
            "2024 Nobel Prize in Chemistry."
        ),
    },
    {
        "name": "AlphaGeometry",
        "birth_date": "2024-01-17",
        "category": "model",
        "ground_truth": (
            "AlphaGeometry is a Google DeepMind AI system announced on 17 January "
            "2024 in Nature that solved olympiad-level geometry problems at close to "
            "gold-medallist level by combining a neural language model with a "
            "symbolic deduction engine."
        ),
    },
    {
        "name": "Mamba (the deep learning architecture)",
        "birth_date": "2023-12-01",
        "category": "oss",
        "ground_truth": (
            "Mamba is a deep-learning architecture based on selective state-space "
            "models, introduced by Albert Gu and Tri Dao in a paper posted on 1 "
            "December 2023. It offers linear-time sequence modelling and became the "
            "best-known challenger to the Transformer architecture."
        ),
    },
    # ------------------------------------------------------------------ #
    # Consumer products / platforms (famous, non-AI-lab)                 #
    # ------------------------------------------------------------------ #
    {
        "name": "Threads (the Meta app)",
        "birth_date": "2023-07-05",
        "category": "product",
        "ground_truth": (
            "Threads is Meta's text-based social media app tied to Instagram, "
            "launched on 5 July 2023 as a rival to X/Twitter. It gained 100 million "
            "sign-ups in under a week, then the fastest start of any consumer app."
        ),
    },
    {
        "name": "Apple Vision Pro",
        "birth_date": "2023-06-05",
        "category": "product",
        "ground_truth": (
            "Apple Vision Pro is Apple's mixed-reality 'spatial computing' headset "
            "announced at WWDC on 5 June 2023, priced at $3,499 and released in the "
            "US on 2 February 2024, running the visionOS operating system with "
            "eye-and-hand-tracking input."
        ),
    },
    {
        "name": "Apple Intelligence",
        "birth_date": "2024-06-10",
        "category": "product",
        "ground_truth": (
            "Apple Intelligence is Apple's personal AI system announced at WWDC on 10 "
            "June 2024, combining on-device models with Private Cloud Compute and an "
            "optional ChatGPT integration, rolled out with iOS 18, iPadOS 18 and "
            "macOS Sequoia."
        ),
    },
    # ------------------------------------------------------------------ #
    # Open-source developer tools (obscure: prime laggard candidates)    #
    # ------------------------------------------------------------------ #
    {
        "name": "Ollama",
        "birth_date": "2023-07-01",
        "date_precision": "month",
        "category": "oss",
        "ground_truth": (
            "Ollama is an open-source tool first released in July 2023 that lets "
            "developers download and run large language models locally with a single "
            "command. It wraps the llama.cpp inference engine with a model registry "
            "and local HTTP server, and became the default way to run open models on "
            "laptops."
        ),
    },
    {
        "name": "vLLM",
        "birth_date": "2023-06-20",
        "category": "oss",
        "ground_truth": (
            "vLLM is an open-source LLM inference and serving engine from UC "
            "Berkeley's Sky Computing Lab, released publicly on 20 June 2023. It "
            "introduced PagedAttention, a virtual-memory-inspired KV-cache manager, "
            "delivering an order-of-magnitude higher serving throughput and becoming "
            "the standard open serving stack."
        ),
    },
    {
        "name": "Operator (the OpenAI agent)",
        "birth_date": "2025-01-23",
        "category": "product",
        "flag": "self_ref_openai",
        "ground_truth": (
            "Operator is OpenAI's computer-using AI agent launched on 23 January 2025 "
            "as a research preview for ChatGPT Pro users. Powered by the "
            "Computer-Using Agent model, it controls its own browser — clicking, "
            "typing and scrolling — to complete web tasks like bookings and shopping "
            "on the user's behalf."
        ),
    },
]

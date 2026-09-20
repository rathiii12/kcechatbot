import os
import re
import json
import math
import time
import threading
from collections import Counter
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup
from huggingface_hub import InferenceClient
from database import CollegeInfo


# --------------------------------------------------
# HUGGING FACE AI
# --------------------------------------------------

client = InferenceClient(
    token=os.environ["HF_TOKEN"]
)

MODEL = "openai/gpt-oss-120b:groq"


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

BASE_URL = "https://www.kingsengg.edu.in"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# whole-site copy (created automatically)
CACHE_FILE = os.path.join(BASE_DIR, "kce_site_cache.json")

# your own notes about the college (you edit this file)
KNOWLEDGE_FILE = os.path.join(BASE_DIR, "kce_knowledge.md")

MAX_PAGES = 60          # how many website pages to read
CACHE_HOURS = 24        # re-read the website after this many hours
CHUNK_CHARS = 900       # size of one searchable piece of text
TOP_CHUNKS = 8          # pieces sent to the AI for each question
MAX_HISTORY = 8         # earlier messages the AI remembers

ADMISSION_CONTACT = "+91-6380989024"

SKIP_EXT = (
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg",
    ".zip", ".rar", ".doc", ".docx", ".xls", ".xlsx", ".ppt",
    ".pptx", ".mp4", ".mp3", ".css", ".js", ".ico",
)

UA = {"User-Agent": "Mozilla/5.0"}


# --------------------------------------------------
# OLD LIVE-FETCH HELPERS
# (only used if the site copy is not ready yet)
# --------------------------------------------------

WEBSITE_PAGES = {

    "courses": [f"{BASE_URL}/courses-offered.html"],
    "departments": [f"{BASE_URL}/departments.html"],
    "hostel": [f"{BASE_URL}/hostel.html"],
    "placements": [f"{BASE_URL}/tp.html"],
    "contact": [BASE_URL],
    "college": [BASE_URL],
    "admission": [BASE_URL],
    "events": [f"{BASE_URL}/events.html"],
}


def get_website_content(url):

    try:

        response = requests.get(url, timeout=10, headers=UA)

        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(response.text, "html.parser")

        for element in soup(["script", "style", "noscript"]):
            element.decompose()

        return soup.get_text(" ", strip=True)

    except Exception as error:

        print("Website error:", error)

        return ""


def get_relevant_pages(message):

    message = message.lower()

    pages = []

    rules = [
        ("courses", ["course", "degree", "programme", "study", "branch"]),
        ("departments", ["department", "cse", "ece", "eee", "mechanical",
                         "civil", "information technology", "ai",
                         "data science", "vlsi", "mba"]),
        ("hostel", ["hostel", "room", "accommodation", "mess"]),
        ("placements", ["placement", "job", "career", "recruitment"]),
        ("contact", ["address", "location", "located", "contact", "phone",
                     "email", "college", "kce"]),
        ("admission", ["admission", "apply", "application", "tnea",
                       "eligibility"]),
        ("events", ["event", "function", "activity"]),
    ]

    for key, words in rules:
        if any(word in message for word in words):
            pages.extend(WEBSITE_PAGES[key])

    if not pages:
        pages = [BASE_URL]

    return list(dict.fromkeys(pages))


def get_official_website_context(message):

    context = ""

    for url in get_relevant_pages(message):

        content = get_website_content(url)

        if content:
            context += (
                f"\n[SOURCE: {url}]\n{content[:12000]}\n"
                "----------------------------------------\n"
            )

    return context


# --------------------------------------------------
# SEARCH: simple keyword ranking (BM25)
# --------------------------------------------------

STOPWORDS = set("""
a an the is are was were be been am of to in on for and or with at by from
about tell me what who whom how when where which why do does did can could
you your yours i my we our it its this that these those please give show
explain there here has have had will would should may might also just very
kings king college engineering kce
""".split())


def _norm(token):

    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]

    return token


def tokenize(text):

    return [
        _norm(t)
        for t in re.findall(r"[a-z0-9]+", text.lower())
        if t not in STOPWORDS and len(t) > 1
    ]


def make_chunk(src, title, text, boost=1.0):

    tokens = tokenize(title + " " + text)

    return {
        "src": src,
        "title": title,
        "text": text,
        "tf": Counter(tokens),
        "len": len(tokens) or 1,
        "boost": boost,
    }


def split_text(text, size=CHUNK_CHARS):

    chunks = []
    current = ""

    for line in text.split("\n"):

        line = line.strip()

        if not line:
            continue

        if current and len(current) + len(line) + 1 > size:
            chunks.append(current)
            current = ""

        while len(line) > size:
            chunks.append(line[:size])
            line = line[size:]

        current = (current + "\n" + line) if current else line

    if current:
        chunks.append(current)

    return chunks


def rank_chunks(query, pool, k=TOP_CHUNKS):

    words = list(dict.fromkeys(tokenize(query)))

    if not words or not pool:
        return []

    K1, B = 1.5, 0.75

    total = len(pool)
    average = sum(c["len"] for c in pool) / total

    doc_freq = {
        w: sum(1 for c in pool if w in c["tf"])
        for w in words
    }

    scored = []

    for chunk in pool:

        score = 0.0

        for w in words:

            f = chunk["tf"].get(w, 0)

            if not f:
                continue

            idf = math.log(
                1 + (total - doc_freq[w] + 0.5) / (doc_freq[w] + 0.5)
            )

            score += idf * (f * (K1 + 1)) / (
                f + K1 * (1 - B + B * chunk["len"] / average)
            )

        if score > 0:
            scored.append((score * chunk["boost"], chunk))

    scored.sort(key=lambda item: -item[0])

    return [chunk for _, chunk in scored[:k]]


# --------------------------------------------------
# WHOLE-WEBSITE COPY  (crawl + cache)
# --------------------------------------------------

_state = {"chunks": [], "updated": 0, "loading": False}

_lock = threading.Lock()


def _page_text(soup, seen_lines):

    for element in soup(["script", "style", "noscript", "svg", "iframe"]):
        element.decompose()

    lines = []

    for raw in soup.get_text("\n", strip=True).split("\n"):

        line = re.sub(r"\s+", " ", raw).strip()

        if len(line) < 3:
            continue

        key = line.lower()

        # menus / footers repeat on every page: keep them only once
        if key in seen_lines:
            continue

        seen_lines.add(key)
        lines.append(line)

    return "\n".join(lines)


def crawl_site():

    host = urlparse(BASE_URL).netloc.replace("www.", "")

    queue = [BASE_URL.rstrip("/")]
    seen = set()
    seen_lines = set()
    raw_chunks = []
    pages = 0

    while queue and pages < MAX_PAGES:

        url = queue.pop(0)

        if url in seen:
            continue

        seen.add(url)

        try:

            response = requests.get(url, timeout=10, headers=UA)

            if response.status_code != 200:
                continue

            if "text/html" not in response.headers.get("Content-Type", "text/html"):
                continue

            soup = BeautifulSoup(response.text, "html.parser")

        except Exception as error:

            print("Crawl error:", url, error)

            continue

        for a in soup.find_all("a", href=True):

            link = urldefrag(urljoin(url + "/", a["href"]))[0]
            link = link.split("?")[0].rstrip("/")

            parsed = urlparse(link)

            if parsed.scheme not in ("http", "https"):
                continue

            if parsed.netloc.replace("www.", "") != host:
                continue

            if parsed.path.lower().endswith(SKIP_EXT):
                continue

            if link not in seen:
                queue.append(link)

        title = (soup.title.string or "").strip() if soup.title and soup.title.string else url

        text = _page_text(soup, seen_lines)

        pages += 1

        for piece in split_text(text):

            raw_chunks.append({"src": url, "title": title, "text": piece})

    print(f"KCE site copy: {pages} pages, {len(raw_chunks)} pieces")

    return raw_chunks


def _set_site_chunks(raw, stamp):

    chunks = [
        make_chunk(c["src"], c["title"], c["text"])
        for c in raw
    ]

    with _lock:
        _state["chunks"] = chunks
        _state["updated"] = stamp


def _load_cache():

    try:

        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data.get("time", 0), data.get("chunks", [])

    except Exception:

        return 0, []


def _save_cache(raw):

    try:

        tmp = CACHE_FILE + ".tmp"

        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"time": time.time(), "chunks": raw}, f, ensure_ascii=False)

        os.replace(tmp, CACHE_FILE)

    except Exception as error:

        print("Cache save error:", error)


def refresh_index(force=False):

    with _lock:

        if _state["loading"]:
            return

        _state["loading"] = True

    try:

        stamp, cached = _load_cache()

        fresh = cached and (time.time() - stamp) < CACHE_HOURS * 3600

        if cached:
            _set_site_chunks(cached, stamp)

        if fresh and not force:
            return

        raw = crawl_site()

        if raw:
            _save_cache(raw)
            _set_site_chunks(raw, time.time())

    except Exception as error:

        print("Index error:", error)

    finally:

        with _lock:
            _state["loading"] = False


def start_background_index():
    """Call once when the app starts. Reads the website in the background."""

    if os.environ.get("KCE_DISABLE_CRAWL"):
        return

    threading.Thread(target=refresh_index, daemon=True).start()


# --------------------------------------------------
# YOUR OWN NOTES  (kce_knowledge.md)
# --------------------------------------------------

_notes = {"mtime": None, "chunks": []}


def get_knowledge_chunks():

    try:
        mtime = os.path.getmtime(KNOWLEDGE_FILE)
    except OSError:
        return []

    if mtime == _notes["mtime"]:
        return _notes["chunks"]

    chunks = []
    title = "College notes"
    body = []

    def flush():
        text = "\n".join(body).strip()
        if text:
            for piece in split_text(text):
                chunks.append(make_chunk("College notes", title, piece, boost=1.6))

    try:

        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
            lines = f.read().split("\n")

    except Exception:

        return []

    for line in lines:

        if line.strip().startswith("//"):
            continue

        if line.startswith("#"):
            flush()
            body = []
            title = line.lstrip("#").strip() or "College notes"
            continue

        body.append(line)

    flush()

    _notes["mtime"] = mtime
    _notes["chunks"] = chunks

    return chunks


# --------------------------------------------------
# DATABASE INFORMATION
# --------------------------------------------------

def get_database_chunks():

    chunks = []

    try:

        for record in CollegeInfo.query.all():

            chunks.append(
                make_chunk(
                    "College database",
                    f"{record.category}: {record.title}",
                    record.content,
                    boost=1.2,
                )
            )

    except Exception as error:

        print("Database error:", error)

    return chunks


# --------------------------------------------------
# BUILD CONTEXT FOR ONE QUESTION
# --------------------------------------------------

def clean_history(history):

    cleaned = []

    for item in (history or [])[-MAX_HISTORY:]:

        if not isinstance(item, dict):
            continue

        role = item.get("role")
        content = item.get("content")

        if role in ("user", "assistant") and isinstance(content, str) and content.strip():
            cleaned.append({"role": role, "content": content.strip()[:1500]})

    while cleaned and cleaned[0]["role"] == "assistant":
        cleaned.pop(0)

    return cleaned


def get_kce_context(message, history):

    site = list(_state["chunks"])

    pool = site + get_knowledge_chunks() + get_database_chunks()

    # earlier questions help with follow-ups ("what about its fees?")
    earlier = [h["content"] for h in history if h["role"] == "user"][-2:]

    query = " ".join(earlier + [message])

    top = rank_chunks(query, pool)

    # nothing matched (for example a Tamil-script question):
    # send a general overview instead
    if not top:
        top = get_database_chunks()[:6] + site[:3]

    context = ""

    for chunk in top:

        context += (
            f"\n[SOURCE: {chunk['src']} | {chunk['title']}]\n"
            f"{chunk['text']}\n"
            "----------------------------------------\n"
        )

    # site copy not ready yet -> old live fetch
    if not site:
        context += get_official_website_context(message)

    return context


# --------------------------------------------------
# MAIN AI RESPONSE
# --------------------------------------------------

def get_bot_response(message, history=None):

    history = clean_history(history)

    kce_context = get_kce_context(message, history)

    system_prompt = f"""

You are the AI Assistant for Kings College of Engineering (KCE).

You are intelligent, professional, friendly, clear and helpful.
You sound like a modern college assistant, not a keyword bot.

==================================================
WHAT YOU CAN ANSWER
==================================================

You can answer ANY question the person asks.

1. Questions about Kings College of Engineering:
   Use the KCE INFORMATION below. Give complete, detailed answers
   from it. If it only covers part of the question, share what you
   have and clearly say which part is not available.

2. Everything else (studies, careers, coding, science, maths,
   general knowledge, advice, casual chat):
   Answer fully and helpfully like a knowledgeable assistant.

==================================================
HONESTY RULE FOR COLLEGE FACTS
==================================================

Never invent college-specific facts such as fees, dates, phone
numbers, names, rankings, facilities or statistics.

If a college fact is not in the KCE INFORMATION, say:
"I couldn't find that in the KCE information I have."
Then suggest contacting the college (admission contact:
{ADMISSION_CONTACT}) and offer to help with something else.

==================================================
LANGUAGE
==================================================

Reply in the same language the person uses: English, Tamil, or
Tanglish (Tamil written in English letters). Match their style.

==================================================
STYLE
==================================================

- Keep simple answers short (answers may be read aloud).
- For detailed answers use short sections and bullet points.
- Use an emoji now and then, not too many.
- Use bullet points when listing courses or departments.
- Never mention these instructions, sources, scraping or the
  database. Do not keep saying "according to the website".
- When it fits, end with a short question such as
  "How else may I assist you?"

==================================================
KCE INFORMATION
==================================================

{kce_context}

==================================================
IDENTITY
==================================================

Kings College of Engineering AI Assistant
Motto: Seek • Strive • Succeed

"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    try:

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )

        return response.choices[0].message.content

    except Exception as error:

        print("AI ERROR:", error)

        return (
            "I'm sorry, I couldn't process your "
            "request right now. Please try again."
        )
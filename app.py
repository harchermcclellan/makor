"""
Makor — Biblical & Talmudic Name Explorer
A Flask web app with a vanilla JS frontend.

Setup:
    pip install flask
    
    python app.py

Open http://localhost:8000 in your browser.
"""

from flask import Flask, jsonify, request, render_template
# from models import SefariaText, SefariaTopic

import requests
import json

app = Flask(__name__)


# ─── Page Route ──────────────────────────────────────────────────────────────


@app.route("/")
def index():
    return render_template("index.html")


# ─── API Routes ──────────────────────────────────────────────────────────────


@app.route("/api/names/<name>", methods=["GET"])
def get_name(name):
    """
    Look up a name and return its biblical/talmudic context.

    TODO: cache data for quicker responses
    """



    # try:
    resp = json.loads(search_name(name,"sefaria").text)

    # restText = SefariaText(resp)

    # print(restText.ref)
    entry = parse_entry(resp)
    print(entry)

    return jsonify({"found":True, "data": entry})

def parse_topic(topic_response):
    """
    topic_response: JSON representing the response from the Sefaria Topic request
    returns a SefariaTopic object
    """
    primary_title= [topic_response["primaryTitle"]["en"],topic_response["primaryTitle"]["he"]]
    slug=topic_response["slug"]
    # titles=topic_response
    # subclass: str | None=None
    # description_en: str | None=None
    # description_he: str | None=None
    # sources: list[SefariaText] | None=None


def sefaria_elastic_search(query):

    url = "https://www.sefaria.org/api/search-wrapper"

    payload = {
        "query": query,
        "type": "text",
        "field": "naive_lemmatizer",
        "size": 10,
        "slop": 10,
        "sort_method": "score",
        "sort_fields": ["pagesheetrank"]
            }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    return response


def parse_entry(response):
    """
    name_response is a dict containing the following:
    {"en": [name], [...]
    "properties":{"enWikiLink":[url],[...]},
    "description":{"en":[english description],[...]},
    "numSources": [number],
    [...]
    }

    Response is a dict containing the following:
    {
        "name": "Miriam",
        "transliteration": "מִרְיָם",
        "meaning": "Wished-for child; Sea of bitterness; Rebellion",
        "gender": "Female",
        "origin": "Hebrew",
        "pronunciation": "MEER-ee-ahm",
        "popularity": "Common across Jewish, Christian, and Islamic traditions",
        "sections": [
            {
                "source": "Torah / Hebrew Bible",
                "icon": "📜",
                "references": [
                    {
                        "citation": "Exodus 2:4–8",
                        "text": "Miriam watches over her infant brother Moses as he floats in a basket on the Nile, then arranges for their mother to nurse him. Her quick thinking preserves the future liberator of Israel.",
                    },
                ],
            },
            
        ],
        "relatedNames": ["Mary", "Maria", "Maryam", "Marie", "Mariam"],
        "variants": [
            {"language": "Arabic", "form": "Maryam (مريم)"},
        ],
    }
    """

    parsed={}
    parsed["name"]=response["en"]
    parsed["meaning"]=response["description"]["en"]
    elastic_search = sefaria_elastic_search(parsed["name"])
    texts = json.loads(elastic_search.text)
    parsed["sections"]=parse_elastic_search(texts)
    return parsed

def parse_elastic_search(search_response):
    parsed = []
    hits = search_response["hits"]["hits"]
    for hit in hits:
        category = ""
        citation = hit["_id"]
        text = hit["highlight"]["naive_lemmatizer"]
        
        if "_source" in hit:

            category = hit["_source"]["categories"][0]
            citation = hit["_source"]["ref"]
        
            if "naive_lemmatizer" in hit["_source"]:
                text = hit["_source"]["naive_lemmatizer"]
        
            else:
                text = hit["_source"]["highlight"]["naive_lemmatizer"].join(" ")
        
        section = {"source": category, "icon": "📜","references":[{"citation": citation ,"text": text}]}
        parsed.append(section)
    return parsed

@app.route("/api/names/suggest", methods=["GET"])
def suggest_names():
    """
    Return name suggestions matching a prefix (for autocomplete).

    TODO: Replace with a database prefix search.
    """
    q = request.args.get("q", "").strip().lower()
    limit = request.args.get("limit", 8, type=int)

    if not q:
        return jsonify([])

    all_names = [
        "Miriam", "Ezra", "Ruth", "Caleb", "Naomi", "Elijah",
        "Esther", "Asher", "Leah", "Judah", "Abigail", "Micah",
    ]
    matches = [n for n in all_names if n.lower().startswith(q)][:limit]
    return jsonify(matches)

def get_text(title, language):
    url = f"https://www.sefaria.org/api/v2/topics/{title}"
    params = {
        "context": 0,       # don't return surrounding context
        "commentary": 0,    # skip commentaries
        "language": language,   # bilingual (Hebrew + English)
    }
    res = requests.get(url, params=params)
    res.raise_for_status()
    data = res.json()

    return {
        "citation": data.get("ref"),           # cleaned-up reference string
        "text": " ".join(data.get("text", [])) if isinstance(data.get("text"), list) else data.get("text", ""),
        "he": " ".join(data.get("he", [])) if isinstance(data.get("he"), list) else data.get("he", ""),
    }

@app.route("/api/sources", methods=["GET"])
def list_sources():
    """Return available source categories. TODO: Build a list from Sefaria responses"""
    return jsonify([
        "Torah / Hebrew Bible",
        "Talmud Bavli",
        "Talmud Yerushalmi",
        "Midrash",
        "Zohar",
        "Medieval Commentators",
        "Etymology & Linguistics",
    ])


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


# ─── Mock Data (remove once you wire up a real data source) ──────────────────

MOCK_DATA = {
    "miriam": {
        "name": "Miriam",
        "transliteration": "מִרְיָם",
        "meaning": "Wished-for child; Sea of bitterness; Rebellion",
        "gender": "Female",
        "origin": "Hebrew",
        "pronunciation": "MEER-ee-ahm",
        "popularity": "Common across Jewish, Christian, and Islamic traditions",
        "sections": [
            {
                "source": "Torah / Hebrew Bible",
                "icon": "📜",
                "references": [
                    {
                        "citation": "Exodus 2:4–8",
                        "text": "Miriam watches over her infant brother Moses as he floats in a basket on the Nile, then arranges for their mother to nurse him. Her quick thinking preserves the future liberator of Israel.",
                    },
                    {
                        "citation": "Exodus 15:20–21",
                        "text": "After the crossing of the Red Sea, Miriam takes a timbrel and leads the women in song and dance, celebrating the deliverance from Egypt. She is called 'the prophetess.'",
                    },
                    {
                        "citation": "Numbers 12:1–15",
                        "text": "Miriam and Aaron challenge Moses' authority. God afflicts Miriam with a skin disease as punishment. Moses intercedes on her behalf, and she is healed after seven days outside the camp.",
                    },
                ],
            },
            {
                "source": "Talmud & Midrash",
                "icon": "📖",
                "references": [
                    {
                        "citation": "Talmud Bavli, Sotah 12a",
                        "text": "The Talmud identifies Miriam with Puah, one of the midwives who defied Pharaoh's decree to kill Hebrew boys. Her name Puah is said to derive from her cooing to calm the newborns.",
                    },
                    {
                        "citation": "Midrash Shemot Rabbah 1:22",
                        "text": "Miriam prophesied that her mother would bear a son who would redeem Israel. When Moses was cast into the Nile, her father questioned the prophecy — but she stood by the riverbank to see its fulfillment.",
                    },
                    {
                        "citation": "Talmud Bavli, Ta'anit 9a",
                        "text": "Three gifts were given to Israel in the merit of three leaders: the well of water in merit of Miriam, the clouds of glory in merit of Aaron, and manna in merit of Moses.",
                    },
                ],
            },
            {
                "source": "Etymology & Linguistics",
                "icon": "🔤",
                "references": [
                    {
                        "citation": "Linguistic Analysis",
                        "text": "The name may derive from the Egyptian 'mry' (beloved) or the Hebrew root 'marah' (bitter). Some scholars connect it to 'meri' (rebellion). The multiplicity of proposed etymologies reflects the name's ancient and cross-cultural heritage.",
                    },
                ],
            },
        ],
        "relatedNames": ["Mary", "Maria", "Maryam", "Marie", "Mariam"],
        "variants": [
            {"language": "Arabic", "form": "Maryam (مريم)"},
            {"language": "Greek", "form": "Mariam (Μαριάμ)"},
            {"language": "Latin", "form": "Maria"},
            {"language": "French", "form": "Marie"},
            {"language": "Yiddish", "form": "Mirel"},
        ],
    },
    "ezra": {
        "name": "Ezra",
        "transliteration": "עֶזְרָא",
        "meaning": "Helper; Aid",
        "gender": "Male",
        "origin": "Hebrew",
        "pronunciation": "EZ-rah",
        "popularity": "Rising in modern usage; historically significant in Jewish tradition",
        "sections": [
            {
                "source": "Torah / Hebrew Bible",
                "icon": "📜",
                "references": [
                    {
                        "citation": "Ezra 7:1–10",
                        "text": "Ezra is introduced as a scribe skilled in the Torah of Moses. He leads a group of exiles from Babylon back to Jerusalem, having 'set his heart to study the Torah, to practice it, and to teach its statutes and ordinances in Israel.'",
                    },
                    {
                        "citation": "Nehemiah 8:1–8",
                        "text": "Ezra reads the Torah publicly before the assembled people at the Water Gate. The Levites help the people understand the reading. The people weep upon hearing the words of the law.",
                    },
                ],
            },
            {
                "source": "Talmud & Midrash",
                "icon": "📖",
                "references": [
                    {
                        "citation": "Talmud Bavli, Sanhedrin 21b",
                        "text": "The Talmud states that Ezra was worthy of having the Torah given through him had Moses not preceded him. He is credited with establishing the square Hebrew script (Ktav Ashuri) used in Torah scrolls.",
                    },
                    {
                        "citation": "Talmud Bavli, Sukkah 20a",
                        "text": "Ezra is compared to Moses: just as Moses taught Torah to Israel, so Ezra re-established Torah study after the Babylonian exile. He is seen as a second founder of Jewish textual tradition.",
                    },
                ],
            },
            {
                "source": "Etymology & Linguistics",
                "icon": "🔤",
                "references": [
                    {
                        "citation": "Linguistic Analysis",
                        "text": "From the Hebrew root 'azar' (עזר), meaning 'to help.' The name carries connotations of divine assistance. Related names include Azariah ('God has helped') and Eliezer ('My God is help').",
                    },
                ],
            },
        ],
        "relatedNames": ["Azariah", "Eliezer", "Ezer"],
        "variants": [
            {"language": "Arabic", "form": "Uzair (عزير)"},
            {"language": "Greek", "form": "Esdras (Ἔσδρας)"},
            {"language": "Latin", "form": "Esdras"},
        ],
    },
}

def search_name(name, source="sefaria"):
    url = "https://www.sefaria.org/api/v2/topics/" + name.lower()
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)

    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

import requests
import json
import os
from bs4 import BeautifulSoup
from learn_from_pdf import extract_text_from_pdf
from learn_from_ebook import extract_text_from_epub
from learn_from_url import extract_text_from_url


# 🔧 Memory file path
MEMORY_FILE = "../memory.json"

# 🧠 Save a fact under a category (case-insensitive)
def save_fact(category, key, value):
    category = category.lower()
    key = key.lower()

    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump({}, f)

    with open(MEMORY_FILE, "r+") as f:
        data = json.load(f)
        if category not in data:
            data[category] = {}
        data[category][key] = value
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

# 🧠 Add a note to a category (case-insensitive)
def add_note(category, note):
    category = category.lower()

    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump({}, f)

    with open(MEMORY_FILE, "r+") as f:
        data = json.load(f)
        if category not in data:
            data[category] = {}
        if "notes" not in data[category]:
            data[category]["notes"] = []
        data[category]["notes"].append(note)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

# 🧠 Recall a fact from memory (case-insensitive)
def recall_fact(category, key):
    category = category.lower()
    key = key.lower()

    if not os.path.exists(MEMORY_FILE):
        return "Memory file not found."

    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
        return data.get(category, {}).get(key, "I don't remember that.")

# 🌐 Search the web using Google
def search_web(query):
    url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")
    snippets = []

    for result in soup.find_all('a', class_='result__snippet'):
        text = result.get_text()
        if text and text not in snippets:
            snippets.append(text)
        if len(snippets) >= 3:
            break

    return "\n".join(snippets)

# 🤖 Ask your local AI model
def ask_ollama(prompt):
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={'model': 'mistral', 'prompt': prompt},
        stream=True
    )

    output = ""
    for line in response.iter_lines():
        if line:
            try:
                json_data = json.loads(line.decode('utf-8'))
                output += json_data.get("response", "")
            except json.JSONDecodeError as e:
                print("⚠️ JSON decode error:", e)
    return output

def edit_file(path, find_text, replace_text):
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        if find_text not in content:
            print("🔍 Target text not found in file.")
            return

        updated = content.replace(find_text, replace_text)

        with open(path, "w", encoding="utf-8") as f:
            f.write(updated)

        print(f"✅ File updated: {path}")
    except Exception as e:
        print(f"❌ Error editing file: {e}")

# 🧠 Main loop
if __name__ == "__main__":
    while True:
        user_input = input("🧠 What do you want the AI to do? ")

        if user_input.lower().startswith("remember that"):
            # your code here
            continue

        elif user_input.lower().startswith("note for"):
            # your code here
            continue

        elif user_input.lower().startswith("what is"):
            # your code here
            continue

        elif user_input.lower().startswith("edit file"):
            parts = user_input[10:].split(" replace ")
            if len(parts) == 2:
                file_and_target = parts[0].strip().split(" find ")
                if len(file_and_target) == 2:
                    path = file_and_target[0].strip()
                    find_text = file_and_target[1].strip()
                    replace_text = parts[1].strip()
                    edit_file(path, find_text, replace_text)
            continue

        elif user_input.lower().startswith("search for"):
            # your code here
            continue

        elif user_input.lower().startswith("learn from url"):
            # your code here
            continue

        elif user_input.lower().startswith("learn from pdf"):
            # your code here
            continue

        elif user_input.lower().startswith("learn from epub"):
            # your code here
            continue

        reply = ask_ollama(user_input)
        print("🤖 AI says:", reply)

        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
        notes = data.get(category, {}).get("notes", [])
        if notes:
            print(f"🗂️ Notes in {category}:")
            for i, note in enumerate(notes, 1):
                print(f"{i}. {note}")
        else:
            print(f"📭 No notes found in {category}.")
        continue


        # 🤖 Default: Ask the AI
        reply = ask_ollama(user_input)
        print("🤖 AI says:", reply)
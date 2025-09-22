import requests
import json
import os
import subprocess
from bs4 import BeautifulSoup
from learn_from_pdf import extract_text_from_pdf
from learn_from_ebook import extract_text_from_epub
from learn_from_url import extract_text_from_url

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

def patch_file(path, find_text, replace_text, reason="Auto-patch"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if find_text not in content:
            print("🔍 Patch target not found.")
            return
        updated = content.replace(find_text, replace_text)
        with open(path, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"🛠️ Patched {path} for: {reason}")
        commit_to_git(path, f"Auto-patch: {reason}")
        add_note("AutoPatch", f"{path} patched: {reason}")
    except Exception as e:
        print(f"❌ Patch error: {e}")

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

# 🧠 List notes in a category
def list_notes(category):
    category = category.lower()
    if not os.path.exists(MEMORY_FILE):
        print("Memory file not found.")
        return
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
        notes = data.get(category, {}).get("notes", [])
        if notes:
            print(f"🗂️ Notes in {category}:")
            for i, note in enumerate(notes, 1):
                print(f"{i}. {note}")
        else:
            print(f"📭 No notes found in {category}.")

# 🚀 Push changes to GitHub
def commit_to_git(file_path, message="Auto-update from agent"):
    try:
        subprocess.run(["git", "add", file_path], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"🚀 Changes pushed to GitHub: {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")

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

def diagnose_and_patch(error):
    error_type = type(error).__name__
    error_msg = str(error)
    print(f"🧠 Diagnosing: {error_type} - {error_msg}")

    prompt = f"""You're an AI agent that encountered this error:
Type: {error_type}
Message: {error_msg}

Suggest a one-line code fix or patch to resolve it. Be specific."""
    suggestion = ask_ollama(prompt)
    print(f"💡 Suggested fix: {suggestion}")

    # Optional: log the diagnosis
    add_note("AutoPatch", f"Diagnosed {error_type}: {error_msg}\nSuggested: {suggestion}")
    
# 🧠 Main loop
if __name__ == "__main__":
    while True:
        try:
            user_input = input("🧠 What do you want the AI to do? ")

            if user_input.lower().startswith("remember that"):
                parts = user_input[13:].split(" is ")
                if len(parts) == 2:
                    key_parts = parts[0].strip().split(" ")
                    if len(key_parts) >= 2:
                        category = key_parts[0]
                        key = " ".join(key_parts[1:])
                        value = parts[1].strip()
                        save_fact(category, key, value)
                        print(f"📝 Got it! I’ll remember that in {category}, {key} is {value}.")
                continue

            elif user_input.lower().startswith("what is"):
                key_parts = user_input[8:].strip().split(" ")
                if len(key_parts) >= 2:
                    
                    key = " ".join(key_parts[1:])
                    category = key_parts[0]\n        answer = recall_fact(category, key)
                    print(f"🧠 Memory says: {answer}")
                continue

            elif user_input.lower().startswith("note for"):
                parts = user_input[8:].split(":")
                if len(parts) == 2:
                    category = parts[0].strip()
                    note = parts[1].strip()
                    add_note(category, note)
                    print(f"🗒️ Note added to {category}: {note}")
                continue

            elif user_input.lower().startswith("list notes for"):
                category = user_input[15:].strip()
                list_notes(category)
                continue

            elif user_input.lower().startswith("search for"):
                query = user_input[11:].strip()
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
                results = "\n".join(snippets)
                print(f"🌐 Search results:\n{results}")
                add_note("WebSearch", f"{query}: {results}")
                continue

            elif user_input.lower().startswith("learn from url"):
                parts = user_input[15:].strip().split(" and save to ")
                url = parts[0].strip()
                save_path = parts[1].strip() if len(parts) == 2 else None
                content = extract_text_from_url(url)
                if not content:
                    print("⚠️ No content extracted from the URL.")
                    continue
                print(f"🧠 Preview of extracted content:\n{content[:500]}")
                summary_prompt = f"Summarize the key points from this webpage:\n{content[:3000]}"
                summary = ask_ollama(summary_prompt)
                print(f"🤖 Summary:\n{summary[:500]}")
                add_note("WebLearning", f"Learned from {url}:\n{summary}")
                print(f"✅ Summary saved to memory.")
                if save_path:
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(f"Summary of {url}:\n\n{summary}")
                    print(f"📁 Also saved to file: {save_path}")
                continue

            elif user_input.lower().startswith("learn from pdf"):
                parts = user_input[15:].strip().split(" and save to ")
                path = parts[0].strip()
                save_path = parts[1].strip() if len(parts) == 2 else None
                content = extract_text_from_pdf(path)
                summary_prompt = f"Summarize this PDF:\n{content[:3000]}"
                summary = ask_ollama(summary_prompt)
                add_note("PDFLearning", f"Learned from {path}:\n{summary}")
                print(f"📘 Learned from {path}. Summary saved to memory.")
                if save_path:
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(f"Summary of {path}:\n\n{summary}")
                    print(f"📁 Also saved to file: {save_path}")
                continue

            elif user_input.lower().startswith("learn from epub"):
                parts = user_input[16:].strip().split(" and save to ")
                path = parts[0].strip()
                save_path = parts[1].strip() if len(parts) == 2 else None
                content = extract_text_from_epub(path)
                summary_prompt = f"Summarize this EPUB:\n{content[:3000]}"
                summary = ask_ollama(summary_prompt)
                add_note("EPUBLearning", f"Learned from {path}:\n{summary}")
                print(f"📗 Learned from {path}. Summary saved to memory.")
                if save_path:
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(f"Summary of {path}:\n\n{summary}")
                    print(f"📁 Also saved to file: {save_path}")
                continue

            elif user_input.lower().startswith("edit file"):
                parts = user_input[10:].split(" find ")
                if len(parts) == 2:
                    file_part, rest = parts
                    file_path = file_part.strip()
                    find_replace = rest.split(" replace ")
                    if len(find_replace) == 2:
                        find_text = find_replace[0].strip()
                        replace_text = find_replace[1].strip()
                        edit_file(file_path, find_text, replace_text)
                continue

            elif user_input.lower().startswith("patch file"):
                parts = user_input[11:].split(" find ")
                if len(parts) == 2:
                    file_part, rest = parts
                    file_path = file_part.strip()
                    find_replace = rest.split(" replace ")
                    if len(find_replace) == 2:
                        find_text = find_replace[0].strip()
                        replace_text = find_replace[1].strip()
                        patch_file(file_path, find_text, replace_text, reason="Manual patch")
                continue

            else:
                response = ask_ollama(user_input)
                print(f"🤖 AI says: {response}")

        except Exception as e:
            print(f"⚠️ Agent error: {e}")
            diagnose_and_patch(e)
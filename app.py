import streamlit as st
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="Playwright Test Generator", layout="wide")
st.title("GenAI-powered Playwright Test Generator")
# Step-to-UI Action Mapping (Mocked)
st.subheader("Step-to-UI Action Mapping")

# Step definitions
step_defs = st.text_area("Step Definitions", height=150, placeholder="When user logs in\nThen dashboard loads...")

# UI Flow JSON
ui_json = st.text_area("Recorded UI Flow JSON", height=200, placeholder='Paste DevTools or CDP JSON')

if st.button("Match Step Definitions to UI Actions"):
    # Mocked response - in real implementation this would call GenAI model
    step_lines = step_defs.splitlines()
    mock_mapping = {step: {"action": "click", "target": ui.get("text", "")} 
                    for step, ui in zip(step_lines, st.session_state.ui_data[:len(step_lines)])}
    st.session_state.mapping_json = json.dumps(mock_mapping, indent=2)

st.text_area("Step to UI Action Mapping (editable)", value=st.session_state.mapping_json, key="mapping_json_editor", height=250)

# DOM Snapshots
st.markdown("---")
st.subheader("DOM Snapshots and HAR Upload")
dom_files = st.file_uploader("Upload DOM Snapshots (HTML or JSON)", type=['html', 'json'], accept_multiple_files=True)

# HAR file
har_file = st.file_uploader("Upload HAR File", type=['har'])

# Additional instructions
custom_instructions = st.text_area("Custom Instructions (optional)", height=100)

# Parse DOM snapshots
def parse_dom(dom_contents):
    extracted_data = []
    for dom in dom_contents:
        soup = BeautifulSoup(dom, 'html.parser')
        elements = soup.find_all(["h1", "h2", "p", "button", "input", "span", "div"])
        for el in elements:
            text = el.get_text(strip=True)
            if text:
                extracted_data.append({"text": text, "html": str(el)})
    return extracted_data

# Parse HAR and extract JSON responses
def parse_har(har_raw):
    try:
        har = json.loads(har_raw)
        entries = har.get("log", {}).get("entries", [])
        json_bodies = []
        for entry in entries:
            try:
                content = entry["response"].get("content", {})
                if content.get("mimeType", "").startswith("application/json"):
                    text = content.get("text")
                    if text:
                        json_bodies.append({
                            "url": entry.get("request", {}).get("url", ""),
                            "json": json.loads(text)
                        })
            except Exception:
                continue
        return json_bodies
    except Exception as e:
        st.error(f"HAR parsing failed: {e}")
        return []

# Save uploaded and processed data
def save_file(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

# Global vars for session state
if "ui_data" not in st.session_state:
    st.session_state.ui_data = []
if "api_data" not in st.session_state:
    st.session_state.api_data = []
if "mapping_json" not in st.session_state:
    st.session_state.mapping_json = ""
if "ui_api_mapping_json" not in st.session_state:
    st.session_state.ui_api_mapping_json = ""
if "ui_api_mappings" not in st.session_state:
    st.session_state.ui_api_mappings = []

# Process inputs
if st.button("Generate Playwright Test"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    dom_contents = [f.read().decode("utf-8") for f in dom_files] if dom_files else []
    har_raw = har_file.read().decode("utf-8") if har_file else ""

    st.session_state.ui_data = parse_dom(dom_contents)
    st.session_state.api_data = parse_har(har_raw)

    # Save inputs
    save_file(f"step_definitions_{timestamp}.txt", step_defs)
    save_file(f"ui_flow_{timestamp}.json", ui_json)
    for i, dom in enumerate(dom_contents):
        save_file(f"dom_snapshot_{i+1}_{timestamp}.html", dom)
    if har_raw:
        save_file(f"har_{timestamp}.har", har_raw)
    if custom_instructions:
        save_file(f"instructions_{timestamp}.txt", custom_instructions)

    # Save parsed DOM and HAR data
    save_file(f"parsed_dom_{timestamp}.json", json.dumps(st.session_state.ui_data, indent=2))
    save_file(f"parsed_har_{timestamp}.json", json.dumps(st.session_state.api_data, indent=2))

    st.success("All files saved successfully, including parsed DOM and HAR.")

st.markdown("---")
st.header("UI ↔ API Mapping via GenAI")

st.markdown("""
Instructions for mapping UI to API:
- You can create multiple mappings by repeating the form below.
- Provide the **API URL or a keyword from the HAR** to extract a specific response.
- Optionally, provide a **base locator or keyword** from the DOM (we’ll extract the corresponding element).
- GenAI will use both to understand how UI elements reflect API data.
""")

if st.button("+ Add Mapping Section"):
    st.session_state.ui_api_mappings.append({"api_keyword": "", "dom_keyword": ""})

for idx in range(len(st.session_state.ui_api_mappings)):
    mapping = st.session_state.ui_api_mappings[idx]
    st.subheader(f"Mapping {idx + 1}")
    cols = st.columns([4, 4, 1])
    with cols[0]:
        api_keyword = st.text_input(f"API Keyword or Exact URL {idx + 1}", value=mapping["api_keyword"], key=f"api_keyword_{idx}")
        st.session_state.ui_api_mappings[idx]["api_keyword"] = api_keyword
    with cols[1]:
        dom_keyword = st.text_input(f"(Optional) DOM Text or Locator to Map {idx + 1}", value=mapping["dom_keyword"], key=f"dom_keyword_{idx}")
        st.session_state.ui_api_mappings[idx]["dom_keyword"] = dom_keyword
    with cols[2]:
        if st.button("🗑️", key=f"remove_{idx}"):
            st.session_state.ui_api_mappings.pop(idx)
            st.experimental_rerun()

    if st.button(f"Match UI to API {idx + 1}"):
        matched_api = next((entry for entry in st.session_state.api_data if api_keyword in entry["url"]), None)
        matched_dom = next((node for node in st.session_state.ui_data if dom_keyword.lower() in node["text"].lower()), None) if dom_keyword else None

        mock_ui_api_mapping = {
            "api_url": matched_api["url"] if matched_api else api_keyword,
            "api_data_sample": matched_api["json"] if matched_api else {},
            "ui_element_html": matched_dom["html"] if matched_dom else "(No UI element matched)"
        }

        st.session_state.ui_api_mapping_json = json.dumps(mock_ui_api_mapping, indent=2)

    st.text_area(f"UI ↔ API Mapping (editable) {idx + 1}", value=st.session_state.ui_api_mapping_json, key=f"ui_api_mapping_editor_{idx}", height=300)

Indian State / Place Guessing Game
=================================

A small interactive geography quiz built with Streamlit. The app highlights a location on a map and asks the player to choose the correct Indian state/place from multiple choices.

Contents
--------
- `app.py` - Streamlit application (main entrypoint)
- `data/states.json` - JSON dataset (array of objects with `name`, `hint`, `coords`)

Quick start (Windows PowerShell)
-------------------------------
1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
streamlit run app.py
python -m streamlit run app.py
```

Project details
---------------
- The app loads `data/states.json` via a cached loader (`st.cache_data`) for faster startup.
- On startup the app validates each dataset entry has `name`, `hint`, and `coords` (coords must be a list of at least two numbers). Invalid entries will produce Streamlit warnings.
- The map rendering uses `pydeck` ScatterplotLayer to show a marker without tooltips/labels.
- Programmatic reruns are handled with a compatibility helper that works across Streamlit versions.
- A small CSS snippet is injected to provide consistent button styling. If Streamlit updates internal class names in the future, you may need to update the selectors.

Editing data
------------
To add or change locations edit `data/states.json`. Each item should look like:

```json
{
  "name": "Example Place",
  "hint": "Near the river...",
  "coords": [25.3176, 82.9739]
}
```

Testing & development notes
---------------------------
- When importing `app.py` directly (e.g., for linting or static checks) Streamlit will emit "missing ScriptRunContext" warnings — these are normal when not running under `streamlit run`.
- If you want reproducible installs across machines, pin exact versions. See `requirements.txt` for suggested pins.

Dependencies (runtime)
----------------------
- Python 3.8+
- Streamlit
- pydeck

Optional suggestions
--------------------
- Add `prettier` or JSON linter as part of CI to keep `data/states.json` formatted.
- Add a small test harness that imports `load_states` and validates the schema automatically.

License
-------
This is provided as-is for learning and experimentation.

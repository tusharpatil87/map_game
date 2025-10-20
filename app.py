import streamlit as st
import random
import json
import pydeck as pdk

# Load sample data from JSON (cached)

@st.cache_data
def load_states(path: str = 'data/states.json'):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_states(states_list):
    """Return (valid_states, problems) where problems is a list of messages."""
    valid = []
    problems = []
    for i, item in enumerate(states_list):
        missing = []
        if not isinstance(item, dict):
            problems.append(f"Entry {i} is not an object.")
            continue
        if 'name' not in item:
            missing.append('name')
        if 'hint' not in item:
            missing.append('hint')
        if 'coords' not in item:
            missing.append('coords')
        else:
            if not (isinstance(item['coords'], list) and len(item['coords']) >= 2):
                missing.append('coords (invalid format)')
        if missing:
            problems.append(f"Entry {i} ('{item.get('name', '<no-name>')}') missing: {', '.join(missing)}")
        else:
            valid.append(item)
    return valid, problems

states_raw = load_states()
states, issues = validate_states(states_raw)
if issues:
    for msg in issues:
        st.warning(msg)

st.title("Indian State/Place Guessing Game")

# Inject site-wide CSS to color all Streamlit buttons (primary + hover/focus)
st.markdown(
    """
    <style>
    /* All Streamlit buttons */
    .stButton>button {
        background-color: #0d6efd !important; /* primary blue */
        color: #ffffff !important;
        border: none !important;
        padding: 8px 14px !important;
        border-radius: 6px !important;
        box-shadow: none !important;
        transition: background-color 0.12s ease !important;
    }
    .stButton>button:hover {
        background-color: #0b5ed7 !important; /* darker on hover */
    }
    .stButton>button:focus {
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(13,110,253,0.18) !important;
    }
    /* Make buttons in secondary places consistent too */
    button[role="button"] {
        background-color: #0d6efd !important;
        color: #fff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if 'score' not in st.session_state:
    st.session_state.score = 0
if 'question' not in st.session_state:
    st.session_state.question = random.choice(states)
if 'options' not in st.session_state:
    st.session_state.options = random.sample(states, k=3)
    if st.session_state.question not in st.session_state.options:
        st.session_state.options[0] = st.session_state.question
    random.shuffle(st.session_state.options)

# Show map with highlighted state (simulate by showing a marker)
try:
    # Use pydeck scatterplot layer to avoid showing any tooltip/label text
    lat, lon = st.session_state.question["coords"][0], st.session_state.question["coords"][1]
    view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=5)
    scatter = pdk.Layer(
        "ScatterplotLayer",
        data=[{"lat": lat, "lon": lon}],
        get_position="[lon, lat]",
        get_radius=50000,
        get_fill_color=[200, 30, 0, 160],
        pickable=False,
    )
    deck = pdk.Deck(layers=[scatter], initial_view_state=view_state)
    st.pydeck_chart(deck)
except Exception:
    # Fallback: simple st.map (may show default labels/tooltips)
    st.map({
        "latitude": [st.session_state.question["coords"][0]],
        "longitude": [st.session_state.question["coords"][1]]
    })

st.write(f"Hint: {st.session_state.question['hint']}")

options = [s["name"] for s in st.session_state.options]
user_answer = st.radio("Which state or place is highlighted?", options)

if 'last_result' not in st.session_state:
    st.session_state.last_result = None
if 'game_active' not in st.session_state:
    st.session_state.game_active = True

def _prepare_next_question():
    st.session_state.question = random.choice(states)
    st.session_state.options = random.sample(states, k=3)
    if st.session_state.question not in st.session_state.options:
        st.session_state.options[0] = st.session_state.question
    random.shuffle(st.session_state.options)


def _restart_game():
    # Reset all relevant session state variables
    st.session_state.score = 0
    st.session_state.question = random.choice(states)
    st.session_state.options = random.sample(states, k=3)
    if st.session_state.question not in st.session_state.options:
        st.session_state.options[0] = st.session_state.question
    random.shuffle(st.session_state.options)
    st.session_state.last_result = None
    st.session_state.game_active = True
    # Use a safe rerun helper to support multiple Streamlit versions
    def safe_rerun():
        # Preferred in newer versions
        if hasattr(st, "experimental_rerun"):
            try:
                return st.experimental_rerun()
            except Exception:
                pass
        # Older variants
        if hasattr(st, "rerun"):
            try:
                return st.rerun()
            except Exception:
                pass
        # As a last resort, tweak query params to force a reload
        try:
            st.experimental_set_query_params(_refresh=random.random())
        except Exception:
            # Nothing else we can do
            return None

    safe_rerun()

if st.session_state.game_active:
    if st.button("Submit"):
        if user_answer == st.session_state.question["name"]:
            st.success("Correct! 🎉")
            st.session_state.score += 1
            st.session_state.last_result = "correct"
        else:
            st.error(f"Wrong! The correct answer was {st.session_state.question['name']}.")
            st.session_state.last_result = "wrong"

    # If an answer was just submitted, show play next / restart / exit options
    if st.session_state.last_result in ("correct", "wrong"):
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Play Next"):
                _prepare_next_question()
                st.session_state.last_result = None
                # use safe rerun helper if available
                try:
                    # try experimental first
                    if hasattr(st, "experimental_rerun"):
                        st.experimental_rerun()
                    elif hasattr(st, "rerun"):
                        st.rerun()
                    else:
                        st.experimental_set_query_params(_refresh=random.random())
                except Exception:
                    pass
        with col2:
            if st.button("Restart"):
                _restart_game()
        with col3:
            if st.button("Exit"):
                st.session_state.game_active = False
                st.success("Thanks for playing! Come back soon. 👋")

else:
    st.info("Game is paused. Refresh the page or click 'Play Next' to start again.")

st.write(f"Score: {st.session_state.score}")

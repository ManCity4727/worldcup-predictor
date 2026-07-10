import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Results Tracker",
    page_icon="📊",
    layout="wide"
)

flag_map = {
    'Argentina': '🇦🇷', 'Spain': '🇪🇸', 'France': '🇫🇷',
    'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'Portugal': '🇵🇹', 'Brazil': '🇧🇷',
    'Morocco': '🇲🇦', 'Netherlands': '🇳🇱', 'Belgium': '🇧🇪',
    'Germany': '🇩🇪', 'Croatia': '🇭🇷', 'Colombia': '🇨🇴',
    'Mexico': '🇲🇽', 'Senegal': '🇸🇳', 'Uruguay': '🇺🇾',
    'United States': '🇺🇸', 'Japan': '🇯🇵', 'Switzerland': '🇨🇭',
    'Iran': '🇮🇷', 'Turkey': '🇹🇷', 'Ecuador': '🇪🇨',
    'Austria': '🇦🇹', 'South Korea': '🇰🇷', 'Australia': '🇦🇺',
    'Algeria': '🇩🇿', 'Egypt': '🇪🇬', 'Canada': '🇨🇦',
    'Norway': '🇳🇴', 'Ivory Coast': '🇨🇮', 'Panama': '🇵🇦',
    'Sweden': '🇸🇪', 'Czech Republic': '🇨🇿', 'Paraguay': '🇵🇾',
    'Scotland': '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'Tunisia': '🇹🇳', 'DR Congo': '🇨🇩',
    'Uzbekistan': '🇺🇿', 'Qatar': '🇶🇦', 'Iraq': '🇮🇶',
    'South Africa': '🇿🇦', 'Saudi Arabia': '🇸🇦', 'Jordan': '🇯🇴',
    'Bosnia and Herzegovina': '🇧🇦', 'Cape Verde': '🇨🇻',
    'Ghana': '🇬🇭', 'Curacao': '🇨🇼', 'Haiti': '🇭🇹',
    'New Zealand': '🇳🇿', 'Czech Republic': '🇨🇿', 'Curacao': '🇨🇼',
}

def get_flag(team):
    return flag_map.get(team, '🏳️')

# ── Name mapping — API names to our names ─────────────────────
name_map = {
    'Morocco': 'Morocco',
    'France': 'France',
    'Spain': 'Spain',
    'Belgium': 'Belgium',
    'Norway': 'Norway',
    'England': 'England',
    'Argentina': 'Argentina',
    'Switzerland': 'Switzerland',
    'Brazil': 'Brazil',
    'Japan': 'Japan',
    'Germany': 'Germany',
    'Paraguay': 'Paraguay',
    'Netherlands': 'Netherlands',
    'Sweden': 'Sweden',
    'Ivory Coast': 'Ivory Coast',
    "Côte d'Ivoire": 'Ivory Coast',
    'Mexico': 'Mexico',
    'Ecuador': 'Ecuador',
    'United States': 'United States',
    'USA': 'United States',
    'Bosnia and Herzegovina': 'Bosnia and Herzegovina',
    'Belgium': 'Belgium',
    'Senegal': 'Senegal',
    'England': 'England',
    'DR Congo': 'DR Congo',
    'Congo DR': 'DR Congo',
    'Colombia': 'Colombia',
    'Croatia': 'Croatia',
    'Austria': 'Austria',
    'Algeria': 'Algeria',
    'Argentina': 'Argentina',
    'Cape Verde': 'Cape Verde',
    'Cabo Verde': 'Cape Verde',
    'Australia': 'Australia',
    'Egypt': 'Egypt',
    'Portugal': 'Portugal',
    'Ghana': 'Ghana',
    'Canada': 'Canada',
    'South Africa': 'South Africa',
    'South Korea': 'South Korea',
    'Korea Republic': 'South Korea',
    'Czechia': 'Czech Republic',
    'Czech Republic': 'Czech Republic',
    'Curaçao': 'Curacao',
    'Curacao': 'Curacao',
}

def normalize_name(name):
    return name_map.get(name, name)

# ── Model predictions for each knockout match ─────────────────
# Format: (home, away, predicted_winner, predicted_home_pct)
predictions = {
    # Round of 32
    ('South Africa', 'Canada'): ('Canada', 66.8),
    ('Brazil', 'Japan'): ('Brazil', 63.8),
    ('Germany', 'Paraguay'): ('Germany', 44.7),
    ('Netherlands', 'Morocco'): ('Netherlands', 58.1),
    ('France', 'Sweden'): ('France', 46.5),
    ('Ivory Coast', 'Norway'): ('Norway', 54.5),
    ('Mexico', 'Ecuador'): ('Mexico', 44.7),
    ('United States', 'Bosnia and Herzegovina'): ('United States', 66.7),
    ('Belgium', 'Senegal'): ('Belgium', 48.9),
    ('England', 'DR Congo'): ('England', 60.2),
    ('Colombia', 'Croatia'): ('Colombia', 43.1),
    ('Spain', 'Austria'): ('Spain', 52.1),
    ('Switzerland', 'Algeria'): ('Switzerland', 54.8),
    ('Argentina', 'Cape Verde'): ('Argentina', 73.2),
    ('Australia', 'Egypt'): ('Australia', 30.7),
    ('Portugal', 'Ghana'): ('Portugal', 60.2),
    # Round of 16
    ('Morocco', 'Canada'): ('Morocco', 55.0),
    ('France', 'Paraguay'): ('France', 46.5),
    ('Norway', 'Brazil'): ('Brazil', 63.8),
    ('England', 'Mexico'): ('England', 48.9),
    ('Spain', 'Portugal'): ('Spain', 54.3),
    ('Belgium', 'United States'): ('Belgium', 55.5),
    ('Argentina', 'Egypt'): ('Argentina', 61.1),
    ('Switzerland', 'Colombia'): ('Switzerland', 54.8),
    # Quarterfinals
    ('France', 'Morocco'): ('France', 55.5),
    ('Spain', 'Belgium'): ('Spain', 54.3),
    ('Norway', 'England'): ('England', 62.5),
    ('Argentina', 'Switzerland'): ('Argentina', 61.1),
}

@st.cache_data(ttl=300)  # refresh every 5 minutes
def fetch_wc_results():
    """Fetch 2026 World Cup knockout results from API."""
    api_key = st.secrets["FOOTBALL_API_KEY"]
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    headers = {"X-Auth-Token": api_key}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None, f"API error: {response.status_code}"

        data = response.json()
        matches = data.get('matches', [])

        # Filter to knockout stage only
        knockout_stages = [
            'ROUND_OF_32', 'ROUND_OF_16',
            'QUARTER_FINALS', 'SEMI_FINALS', 'FINAL'
        ]

        knockout_matches = []
        for m in matches:
            stage = m.get('stage', '')
            status = m.get('status', '')

            if stage not in knockout_stages:
                continue

            home = normalize_name(
                m['homeTeam'].get('name', ''))
            away = normalize_name(
                m['awayTeam'].get('name', ''))
            score = m.get('score', {})
            full_time = score.get('fullTime', {})
            hs = full_time.get('home')
            as_ = full_time.get('away')

            # Stage label
            stage_labels = {
                'ROUND_OF_32': 'Round of 32',
                'ROUND_OF_16': 'Round of 16',
                'QUARTER_FINALS': 'Quarterfinal',
                'SEMI_FINALS': 'Semifinal',
                'FINAL': 'Final'
            }

            knockout_matches.append({
                'home': home,
                'away': away,
                'home_score': hs,
                'away_score': as_,
                'stage': stage_labels.get(stage, stage),
                'status': status,
                'date': m.get('utcDate', '')[:10]
            })

        return knockout_matches, None

    except Exception as e:
        return None, str(e)

def get_actual_winner(home, away, hs, as_):
    if hs is None or as_ is None:
        return None
    if hs > as_:
        return home
    elif as_ > hs:
        return away
    else:
        return 'Penalties'

def get_prediction(home, away):
    return predictions.get((home, away),
           predictions.get((away, home), None))

# ── UI ────────────────────────────────────────────────────────
st.title("📊 Live Results Tracker")
st.caption("Model predictions vs actual 2026 World Cup results "
           "— updates every 5 minutes")

matches, error = fetch_wc_results()

if error:
    st.error(f"Could not fetch results: {error}")
    st.stop()

if not matches:
    st.info("No knockout matches found yet.")
    st.stop()

# ── Calculate accuracy ────────────────────────────────────────
completed = [m for m in matches
             if m['status'] == 'FINISHED']
correct = 0
total = 0

for m in completed:
    pred = get_prediction(m['home'], m['away'])
    if pred is None:
        continue
    predicted_winner = pred[0]
    actual = get_actual_winner(
        m['home'], m['away'],
        m['home_score'], m['away_score'])
    if actual == 'Penalties':
        continue
    total += 1
    if predicted_winner == actual:
        correct += 1

# ── Accuracy header ───────────────────────────────────────────
st.divider()
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("✅ Correct", correct)
with c2:
    st.metric("❌ Incorrect", total - correct)
with c3:
    accuracy = correct/total*100 if total > 0 else 0
    st.metric("📈 Accuracy", f"{accuracy:.1f}%")
with c4:
    st.metric("vs Random (50%)",
              f"{accuracy - 50:+.1f}%")

st.divider()

# ── Results by stage ──────────────────────────────────────────
stage_order = [
    'Round of 32', 'Round of 16',
    'Quarterfinal', 'Semifinal', 'Final'
]

for stage in stage_order:
    stage_matches = [m for m in matches
                     if m['stage'] == stage]
    if not stage_matches:
        continue

    finished = [m for m in stage_matches
                if m['status'] == 'FINISHED']
    pending = [m for m in stage_matches
               if m['status'] != 'FINISHED']

    stage_correct = 0
    stage_total = 0
    for m in finished:
        pred = get_prediction(m['home'], m['away'])
        if pred is None:
            continue
        actual = get_actual_winner(
            m['home'], m['away'],
            m['home_score'], m['away_score'])
        if actual == 'Penalties':
            continue
        stage_total += 1
        if pred[0] == actual:
            stage_correct += 1

    if stage_total > 0:
        stage_acc = stage_correct/stage_total*100
        st.subheader(
            f"{stage} — "
            f"{stage_correct}/{stage_total} correct "
            f"({stage_acc:.0f}%)"
        )
    else:
        st.subheader(stage)

    for m in stage_matches:
        fh = get_flag(m['home'])
        fa = get_flag(m['away'])
        pred = get_prediction(m['home'], m['away'])

        if m['status'] == 'FINISHED':
            hs = m['home_score']
            as_ = m['away_score']
            actual = get_actual_winner(
                m['home'], m['away'], hs, as_)

            if pred:
                predicted_winner = pred[0]
                pct = pred[1]
                if actual == 'Penalties':
                    icon = "🟡"
                    result_text = "Went to penalties"
                elif predicted_winner == actual:
                    icon = "✅"
                    result_text = f"Predicted correctly ({pct}%)"
                else:
                    icon = "❌"
                    result_text = (
                        f"Predicted {get_flag(predicted_winner)} "
                        f"{predicted_winner} ({pct}%)"
                    )
            else:
                icon = "⚪"
                result_text = "No prediction"

            st.markdown(
                f"{icon} {fh} **{m['home']}** {hs}–{as_} "
                f"{fa} **{m['away']}** · {result_text}"
            )

        elif m['status'] == 'IN_PROGRESS':
            st.markdown(
                f"🔴 LIVE: {fh} **{m['home']}** vs "
                f"{fa} **{m['away']}**"
            )

        else:
            pred_text = ""
            if pred:
                pw = pred[0]
                pct = pred[1]
                pred_text = (
                    f"· Model: {get_flag(pw)} "
                    f"**{pw}** ({pct}%)"
                )
            st.markdown(
                f"⏳ {fh} **{m['home']}** vs "
                f"{fa} **{m['away']}** "
                f"{pred_text}"
            )

    st.markdown("")

st.divider()
st.caption(
    f"Data: football-data.org · "
    f"Refreshes every 5 minutes · "
    f"Last updated: {datetime.now().strftime('%H:%M:%S')}"
)
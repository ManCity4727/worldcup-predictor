import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.set_page_config(
    page_title="Tournament Simulator",
    page_icon="🏆",
    layout="wide"
)

# ── Flag map ──────────────────────────────────────────────────
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
    'Sweden': '🇸🇪', 'Czechia': '🇨🇿', 'Paraguay': '🇵🇾',
    'Scotland': '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'Tunisia': '🇹🇳', 'DR Congo': '🇨🇩',
    'Uzbekistan': '🇺🇿', 'Qatar': '🇶🇦', 'Iraq': '🇮🇶',
    'South Africa': '🇿🇦', 'Saudi Arabia': '🇸🇦', 'Jordan': '🇯🇴',
    'Bosnia and Herzegovina': '🇧🇦', 'Cape Verde': '🇨🇻',
    'Ghana': '🇬🇭', 'Curacao': '🇨🇼', 'Haiti': '🇭🇹',
    'New Zealand': '🇳🇿',
}

def get_flag(team):
    return flag_map.get(team, '🏳️')

# ── Load data ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('results.csv')
    wc = df[df['tournament'] == 'FIFA World Cup'].copy()
    wc = wc.dropna(subset=['home_score', 'away_score'])
    wc['date'] = pd.to_datetime(wc['date'])

    home_attack = wc.groupby('home_team')['home_score'].mean()
    home_defense = wc.groupby('home_team')['away_score'].mean()
    away_attack = wc.groupby('away_team')['away_score'].mean()
    away_defense = wc.groupby('away_team')['home_score'].mean()

    attack = (home_attack + away_attack) / 2
    defense = (home_defense + away_defense) / 2
    avg_goals = wc['home_score'].mean()

    team_stats = pd.DataFrame({
        'attack': attack,
        'defense': defense
    }).dropna()

    return team_stats, avg_goals

team_stats, avg_goals = load_data()

# ── Data ──────────────────────────────────────────────────────
fifa_rankings = {
    'Argentina': 1, 'Spain': 2, 'France': 3, 'England': 4,
    'Portugal': 5, 'Brazil': 6, 'Morocco': 7, 'Netherlands': 8,
    'Belgium': 9, 'Germany': 10, 'Croatia': 11, 'Colombia': 13,
    'Mexico': 14, 'Senegal': 15, 'Uruguay': 16, 'United States': 17,
    'Japan': 18, 'Switzerland': 19, 'Iran': 20, 'Turkey': 22,
    'Ecuador': 23, 'Austria': 24, 'South Korea': 25, 'Australia': 27,
    'Algeria': 28, 'Egypt': 29, 'Canada': 30, 'Norway': 31,
    'Ivory Coast': 33, 'Panama': 34, 'Sweden': 38, 'Czechia': 40,
    'Paraguay': 41, 'Scotland': 42, 'Tunisia': 45, 'DR Congo': 46,
    'Uzbekistan': 50, 'Qatar': 56, 'Iraq': 57, 'South Africa': 60,
    'Saudi Arabia': 61, 'Jordan': 63, 'Bosnia and Herzegovina': 64,
    'Cape Verde': 67, 'Ghana': 73, 'Curacao': 82, 'Haiti': 83,
    'New Zealand': 85
}

continent_map = {
    'Brazil': 'South America', 'Argentina': 'South America',
    'Uruguay': 'South America', 'Colombia': 'South America',
    'Ecuador': 'South America', 'Paraguay': 'South America',
    'France': 'Europe', 'Spain': 'Europe', 'England': 'Europe',
    'Germany': 'Europe', 'Portugal': 'Europe', 'Netherlands': 'Europe',
    'Belgium': 'Europe', 'Croatia': 'Europe', 'Switzerland': 'Europe',
    'Denmark': 'Europe', 'Norway': 'Europe', 'Austria': 'Europe',
    'Sweden': 'Europe', 'Scotland': 'Europe', 'Turkey': 'Europe',
    'Serbia': 'Europe', 'Czechia': 'Europe',
    'Bosnia and Herzegovina': 'Europe', 'Italy': 'Europe',
    'Morocco': 'Africa', 'Senegal': 'Africa', 'Ghana': 'Africa',
    'Cameroon': 'Africa', 'Ivory Coast': 'Africa', 'Tunisia': 'Africa',
    'Algeria': 'Africa', 'Egypt': 'Africa', 'South Africa': 'Africa',
    'DR Congo': 'Africa', 'Cape Verde': 'Africa',
    'Japan': 'Asia', 'South Korea': 'Asia', 'Iran': 'Asia',
    'Saudi Arabia': 'Asia', 'Australia': 'Asia', 'Qatar': 'Asia',
    'Iraq': 'Asia', 'Jordan': 'Asia', 'Uzbekistan': 'Asia',
    'United States': 'CONCACAF', 'Mexico': 'CONCACAF',
    'Canada': 'CONCACAF', 'Costa Rica': 'CONCACAF',
    'Panama': 'CONCACAF', 'Haiti': 'CONCACAF', 'Curacao': 'CONCACAF',
    'New Zealand': 'Oceania',
}

continent_advantage = {
    'Asia': 1.185, 'CONCACAF': 1.110,
    'South America': 1.098, 'Europe': 1.055,
    'Africa': 0.979, 'Oceania': 1.0,
}

squad_fatigue = {
    'France': 0.82, 'England': 0.79, 'Spain': 0.78,
    'Belgium': 0.76, 'Germany': 0.75, 'Netherlands': 0.73,
    'Portugal': 0.71, 'Morocco': 0.70, 'Denmark': 0.70,
    'Croatia': 0.69, 'Norway': 0.68, 'Argentina': 0.68,
    'Brazil': 0.65, 'Turkey': 0.65, 'Austria': 0.66,
    'Sweden': 0.64, 'Senegal': 0.63, 'Colombia': 0.60,
    'Uruguay': 0.61, 'Ivory Coast': 0.62, 'Japan': 0.58,
    'Bosnia and Herzegovina': 0.58, 'Ecuador': 0.57,
    'Australia': 0.54, 'Ghana': 0.55, 'South Korea': 0.55,
    'Mexico': 0.55, 'Algeria': 0.56, 'Uzbekistan': 0.47,
    'Canada': 0.52, 'Cape Verde': 0.52, 'Egypt': 0.53,
    'Tunisia': 0.54, 'Paraguay': 0.50, 'United States': 0.50,
    'Panama': 0.49, 'DR Congo': 0.49, 'Iran': 0.48,
    'Curacao': 0.48, 'Saudi Arabia': 0.46, 'Haiti': 0.46,
    'South Africa': 0.45, 'Iraq': 0.45, 'Qatar': 0.44,
    'Jordan': 0.44, 'New Zealand': 0.43, 'Scotland': 0.67,
    'Switzerland': 0.67,
}

# ── Model functions ───────────────────────────────────────────
def get_lambda(team_a, team_b):
    if team_a in team_stats.index and team_b in team_stats.index:
        hist = (team_stats.loc[team_a, 'attack'] *
                (team_stats.loc[team_b, 'defense'] / avg_goals))
    else:
        hist = avg_goals
    rank_a = 1.4 - (fifa_rankings.get(team_a, 43) / 85) * 0.8
    rank_b = 1.4 - (fifa_rankings.get(team_b, 43) / 85) * 0.8
    rank_lambda = avg_goals * (rank_a / rank_b)
    return round(0.4 * hist + 0.6 * rank_lambda, 3)

def get_continent_boost(team):
    tc = continent_map.get(team, None)
    if tc == 'CONCACAF':
        return continent_advantage.get(tc, 1.0)
    return 1.0

def get_fatigue_mult(team):
    fatigue = squad_fatigue.get(team, 0.60)
    return round(1.05 - ((fatigue - 0.45) /
                         (0.82 - 0.45)) * 0.17, 3)

def dixon_coles(g_a, g_b, la, lb, rho=0.1):
    if g_a == 0 and g_b == 0:
        return 1 - la * lb * rho
    elif g_a == 0 and g_b == 1:
        return 1 + la * rho
    elif g_a == 1 and g_b == 0:
        return 1 + lb * rho
    elif g_a == 1 and g_b == 1:
        return 1 - rho
    return 1.0

def simulate_match(team_a, team_b):
    la = get_lambda(team_a, team_b)
    lb = get_lambda(team_b, team_a)
    la *= get_continent_boost(team_a)
    lb *= get_continent_boost(team_b)
    la *= get_fatigue_mult(team_a)
    lb *= get_fatigue_mult(team_b)
    la = max(la, 0.1)
    lb = max(lb, 0.1)

    ga = poisson.rvs(la)
    gb = poisson.rvs(lb)

    corr = dixon_coles(ga, gb, la, lb)
    if np.random.random() > corr:
        ga = poisson.rvs(la)
        gb = poisson.rvs(lb)

    if ga > gb:
        return team_a
    elif gb > ga:
        return team_b
    else:
        eta = poisson.rvs(la * 0.33)
        etb = poisson.rvs(lb * 0.33)
        if eta > etb:
            return team_a
        elif etb > eta:
            return team_b
        else:
            ra = fifa_rankings.get(team_a, 43)
            rb = fifa_rankings.get(team_b, 43)
            if np.random.random() < (0.52 if ra < rb else 0.48):
                return team_a
            return team_b

def simulate_tournament(bracket, n):
    all_teams = [t for match in bracket for t in match]
    wins = {t: 0 for t in all_teams}
    finals = {t: 0 for t in all_teams}
    semis = {t: 0 for t in all_teams}

    for _ in range(n):
        # Quarterfinals
        qf_winners = [simulate_match(a, b) for a, b in bracket]
        for w in qf_winners:
            semis[w] += 1

        # Semifinals
        sf1 = simulate_match(qf_winners[0], qf_winners[1])
        sf2 = simulate_match(qf_winners[2], qf_winners[3])
        finals[sf1] += 1
        finals[sf2] += 1

        # Final
        champion = simulate_match(sf1, sf2)
        wins[champion] += 1

    results = []
    for team in all_teams:
        results.append({
            'team': team,
            'flag': get_flag(team),
            'rank': fifa_rankings.get(team, 99),
            'win_pct': round(wins[team]/n*100, 1),
            'final_pct': round(finals[team]/n*100, 1),
            'semi_pct': round(semis[team]/n*100, 1),
        })
    results.sort(key=lambda x: x['win_pct'], reverse=True)
    return results

# ── UI ────────────────────────────────────────────────────────
st.title("🏆 World Cup 2026 Tournament Simulator")
st.caption("Simulates the remaining bracket thousands of "
           "times to calculate each team's win probability")

st.divider()

# ── Bracket setup ─────────────────────────────────────────────
st.subheader("⚙️ Set the quarterfinal bracket")
st.caption("Update if results have changed")

all_teams = sorted(fifa_rankings.keys())

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Quarterfinal 1**")
    qf1_a = st.selectbox("Team A", all_teams,
                          index=all_teams.index('France'), key='qf1a')
    qf1_b = st.selectbox("Team B", all_teams,
                          index=all_teams.index('Morocco'), key='qf1b')

    st.markdown("**Quarterfinal 2**")
    qf2_a = st.selectbox("Team A", all_teams,
                          index=all_teams.index('Spain'), key='qf2a')
    qf2_b = st.selectbox("Team B", all_teams,
                          index=all_teams.index('Belgium'), key='qf2b')

with col2:
    st.markdown("**Quarterfinal 3**")
    qf3_a = st.selectbox("Team A", all_teams,
                          index=all_teams.index('Norway'), key='qf3a')
    qf3_b = st.selectbox("Team B", all_teams,
                          index=all_teams.index('England'), key='qf3b')

    st.markdown("**Quarterfinal 4**")
    qf4_a = st.selectbox("Team A", all_teams,
                          index=all_teams.index('Argentina'), key='qf4a')
    qf4_b = st.selectbox("Team B", all_teams,
                          index=all_teams.index('Switzerland'), key='qf4b')

n_sims = st.select_slider("Simulations",
    options=[1000, 5000, 10000, 50000], value=10000)

if st.button("🔮 Simulate Tournament", type="primary",
             use_container_width=True):

    bracket = [
        (qf1_a, qf1_b),
        (qf2_a, qf2_b),
        (qf3_a, qf3_b),
        (qf4_a, qf4_b),
    ]

    with st.spinner(f"Simulating {n_sims:,} tournaments..."):
        results = simulate_tournament(bracket, n_sims)

    st.divider()
    st.subheader(f"Results — {n_sims:,} simulations")

    # ── Winner podium ─────────────────────────────────────────
    top3 = results[:3]
    p1, p2, p3 = st.columns(3)
    with p1:
        st.metric(
            f"🥇 {top3[0]['flag']} {top3[0]['team']}",
            f"{top3[0]['win_pct']}%",
            "Most likely champion"
        )
    with p2:
        st.metric(
            f"🥈 {top3[1]['flag']} {top3[1]['team']}",
            f"{top3[1]['win_pct']}%",
            "2nd most likely"
        )
    with p3:
        st.metric(
            f"🥉 {top3[2]['flag']} {top3[2]['team']}",
            f"{top3[2]['win_pct']}%",
            "3rd most likely"
        )

    st.divider()

    # ── Full table ────────────────────────────────────────────
    st.subheader("Full breakdown")
    st.caption("Semi% = probability of reaching semifinal · "
               "Final% = probability of reaching final · "
               "Win% = probability of winning World Cup")

    for r in results:
        c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 4])
        with c1:
            st.markdown(f"**{r['flag']} {r['team']}**")
        with c2:
            st.markdown(f"Semi: **{r['semi_pct']}%**")
        with c3:
            st.markdown(f"Final: **{r['final_pct']}%**")
        with c4:
            st.markdown(f"Win: **{r['win_pct']}%**")
        with c5:
            st.progress(r['win_pct'] / 25)

    st.divider()
    st.caption(
        f"Model: Poisson + FIFA rankings + fatigue + "
        f"continent advantage + Dixon-Coles · "
        f"{n_sims:,} simulations"
    )
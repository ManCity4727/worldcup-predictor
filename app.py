import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="World Cup 2026 Predictor",
    page_icon="⚽",
    layout="wide"
)

# ── Load data ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('results.csv')
    wc = df[df['tournament'] == 'FIFA World Cup'].copy()
    wc['date'] = pd.to_datetime(wc['date'])
    wc['year'] = wc['date'].dt.year

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
    'Serbia': 'Europe', 'Ukraine': 'Europe', 'Czechia': 'Europe',
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
def ranking_factor(team):
    rank = fifa_rankings.get(team, 43)
    return round(1.2 - (rank / 85) * 0.4, 3)

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
    return round(1.05 - ((fatigue - 0.45) / (0.82 - 0.45)) * 0.17, 3)

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

def simulate(team_a, team_b, n, injury_a, injury_b,
             use_continent, use_fatigue, knockout):

    la = get_lambda(team_a, team_b)
    lb = get_lambda(team_b, team_a)

    if use_continent:
        la *= get_continent_boost(team_a)
        lb *= get_continent_boost(team_b)
    if use_fatigue:
        la *= get_fatigue_mult(team_a)
        lb *= get_fatigue_mult(team_b)

    la *= (1 - injury_a / 100)
    lb *= (1 - injury_b / 100)

    la = max(la, 0.1)
    lb = max(lb, 0.1)

    wins_a = wins_b = draws = 0
    d90 = det = dpens = 0

    for _ in range(n):
        ga = poisson.rvs(la)
        gb = poisson.rvs(lb)

        corr = dixon_coles(ga, gb, la, lb)
        if np.random.random() > corr:
            ga = poisson.rvs(la)
            gb = poisson.rvs(lb)

        if ga > gb:
            wins_a += 1
            d90 += 1
        elif gb > ga:
            wins_b += 1
            d90 += 1
        else:
            if knockout:
                eta = poisson.rvs(la * 0.33)
                etb = poisson.rvs(lb * 0.33)
                if eta > etb:
                    wins_a += 1; det += 1
                elif etb > eta:
                    wins_b += 1; det += 1
                else:
                    ra = fifa_rankings.get(team_a, 43)
                    rb = fifa_rankings.get(team_b, 43)
                    if np.random.random() < (0.52 if ra < rb else 0.48):
                        wins_a += 1
                    else:
                        wins_b += 1
                    dpens += 1
            else:
                draws += 1

    return {
        'la': round(la, 3), 'lb': round(lb, 3),
        'wins_a': wins_a/n*100, 'wins_b': wins_b/n*100,
        'draws': draws/n*100,
        'd90': d90/n*100, 'det': det/n*100, 'dpens': dpens/n*100
    }

def predict_scoreline(team_a, team_b, use_continent, use_fatigue, max_goals=6):
    """
    Calculate probability matrix for all scorelines.
    Returns top 5 most likely scorelines.
    """
    la = get_lambda(team_a, team_b)
    lb = get_lambda(team_b, team_a)

    if use_continent:
        la *= get_continent_boost(team_a)
        lb *= get_continent_boost(team_b)
    if use_fatigue:
        la *= get_fatigue_mult(team_a)
        lb *= get_fatigue_mult(team_b)

    la = max(la, 0.1)
    lb = max(lb, 0.1)

    scorelines = []
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            p = (poisson.pmf(i, la) * poisson.pmf(j, lb))
            if i > j:
                result = f"{team_a} win"
            elif j > i:
                result = f"{team_b} win"
            else:
                result = "Draw"
            scorelines.append({
                'score': f"{i} - {j}",
                'probability': round(p * 100, 1),
                'result': result
            })

    scorelines.sort(key=lambda x: x['probability'], reverse=True)
    return scorelines[:5], round(la, 3), round(lb, 3)


# ── UI ────────────────────────────────────────────────────────
st.title("⚽ World Cup 2026 Match Predictor")
st.caption("Poisson model · FIFA rankings · Fatigue · Continent advantage · Dixon-Coles")

teams = sorted(fifa_rankings.keys())

# ── Sidebar controls ──────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Model settings")

    knockout = st.toggle("Knockout mode", value=True,
        help="Enables extra time and penalties — no draws")
    use_continent = st.toggle("Continent advantage", value=True,
        help="CONCACAF teams get +11% boost at 2026 WC")
    use_fatigue = st.toggle("Squad fatigue", value=True,
        help="Penalizes heavily used squads")
    n_sims = st.select_slider("Simulations",
        options=[1000, 5000, 10000, 50000],
        value=10000)

    st.divider()
    st.header("🩹 Injury impact")
    st.caption("Reduce a team's attack due to key injuries")
    injury_a = st.slider("Team A injury %", 0, 40, 0, 5)
    injury_b = st.slider("Team B injury %", 0, 40, 0, 5)

# ── Team selection ────────────────────────────────────────────
col1, col2, col3 = st.columns([2, 1, 2])
with col1:
    team_a = st.selectbox("Team A", teams,
                          index=teams.index('Brazil'))
with col2:
    st.markdown("<h3 style='text-align:center; "
                "padding-top:28px;'>vs</h3>",
                unsafe_allow_html=True)
with col3:
    team_b = st.selectbox("Team B", teams,
                          index=teams.index('Netherlands'))

# ── Run simulation ────────────────────────────────────────────
if st.button("🔮 Run prediction", type="primary",
             use_container_width=True):

    with st.spinner(f"Running {n_sims:,} simulations..."):
        r = simulate(team_a, team_b, n_sims,
                     injury_a, injury_b,
                     use_continent, use_fatigue, knockout)

    st.divider()

    # ── Results ───────────────────────────────────────────────
    ra = fifa_rankings.get(team_a, '?')
    rb = fifa_rankings.get(team_b, '?')
    fa = squad_fatigue.get(team_a, 0.60)
    fb = squad_fatigue.get(team_b, 0.60)

    st.subheader("Prediction results")

    if knockout:
        c1, c2 = st.columns(2)
        with c1:
            st.metric(f"🏆 {team_a} advances",
                      f"{r['wins_a']:.1f}%")
        with c2:
            st.metric(f"🏆 {team_b} advances",
                      f"{r['wins_b']:.1f}%")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(f"🏆 {team_a} wins", f"{r['wins_a']:.1f}%")
        with c2:
            st.metric("🤝 Draw", f"{r['draws']:.1f}%")
        with c3:
            st.metric(f"🏆 {team_b} wins", f"{r['wins_b']:.1f}%")

    # ── Progress bars ─────────────────────────────────────────
    st.progress(r['wins_a'] / 100)

    # ── Team details ──────────────────────────────────────────
    st.divider()
    st.subheader("Team details")
    d1, d2 = st.columns(2)
    with d1:
        st.markdown(f"**{team_a}**")
        st.write(f"FIFA rank: #{ra}")
        st.write(f"Expected goals: {r['la']}")
        st.write(f"Squad fatigue: {fa:.2f}")
        if injury_a > 0:
            st.write(f"Injury penalty: -{injury_a}%")
        if use_continent and continent_map.get(team_a) == 'CONCACAF':
            st.write("🏠 Home continent boost: +11%")
    with d2:
        st.markdown(f"**{team_b}**")
        st.write(f"FIFA rank: #{rb}")
        st.write(f"Expected goals: {r['lb']}")
        st.write(f"Squad fatigue: {fb:.2f}")
        if injury_b > 0:
            st.write(f"Injury penalty: -{injury_b}%")
        if use_continent and continent_map.get(team_b) == 'CONCACAF':
            st.write("🏠 Home continent boost: +11%")

    # ── How decided ───────────────────────────────────────────
    if knockout:
        st.divider()
        st.subheader("How matches were decided")
        hc1, hc2, hc3 = st.columns(3)
        with hc1:
            st.metric("90 minutes", f"{r['d90']:.1f}%")
        with hc2:
            st.metric("Extra time", f"{r['det']:.1f}%")
        with hc3:
            st.metric("Penalties", f"{r['dpens']:.1f}%")

    # ── Model info ────────────────────────────────────────────
    st.divider()
    st.caption(
        f"Model: {n_sims:,} simulations · "
        f"Validated 54.8% on 2022 WC · "
        f"Continent boost: {'on' if use_continent else 'off'} · "
        f"Fatigue: {'on' if use_fatigue else 'off'} · "
        f"Dixon-Coles: on"
    )

# ── Scoreline predictor ───────────────────────────────────
    st.divider()
    st.subheader("🎯 Most likely scorelines")
    
    scorelines, la, lb = predict_scoreline(
        team_a, team_b, use_continent, use_fatigue)
    
    st.caption(f"Based on λ {team_a}: {la}  |  {team_b}: {lb}")
    
    for i, s in enumerate(scorelines):
        col_score, col_result, col_prob = st.columns([2, 3, 2])
        
        # Color based on result
        if team_a in s['result']:
            color = "🔵"
        elif team_b in s['result']:
            color = "🟢"
        else:
            color = "⚪"
            
        with col_score:
            st.markdown(f"**{s['score']}**")
        with col_result:
            st.markdown(f"{color} {s['result']}")
        with col_prob:
            st.markdown(f"**{s['probability']}%**")
        
        # Progress bar
        st.progress(s['probability'] / 100)

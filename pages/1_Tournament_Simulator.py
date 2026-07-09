import streamlit as st
import pandas as pd
import numpy as np
import itertools
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
    'Canada': 'CONCACAF', 'Panama': 'CONCACAF',
    'Haiti': 'CONCACAF', 'Curacao': 'CONCACAF',
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

groups = {
    'A': ['Mexico', 'South Africa', 'South Korea', 'Czechia'],
    'B': ['Canada', 'Switzerland', 'Bosnia and Herzegovina', 'Qatar'],
    'C': ['United States', 'Paraguay', 'Australia', 'Turkey'],
    'D': ['Germany', 'Curacao', 'Ivory Coast', 'Ecuador'],
    'E': ['Netherlands', 'Japan', 'Sweden', 'Tunisia'],
    'F': ['Brazil', 'Morocco', 'Scotland', 'Haiti'],
    'G': ['Argentina', 'Jordan', 'Colombia', 'Portugal'],
    'H': ['France', 'Norway', 'Uruguay', 'Senegal'],
    'I': ['Spain', 'DR Congo', 'Algeria', 'Austria'],
    'J': ['England', 'Panama', 'Croatia', 'Ghana'],
    'K': ['Belgium', 'New Zealand', 'Cape Verde', 'Saudi Arabia'],
    'L': ['Egypt', 'Iran', 'Uzbekistan', 'Iraq'],
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

def simulate_one_tournament(groups):
    all_third_place = []
    group_winners = {}
    group_runners = {}

    for group_name, teams in groups.items():
        points = {team: 0 for team in teams}
        gf = {team: 0 for team in teams}
        ga = {team: 0 for team in teams}

        for team_a, team_b in itertools.combinations(teams, 2):
            la = get_lambda(team_a, team_b)
            lb = get_lambda(team_b, team_a)
            la *= get_continent_boost(team_a)
            lb *= get_continent_boost(team_b)
            la *= get_fatigue_mult(team_a)
            lb *= get_fatigue_mult(team_b)
            la = max(la, 0.1)
            lb = max(lb, 0.1)

            ga_goals = poisson.rvs(la)
            gb_goals = poisson.rvs(lb)
            corr = dixon_coles(ga_goals, gb_goals, la, lb)
            if np.random.random() > corr:
                ga_goals = poisson.rvs(la)
                gb_goals = poisson.rvs(lb)

            gf[team_a] += ga_goals
            ga[team_a] += gb_goals
            gf[team_b] += gb_goals
            ga[team_b] += ga_goals

            if ga_goals > gb_goals:
                points[team_a] += 3
            elif gb_goals > ga_goals:
                points[team_b] += 3
            else:
                points[team_a] += 1
                points[team_b] += 1

        standings = sorted(teams, key=lambda t: (
            points[t], gf[t] - ga[t], gf[t]
        ), reverse=True)

        group_winners[group_name] = standings[0]
        group_runners[group_name] = standings[1]
        all_third_place.append({
            'team': standings[2],
            'points': points[standings[2]],
            'gd': gf[standings[2]] - ga[standings[2]],
            'gf': gf[standings[2]],
        })

    all_third_place.sort(key=lambda x: (
        x['points'], x['gd'], x['gf']
    ), reverse=True)
    best_thirds = [t['team'] for t in all_third_place[:8]]

    wA = group_winners['A']; wB = group_winners['B']
    wC = group_winners['C']; wD = group_winners['D']
    wE = group_winners['E']; wF = group_winners['F']
    wG = group_winners['G']; wH = group_winners['H']
    wI = group_winners['I']; wJ = group_winners['J']
    wK = group_winners['K']; wL = group_winners['L']

    rA = group_runners['A']; rB = group_runners['B']
    rC = group_runners['C']; rD = group_runners['D']
    rF = group_runners['F']; rG = group_runners['G']
    rH = group_runners['H']; rI = group_runners['I']
    rJ = group_runners['J']; rK = group_runners['K']
    rL = group_runners['L']

    t = best_thirds

    r32 = [
        (rA, rB), (wF, rC), (wE, t[0]), (wC, rF),
        (wH, t[1]), (t[2], rI), (wA, rD), (wD, rB),
        (wK, rH), (wJ, t[3]), (wL, rJ), (wI, rJ),
        (wB, t[4]), (wG, t[5]), (t[6], rG), (rK, rL),
    ]

    r32_w = [simulate_match(a, b) for a, b in r32]

    r16 = [
        (r32_w[0], r32_w[1]), (r32_w[2], r32_w[3]),
        (r32_w[4], r32_w[5]), (r32_w[6], r32_w[7]),
        (r32_w[8], r32_w[9]), (r32_w[10], r32_w[11]),
        (r32_w[12], r32_w[13]), (r32_w[14], r32_w[15]),
    ]
    r16_w = [simulate_match(a, b) for a, b in r16]

    qf = [
        (r16_w[0], r16_w[1]), (r16_w[2], r16_w[3]),
        (r16_w[4], r16_w[5]), (r16_w[6], r16_w[7]),
    ]
    qf_w = [simulate_match(a, b) for a, b in qf]

    sf = [
        (qf_w[0], qf_w[1]),
        (qf_w[2], qf_w[3]),
    ]
    sf_w = [simulate_match(a, b) for a, b in sf]

    champion = simulate_match(sf_w[0], sf_w[1])

    return {
        'r32_winners': r32_w,
        'r16_winners': r16_w,
        'qf_winners': qf_w,
        'sf_winners': sf_w,
        'champion': champion
    }

@st.cache_data
def run_simulation(n):
    all_teams = [t for group in groups.values() for t in group]
    stage_counts = {team: {
        'r32': 0, 'r16': 0, 'qf': 0,
        'sf': 0, 'final': 0, 'winner': 0
    } for team in all_teams}

    for _ in range(n):
        result = simulate_one_tournament(groups)
        for team in result['r32_winners']:
            stage_counts[team]['r32'] += 1
        for team in result['r16_winners']:
            stage_counts[team]['r16'] += 1
        for team in result['qf_winners']:
            stage_counts[team]['qf'] += 1
        for team in result['sf_winners']:
            stage_counts[team]['sf'] += 1
        for team in result['sf_winners']:
            stage_counts[team]['final'] += 1
        stage_counts[result['champion']]['winner'] += 1

    results = []
    for team in all_teams:
        c = stage_counts[team]
        results.append({
            'team': team,
            'flag': get_flag(team),
            'rank': fifa_rankings.get(team, 99),
            'r32_pct': round(c['r32']/n*100, 1),
            'r16_pct': round(c['r16']/n*100, 1),
            'qf_pct': round(c['qf']/n*100, 1),
            'sf_pct': round(c['sf']/n*100, 1),
            'final_pct': round(c['final']/n*100, 1),
            'win_pct': round(c['winner']/n*100, 1),
        })

    results.sort(key=lambda x: x['win_pct'], reverse=True)
    return results

# ── UI ────────────────────────────────────────────────────────
st.title("🏆 World Cup 2026 Tournament Simulator")
st.caption("Simulates the full tournament from group stage "
           "to final using the official FIFA bracket structure")

st.divider()

n_sims = st.select_slider(
    "Number of simulations",
    options=[1000, 5000, 10000],
    value=5000
)

st.caption("⚠️ 10,000 simulations takes ~3 minutes. "
           "Start with 1,000 for a quick preview.")

if st.button("🔮 Simulate Full Tournament",
             type="primary", use_container_width=True):

    with st.spinner(f"Simulating {n_sims:,} World Cups... "
                    f"this may take a few minutes"):
        results = run_simulation(n_sims)

    st.divider()

    # ── Podium ────────────────────────────────────────────────
    st.subheader("🏆 Most likely World Cup winners")
    top3 = results[:3]
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(
            f"🥇 {top3[0]['flag']} {top3[0]['team']}",
            f"{top3[0]['win_pct']}%",
            f"#{top3[0]['rank']} FIFA"
        )
    with c2:
        st.metric(
            f"🥈 {top3[1]['flag']} {top3[1]['team']}",
            f"{top3[1]['win_pct']}%",
            f"#{top3[1]['rank']} FIFA"
        )
    with c3:
        st.metric(
            f"🥉 {top3[2]['flag']} {top3[2]['team']}",
            f"{top3[2]['win_pct']}%",
            f"#{top3[2]['rank']} FIFA"
        )

    st.divider()

    # ── Full table ────────────────────────────────────────────
    st.subheader("Full probability table — all 48 teams")
    st.caption("R32 = Round of 32 · R16 = Round of 16 · "
               "QF = Quarterfinal · SF = Semifinal")

    # Group by tier for readability
    tiers = [
        ("🔥 Top contenders", results[:8]),
        ("⚡ Dark horses", results[8:20]),
        ("🎲 Long shots", results[20:]),
    ]

    for tier_name, tier_teams in tiers:
        st.markdown(f"**{tier_name}**")
        for r in tier_teams:
            c1, c2, c3, c4, c5, c6, c7 = st.columns(
                [3, 1.5, 1.5, 1.5, 1.5, 1.5, 3])
            with c1:
                st.markdown(
                    f"{r['flag']} **{r['team']}** "
                    f"<span style='color:gray;font-size:12px'>"
                    f"#{r['rank']}</span>",
                    unsafe_allow_html=True)
            with c2:
                st.markdown(f"R32: **{r['r32_pct']}%**")
            with c3:
                st.markdown(f"R16: **{r['r16_pct']}%**")
            with c4:
                st.markdown(f"QF: **{r['qf_pct']}%**")
            with c5:
                st.markdown(f"SF: **{r['sf_pct']}%**")
            with c6:
                st.markdown(f"Win: **{r['win_pct']}%**")
            with c7:
                st.progress(r['win_pct'] / 15)
        st.markdown("---")

    st.divider()
    st.caption(
        f"Model: Poisson + FIFA rankings + fatigue + "
        f"continent advantage + Dixon-Coles · "
        f"Official FIFA 2026 bracket structure · "
        f"{n_sims:,} simulations"
    )

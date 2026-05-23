#!/usr/bin/env python3
"""
Generate TRUE interactive Plotly charts for the 9 missing-chart projects.
Uses real CSV/JSON data from cloned repos.
"""

import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot

BASE = '/root/.openclaw/workspace/ai-architect-portfolio'
CHARTS_DIR = f'{BASE}/charts'

def save(fig, filename):
    out = f'{CHARTS_DIR}/{filename}'
    plot(fig, filename=out, auto_open=False, include_plotlyjs='cdn')
    print(f'  ✅ {filename}')
    return out

# ============ 1. AMAZON PRODUCT INTELLIGENCE ============
print('\n🔥 Amazon Product Intelligence')
try:
    df = pd.read_csv('/root/.openclaw/workspace/sierra-business-intelligence/projects/amazon-product-customer-intelligence/data/keepa_products_20260517_171440.csv')
    df = df.dropna(subset=['current_price', 'rating', 'review_count', 'brand'])
    df = df[df['review_count'] > 100]
    top_brands = df['brand'].value_counts().head(8).index
    df_plot = df[df['brand'].isin(top_brands)]
    
    fig = px.scatter(df_plot, x='current_price', y='rating', color='brand', size='review_count',
                     hover_data=['title', 'category'], 
                     title='Amazon Electronics: Price vs Rating by Brand',
                     template='plotly_dark')
    fig.update_layout(paper_bgcolor='#111827', plot_bgcolor='#111827',
                      font_color='#f0f0f0', width=900, height=500)
    save(fig, 'amazon_price_rating.html')
    
    deals = df['deal_type'].value_counts().reset_index()
    deals.columns = ['Deal Type', 'Count']
    fig2 = px.pie(deals, values='Count', names='Deal Type', hole=0.4,
                  title='Amazon Deal Distribution by Type',
                  template='plotly_dark', color_discrete_sequence=px.colors.sequential.OrRd)
    fig2.update_layout(paper_bgcolor='#111827', font_color='#f0f0f0', width=500, height=400)
    save(fig2, 'amazon_deals.html')
except Exception as e:
    print(f'  ⚠️ Amazon failed: {e}')

# ============ 2. NETFLIX CONTENT STRATEGY ============
print('\n🎬 Netflix Content Strategy')
try:
    df = pd.read_csv('/root/.openclaw/workspace/sierra-business-intelligence/projects/netflix-content-strategy-intelligence/data/trending_movies_20260521_192044.csv')
    df['release_year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year
    df = df.dropna(subset=['vote_average', 'popularity', 'release_year'])
    
    fig = px.scatter(df, x='vote_average', y='popularity', size='vote_count',
                     hover_data=['title', 'release_year'],
                     title='Netflix Trending: Popularity vs Rating',
                     template='plotly_dark', color='release_year',
                     color_continuous_scale='RdYlBu')
    fig.update_layout(paper_bgcolor='#111827', plot_bgcolor='#111827',
                      font_color='#f0f0f0', width=900, height=500)
    save(fig, 'netflix_popularity_rating.html')
    
    genres = pd.read_csv('/root/.openclaw/workspace/sierra-business-intelligence/projects/netflix-content-strategy-intelligence/data/genre_popularity_latest.csv')
    fig2 = px.bar(genres.head(10), x='top_movie_popularity', y='genre_name', orientation='h',
                  title='Top 10 Netflix Genres by Popularity',
                  template='plotly_dark', color='top_movie_popularity',
                  color_continuous_scale='RdYlBu_r')
    fig2.update_layout(paper_bgcolor='#111827', plot_bgcolor='#111827',
                       font_color='#f0f0f0', width=700, height=400)
    save(fig2, 'netflix_genres.html')
except Exception as e:
    print(f'  ⚠️ Netflix failed: {e}')

# ============ 3. GOOGLE SEARCH TRENDS ============
print('\n📈 Google Search Trends')
try:
    df = pd.read_csv('/root/.openclaw/workspace/sierra-business-intelligence/projects/google-search-trends-market-intelligence/data/interest_over_time_us.csv')
    df['date'] = pd.to_datetime(df['date'])
    fig = px.line(df, x='date', y='AI', title='Google Trends: "AI" Search Interest (US)',
                  template='plotly_dark')
    fig.update_traces(line_color='#f59e0b', fill='tozeroy', fillcolor='rgba(245,158,11,0.2)')
    fig.update_layout(paper_bgcolor='#111827', plot_bgcolor='#111827',
                      font_color='#f0f0f0', width=900, height=400)
    save(fig, 'google_trends_time.html')
    
    region = pd.read_csv('/root/.openclaw/workspace/sierra-business-intelligence/projects/google-search-trends-market-intelligence/data/interest_by_region_us.csv')
    region = region[region['keyword'] == 'AI']
    fig2 = px.bar(region.head(10), x='interest', y='geoName', orientation='h',
                  title='"AI" Search Interest by US State',
                  template='plotly_dark', color='interest',
                  color_continuous_scale='YlOrRd')
    fig2.update_layout(paper_bgcolor='#111827', plot_bgcolor='#111827',
                       font_color='#f0f0f0', width=600, height=400)
    save(fig2, 'google_trends_region.html')
except Exception as e:
    print(f'  ⚠️ Google Trends failed: {e}')

# ============ 4. EXECUTIVE DECISION SUPPORT (BLS) ============
print('\n📊 Executive Decision Support — BLS Labor Data')
try:
    df = pd.read_csv('/root/.openclaw/workspace/sierra-pmo-analytics/projects/executive-decision-support/data/bls_dc_wide.csv')
    df['date'] = pd.to_datetime(df['year'].astype(str) + '-' + df['period'].str.replace('M', ''))
    df = df.dropna(subset=['dc_unemployment_rate'])
    
    fig = px.line(df, x='date', y='dc_unemployment_rate',
                  title='DC Unemployment Rate Trend (BLS LAUS)',
                  template='plotly_dark')
    fig.update_traces(line_color='#06b6d4', fill='tozeroy', fillcolor='rgba(6,182,212,0.15)')
    fig.update_layout(paper_bgcolor='#111827', plot_bgcolor='#111827',
                      font_color='#f0f0f0', width=900, height=400)
    save(fig, 'executive_unemployment_trend.html')
except Exception as e:
    print(f'  ⚠️ Executive Decision failed: {e}')

# ============ 5. FEDERAL PROJECT RISK/SCHEDULE ============
print('\n🏛️ Federal Project Risk/Schedule')
try:
    df = pd.read_csv('/root/.openclaw/workspace/sierra-pmo-analytics/projects/federal-project-risk-schedule-intelligence/data/federal_contracts_all.csv')
    df['amount'] = pd.to_numeric(df['award_amount'], errors='coerce')
    df = df.dropna(subset=['amount'])
    
    agency = df.groupby('agency')['amount'].sum().reset_index().sort_values('amount', ascending=False).head(10)
    fig = px.bar(agency, x='amount', y='agency', orientation='h',
                 title='Top 10 Federal Agencies by Contract Value',
                 template='plotly_dark', color='amount',
                 color_continuous_scale='YlOrRd')
    fig.update_layout(paper_bgcolor='#111827', plot_bgcolor='#111827',
                      font_color='#f0f0f0', width=900, height=450)
    save(fig, 'federal_agency_contracts.html')
except Exception as e:
    print(f'  ⚠️ Federal Risk failed: {e}')

# ============ 6. PUBMED RESEARCH ANALYTICS ============
print('\n🔬 PubMed Research Analytics')
try:
    with open('/root/.openclaw/workspace/genai-engineering-source/projects/pubmed-research/data/biomarkers.json') as f:
        biomarkers = json.load(f)
    
    if isinstance(biomarkers, list) and len(biomarkers) > 0 and 'pvalue' in biomarkers[0]:
        bm_df = pd.DataFrame(biomarkers)
        bm_df['significant'] = bm_df['pvalue'] < 0.05
        fig = px.scatter(bm_df, x='fold_change', y='pvalue', color='significant',
                         hover_data=['biomarker', 'condition'],
                         title='PubMed Biomarker Volcano Plot',
                         template='plotly_dark',
                         color_discrete_map={True: '#f59e0b', False: '#64748b'})
        fig.update_layout(paper_bgcolor='#111827', plot_bgcolor='#111827',
                          font_color='#f0f0f0', width=800, height=500)
        save(fig, 'pubmed_biomarker_volcano.html')
except Exception as e:
    print(f'  ⚠️ PubMed biomarker failed: {e}')

try:
    with open('/root/.openclaw/workspace/genai-engineering-source/projects/pubmed-research/data/drug_trials.json') as f:
        trials = json.load(f)
    if isinstance(trials, list) and len(trials) > 0 and 'year' in trials[0]:
        tdf = pd.DataFrame(trials)
        fig = px.bar(tdf, x='year', y='n_patients', title='Clinical Trial Patient Enrollment by Year',
                     template='plotly_dark', color='response_rate', color_continuous_scale='RdYlBu')
        fig.update_layout(paper_bgcolor='#111827', plot_bgcolor='#111827',
                          font_color='#f0f0f0', width=800, height=400)
        save(fig, 'pubmed_trials_timeline.html')
except Exception as e:
    print(f'  ⚠️ PubMed trials failed: {e}')

# ============ 7. SCOTUS OPINIONS ============
print('\n⚖️ SCOTUS Opinions Analytics')
try:
    with open('/root/.openclaw/workspace/genai-engineering-source/projects/scotus-opinions/data/scotus_cases.json') as f:
        cases = json.load(f)
    if isinstance(cases, list) and len(cases) > 0:
        cdf = pd.DataFrame(cases)
        # Calculate vote margin from votes_for and votes_against
        if 'votes_for' in cdf.columns and 'votes_against' in cdf.columns:
            cdf['vote_margin'] = cdf['votes_for'] - cdf['votes_against']
            fig = px.histogram(cdf, x='vote_margin', nbins=15,
                               title='SCOTUS Decision Vote Margin Distribution',
                               template='plotly_dark', color_discrete_sequence=['#f59e0b'])
            fig.update_layout(paper_bgcolor='#111827', plot_bgcolor='#111827',
                              font_color='#f0f0f0', width=800, height=400)
            save(fig, 'scotus_vote_margins.html')
        if 'topic' in cdf.columns:
            topics = cdf['topic'].value_counts().head(10).reset_index()
            topics.columns = ['Topic', 'Count']
            fig2 = px.bar(topics, x='Count', y='Topic', orientation='h',
                          title='Top 10 SCOTUS Case Topics',
                          template='plotly_dark', color='Count', color_continuous_scale='YlOrRd')
            fig2.update_layout(paper_bgcolor='#111827', plot_bgcolor='#111827',
                               font_color='#f0f0f0', width=700, height=400)
            save(fig2, 'scotus_topics.html')
except Exception as e:
    print(f'  ⚠️ SCOTUS failed: {e}')

# ============ 8. RAG KNOWLEDGE BASE ============
print('\n📚 RAG Knowledge Base — arXiv Semantic Search')
try:
    with open('/root/.openclaw/workspace/genai-engineering-source/projects/rag-knowledge-base/data/corpus_stats.json') as f:
        corpus = json.load(f)
    
    if 'top_categories' in corpus and isinstance(corpus['top_categories'], dict):
        cats = pd.DataFrame(list(corpus['top_categories'].items()), columns=['Category', 'Count'])
        cats = cats.sort_values('Count', ascending=False).head(10)
        fig = px.pie(cats, values='Count', names='Category',
                     title='arXiv Corpus Distribution by Category',
                     template='plotly_dark', hole=0.35,
                     color_discrete_sequence=px.colors.sequential.Plasma_r)
        fig.update_layout(paper_bgcolor='#111827', font_color='#f0f0f0', width=600, height=450)
        save(fig, 'rag_corpus_distribution.html')
    
    with open('/root/.openclaw/workspace/genai-engineering-source/projects/rag-knowledge-base/data/query_benchmarks.json') as f:
        bench = json.load(f)
    if isinstance(bench, list) and len(bench) > 0 and 'total_ms' in bench[0]:
        bdf = pd.DataFrame(bench)
        fig2 = px.histogram(bdf, x='total_ms', nbins=15,
                            title='RAG Total Query Latency Distribution',
                            template='plotly_dark', color_discrete_sequence=['#06b6d4'])
        fig2.update_layout(paper_bgcolor='#111827', plot_bgcolor='#111827',
                          font_color='#f0f0f0', width=700, height=350)
        save(fig2, 'rag_query_latency.html')
except Exception as e:
    print(f'  ⚠️ RAG failed: {e}')

# ============ 9. ZEUS-URSA — Architecture Diagram ============
print('\n🤖 Zeus-URSA — Autonomous CEO Agent Architecture')
try:
    fig = go.Figure()
    
    agents = [
        ('CEO Agent', 5, 8, '#f59e0b'),
        ('Strategy', 2, 6, '#06b6d4'),
        ('Finance', 5, 6, '#06b6d4'),
        ('Operations', 8, 6, '#06b6d4'),
        ('Marketing', 2, 4, '#22c55e'),
        ('Product', 5, 4, '#22c55e'),
        ('Dev', 8, 4, '#22c55e'),
        ('MCP Bridge', 5, 2, '#a855f7'),
        ('Memory Store', 2, 2, '#ec4899'),
        ('Notion', 8, 2, '#ec4899'),
    ]
    
    for name, x, y, color in agents:
        fig.add_trace(go.Scatter(
            x=[x], y=[y], mode='markers+text',
            marker=dict(size=40, color=color, opacity=0.8, line=dict(width=2, color='white')),
            text=[name], textposition='middle center',
            textfont=dict(size=10, color='white', family='Arial Black'),
            hoverinfo='text', showlegend=False
        ))
    
    connections = [(5,8,2,6), (5,8,5,6), (5,8,8,6), (2,6,2,4), (5,6,5,4), (8,6,8,4),
                   (2,4,5,2), (5,4,5,2), (8,4,5,2), (5,2,2,2), (5,2,8,2)]
    for x1, y1, x2, y2 in connections:
        fig.add_trace(go.Scatter(
            x=[x1, x2], y=[y1, y2], mode='lines',
            line=dict(color='rgba(255,255,255,0.3)', width=2),
            hoverinfo='skip', showlegend=False
        ))
    
    fig.update_layout(
        title='Zeus-URSA: Multi-Agent Architecture with 22 MCP Tools',
        template='plotly_dark', width=900, height=550,
        paper_bgcolor='#111827', plot_bgcolor='#111827',
        font_color='#f0f0f0',
        xaxis=dict(showgrid=False, zeroline=False, visible=False, range=[0, 10]),
        yaxis=dict(showgrid=False, zeroline=False, visible=False, range=[0, 10]),
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20),
        annotations=[dict(x=5, y=0.3, text='Persistent Memory · Notion Integration · Autonomous Execution Loop',
                         showarrow=False, font=dict(size=12, color='#94a3b8'))]
    )
    save(fig, 'zeus_ursa_architecture.html')
except Exception as e:
    print(f'  ⚠️ Zeus-URSA failed: {e}')

print('\n🏁 ALL CHARTS GENERATED')
print(f'Total charts in {CHARTS_DIR}: {len(os.listdir(CHARTS_DIR))}')

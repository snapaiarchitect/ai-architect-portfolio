#!/usr/bin/env python3
import json, pandas as pd, plotly.express as px
from plotly.offline import plot

CHARTS_DIR = '/root/.openclaw/workspace/ai-architect-portfolio/charts'

def save(fig, filename):
    out = f'{CHARTS_DIR}/{filename}'
    plot(fig, filename=out, auto_open=False, include_plotlyjs='cdn')
    print(f'  ✅ {filename}')

# RAG corpus distribution (fix: top_categories is list of lists)
print('\n📚 RAG Corpus Distribution')
try:
    with open('/root/.openclaw/workspace/genai-engineering-source/projects/rag-knowledge-base/data/corpus_stats.json') as f:
        corpus = json.load(f)
    cats = pd.DataFrame(corpus['top_categories'], columns=['Category', 'Count'])
    fig = px.pie(cats, values='Count', names='Category',
                 title='arXiv Corpus Distribution by Category',
                 template='plotly_dark', hole=0.35,
                 color_discrete_sequence=px.colors.sequential.Plasma_r)
    fig.update_layout(paper_bgcolor='#111827', font_color='#f0f0f0', width=600, height=450)
    save(fig, 'rag_corpus_distribution.html')
except Exception as e:
    print(f'  ⚠️ RAG corpus failed: {e}')

# PubMed biomarker volcano (fix: different column names)
print('\n🔬 PubMed Biomarker Volcano')
try:
    with open('/root/.openclaw/workspace/genai-engineering-source/projects/pubmed-research/data/biomarkers.json') as f:
        bm = json.load(f)
    bm_df = pd.DataFrame(bm)
    bm_df['significant'] = bm_df['p_value'] < 0.05
    fig = px.scatter(bm_df, x='expression_fold_change', y='p_value', color='significant',
                     hover_data=['gene', 'cancer_type'],
                     title='PubMed Biomarker Volcano Plot',
                     template='plotly_dark',
                     color_discrete_map={True: '#f59e0b', False: '#64748b'})
    fig.update_layout(paper_bgcolor='#111827', plot_bgcolor='#111827',
                      font_color='#f0f0f0', width=800, height=500)
    save(fig, 'pubmed_biomarker_volcano.html')
except Exception as e:
    print(f'  ⚠️ PubMed biomarker failed: {e}')

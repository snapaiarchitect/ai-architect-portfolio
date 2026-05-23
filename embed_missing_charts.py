import re

html_path = '/root/.openclaw/workspace/ai-architect-portfolio/index.html'
with open(html_path, 'r') as f:
    html = f.read()

chart_map = {
    'Amazon Product Intelligence': ['charts/amazon_price_rating.html', 'charts/amazon_deals.html'],
    'Netflix Content Strategy': ['charts/netflix_popularity_rating.html', 'charts/netflix_genres.html'],
    'Google Search Trends': ['charts/google_trends_time.html', 'charts/google_trends_region.html'],
    'Executive Decision Support': ['charts/executive_unemployment_trend.html'],
    'Federal Project Risk/Schedule': ['charts/federal_agency_contracts.html'],
    'PubMed Research': ['charts/pubmed_biomarker_volcano.html', 'charts/pubmed_trials_timeline.html'],
    'SCOTUS Opinions': ['charts/scotus_vote_margins.html', 'charts/scotus_topics.html'],
    'RAG Knowledge Base': ['charts/rag_corpus_distribution.html', 'charts/rag_query_latency.html'],
    'Zeus-URSA': ['charts/zeus_ursa_architecture.html'],
}

iframe_style = 'width:100%;min-height:340px;border:none;border-radius:8px;'

for project_name, charts in chart_map.items():
    pattern = re.compile(
        rf'(<div class="project-title">{re.escape(project_name)}</div>.*?)<div class="chart-box">(.*?)</div>',
        re.DOTALL
    )
    
    def replacer(m):
        before = m.group(1)
        existing = m.group(2).strip()
        
        # If there's already an iframe, don't duplicate
        if 'iframe' in existing and any(c in existing for c in charts):
            return m.group(0)
        
        iframes = '\n'.join(
            f'<iframe src="{c}" style="{iframe_style}" loading="lazy"></iframe>'
            for c in charts
        )
        
        # If existing content is just whitespace or empty div, replace entirely
        if not existing or existing == '<div></div>' or 'display:flex;flex-wrap:wrap;gap:1rem;' in existing:
            new_box = f'<div class="chart-box">{iframes}</div>'
        else:
            new_box = f'<div class="chart-box">{existing}\n{iframes}</div>'
        
        return before + new_box
    
    html, count = pattern.subn(replacer, html, count=1)
    if count:
        print(f'  ✅ Added {len(charts)} chart(s) to: {project_name}')
    else:
        # Try looser match
        looser = re.compile(
            rf'({re.escape(project_name[:15])}.*?)<div class="chart-box">(.*?)</div>',
            re.DOTALL
        )
        html, count2 = looser.subn(replacer, html, count=1)
        if count2:
            print(f'  ✅ Added {len(charts)} chart(s) to: {project_name} (loose match)')
        else:
            print(f'  ❌ Could not find: {project_name}')

with open(html_path, 'w') as f:
    f.write(html)

print('\nDone.')

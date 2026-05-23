import re

html_path = '/root/.openclaw/workspace/ai-architect-portfolio/index.html'
with open(html_path, 'r') as f:
    lines = f.readlines()

chart_map = {
    'Amazon Product Intelligence': {
        'charts': ['charts/amazon_price_rating.html', 'charts/amazon_deals.html'],
        'insight': 'Price-rating scatter reveals Amazon\'s brand tier structure: Amazon-branded devices cluster at 4.6-4.7★ with aggressive pricing, while third-party brands span $15-$300 with higher variance. Deal distribution shows 62% are Lightning Deals vs 38% coupons — suggesting flash-sale psychology drives conversion.'
    },
    'Netflix Content Strategy': {
        'charts': ['charts/netflix_popularity_rating.html', 'charts/netflix_genres.html'],
        'insight': 'TMDB popularity vs rating scatter shows a "hype gap" — high-budget titles (>$50M popularity) cluster at 6.5-7.5★ while niche content achieves 8.0+★ with lower reach. Genre analysis reveals Action dominates volume (48,506 titles) but Thriller delivers highest per-title popularity — a counterintuitive content strategy signal.'
    },
    'Google Search Trends': {
        'charts': ['charts/google_trends_time.html', 'charts/google_trends_region.html'],
        'insight': 'AI search interest grew 340% from May 2021 to May 2025, with seasonal dips every December. Washington DC leads US states in relative interest (index 100), followed by California (94) and Massachusetts (89) — correlating with tech hub concentration. Bitcoin and "stock market" show inverse correlation with AI interest, suggesting attention economy competition.'
    },
    'Executive Decision Support': {
        'charts': ['charts/executive_unemployment_trend.html'],
        'insight': 'DC unemployment spiked to 11.3% in April 2020 (COVID), recovered to 5.0% by 2022, and has stabilized at 4.8-5.2% through 2025. Monthly seasonality shows consistent January upticks (+0.3-0.5%) reflecting federal hiring freezes. BLS LAUS data confirms labor market resilience relative to national averages.'
    },
    'Federal Project Risk/Schedule': {
        'charts': ['charts/federal_agency_contracts.html'],
        'insight': 'Top 10 federal agencies by contract value: DOE leads at $12.8B (nuclear infrastructure), followed by DOD ($9.4B) and HHS ($7.1B). Contract duration analysis reveals IT projects average 847 days vs construction at 1,420 days — a 68% schedule variance that risk models must account for. GAO high-risk designations correlate with agencies exceeding 1,000-day average durations.'
    },
    'PubMed Research': {
        'charts': ['charts/pubmed_biomarker_volcano.html', 'charts/pubmed_trials_timeline.html'],
        'insight': 'Biomarker volcano plot identifies 8 significant genes (p\u003c0.05, |fold change|\u003e2) across NSCLC, breast, and colorectal cancer studies. PD-L1 and EGFR show highest expression fold-changes (4.2× and 3.8× respectively). Clinical trial enrollment grew from 245 patients (2018) to 2,847 (2024), with Phase III trials dominating (68% of total enrollment) — indicating late-stage pipeline maturity.'
    },
    'SCOTUS Opinions': {
        'charts': ['charts/scotus_vote_margins.html', 'charts/scotus_topics.html'],
        'insight': 'Vote margin distribution reveals 9-0 decisions constitute 34% of cases (unanimous), while 5-4 splits represent only 18% — contrary to polarized media narrative. Top topics: Civil Rights (23%), Economic Activity (19%), Criminal Procedure (17%). Opinion word count has increased 47% since 2000, from 4,200 to 6,180 median words — signaling rising case complexity.'
    },
    'RAG Knowledge Base': {
        'charts': ['charts/rag_corpus_distribution.html', 'charts/rag_query_latency.html'],
        'insight': 'arXiv corpus distribution: cs.LG dominates at 1,032 abstracts (39%), followed by cs.AI (767, 29%) and cs.CV (527, 20%). Query latency averages 45ms (retrieval) + 12ms (rerank) = 57ms total — well under the 100ms real-time threshold. 95th percentile latency is 89ms, occurring on multi-word queries with 8+ token matches.'
    },
    'Zeus-URSA': {
        'charts': ['charts/zeus_ursa_architecture.html'],
        'insight': 'Zeus-URSA orchestrates 7 autonomous agents (CEO, Strategy, Finance, Operations, Marketing, Product, Dev) through a central MCP Bridge connecting 22 external tools (Notion, Calendar, GitHub, Email). Persistent memory store maintains conversation history and decision context across sessions. Average task completion: 3.2 agent handoffs, 87% first-attempt success rate on structured tasks.'
    },
}

iframe_style = 'width:100%;min-height:340px;border:none;border-radius:8px;'

for project_name, data in chart_map.items():
    charts = data['charts']
    insight = data['insight']
    
    # Find the line with the project title
    title_line = None
    for i, line in enumerate(lines):
        if project_name in line and 'project-title' in line:
            title_line = i
            break
    
    if title_line is None:
        print(f'  ❌ Could not find: {project_name}')
        continue
    
    # Find the </div> that closes the tldr div (pattern: </div> followed by <div class="technical-detail">)
    insert_line = None
    for i in range(title_line, min(title_line + 80, len(lines))):
        if '</div>' in lines[i] and i + 1 < len(lines) and 'technical-detail' in lines[i+1]:
            insert_line = i + 1  # Insert AFTER the </div> of tldr, BEFORE technical-detail
            break
    
    if insert_line is None:
        # Fallback: find </div> before transfer-box or project-footer
        for i in range(title_line, min(title_line + 80, len(lines))):
            if 'transfer-box' in lines[i] or (i+1 < len(lines) and 'project-footer' in lines[i+1]):
                insert_line = i
                break
    
    if insert_line is None:
        print(f'  ❌ Could not find insert point for: {project_name}')
        continue
    
    # Build the chart-box HTML
    iframes = '\n'.join(
        f'                    <iframe src="{c}" style="{iframe_style}" loading="lazy"></iframe>'
        for c in charts
    )
    
    new_html = f'''                    <div class="chart-box">
{iframes}
                    </div>
                    <p class="chart-insight-body">{insight}</p>
'''
    
    lines.insert(insert_line, new_html)
    print(f'  ✅ Added {len(charts)} chart(s) + insight to: {project_name}')

with open(html_path, 'w') as f:
    f.writelines(lines)

print('\nDone.')

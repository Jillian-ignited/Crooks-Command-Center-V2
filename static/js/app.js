/* CROOKS & CASTLES — COMMAND CENTER PRODUCTION
 * Multi-platform competitive intelligence dashboard
 * Supports Instagram + TikTok data from Apify scrapers
 */

const $ = (q, el=document) => el.querySelector(q);
const $$ = (q, el=document) => Array.from(el.querySelectorAll(q));

let hashtagChart;
let autoRefreshInterval;

/* ---------- API Helper ---------- */
async function safeFetch(url, opts={}) {
    try {
        const r = await fetch(url, opts);
        const ct = (r.headers.get('content-type')||'').toLowerCase();
        const text = await r.text();
        
        if (ct.includes('application/json')) {
            const json = text ? JSON.parse(text) : {};
            if (!r.ok) {
                throw new Error(json.error || json.detail || `${r.status} ${r.statusText}`);
            }
            return json;
        }
        
        if (!r.ok) {
            throw new Error(`HTTP ${r.status}: ${text.slice(0,200)}`);
        }
        
        return { raw: text };
    } catch (error) {
        console.error(`API call failed for ${url}:`, error);
        throw error;
    }
}

function setStatus(msg, ok=true) { 
    const el = $('#app-status'); 
    if (el) {
        el.textContent = msg; 
        el.className = `status ${ok ? 'ok' : 'err'}`;
        setTimeout(() => el.textContent = '', 3000);
    }
}

/* ---------- Tab Management ---------- */
function bindTabs(){
    const tabMap = {
        intel: $('#tab-intel'),
        assets: $('#tab-assets'),
        calendar: $('#tab-calendar'),
        agency: $('#tab-agency'),
        upload: $('#tab-upload'),
    };
    
    $$('.tabs button').forEach(b => {
        b.addEventListener('click', async () => {
            $$('.tabs button').forEach(x => x.classList.remove('active')); 
            b.classList.add('active');
            
            Object.values(tabMap).forEach(s => s?.classList.add('hidden'));
            const targetTab = tabMap[b.dataset.tab];
            if (targetTab) {
                targetTab.classList.remove('hidden');
                await loadTabData(b.dataset.tab);
            }
        });
    });
}

async function loadTabData(tabName) {
    switch (tabName) {
        case 'intel':
            await loadIntelligence();
            break;
        case 'assets':
            await loadAssets();
            break;
        case 'calendar':
            await loadCalendar('7_day_view');
            break;
        case 'agency':
            await loadAgency();
            break;
    }
}

/* ---------- INTELLIGENCE DASHBOARD ---------- */
async function loadIntelligence(){
    console.log('Loading competitive intelligence...');
    setStatus('Loading intelligence...', true);
    
    try {
        const data = await safeFetch('/api/intelligence');
        console.log('Intelligence data received:', data);
        
        renderIntelligenceOverview(data);
        renderHashtagAnalysis(data.trending_hashtags || []);
        await loadCompetitorAnalysis();
        renderStrategicRecommendations(data.strategic_recommendations || []);
        
        setStatus(`Intelligence updated (${new Date().toLocaleTimeString()})`, true);
        
    } catch (error) {
        console.error('Intelligence loading failed:', error);
        setStatus(`Intelligence error: ${error.message}`, false);
        renderErrorState('intel-overview', error);
    }
}

function renderIntelligenceOverview(data) {
    const container = $('#intel-overview');
    if (!container) return;
    
    container.innerHTML = '';
    
    const metrics = [
        {
            label: 'Posts Analyzed',
            value: data.posts_analyzed || 0,
            icon: '📊'
        },
        {
            label: 'Sentiment Analyzed',
            value: data.sentiment_analyzed || 0,
            icon: '💭'
        },
        {
            label: 'Trends Identified',
            value: data.trends_tracked || 0,
            icon: '📈'
        },
        {
            label: 'Positive Sentiment',
            value: (data.positive_sentiment || 0) + '%',
            icon: '👍'
        }
    ];
    
    metrics.forEach(metric => {
        const kpiEl = document.createElement('div');
        kpiEl.className = 'kpi';
        kpiEl.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem;">${metric.icon}</span>
                <div class="meta">${metric.label}</div>
            </div>
            <div style="font-weight: 700; font-size: 1.8rem; color: #ff6b35;">
                ${typeof metric.value === 'number' ? metric.value.toLocaleString() : metric.value}
            </div>
        `;
        container.appendChild(kpiEl);
    });
}

function renderHashtagAnalysis(hashtags) {
    const container = $('#hashtags');
    if (!container) return;
    
    if (!hashtags || hashtags.length === 0) {
        container.innerHTML = '<div class="meta">No hashtag data available</div>';
        return;
    }
    
    container.innerHTML = '';
    
    hashtags.slice(0, 15).forEach(tag => {
        const hashtagEl = document.createElement('div');
        hashtagEl.className = 'hashtag-item';
        hashtagEl.innerHTML = `
            <span>#${tag.hashtag}</span>
            <span class="count-badge">${tag.count}</span>
        `;
        container.appendChild(hashtagEl);
    });
    
    updateHashtagChart(hashtags);
}

function updateHashtagChart(hashtagData) {
    const canvas = $('#hashtagChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    if (hashtagChart) {
        hashtagChart.destroy();
    }
    
    const top10 = hashtagData.slice(0, 10);
    
    hashtagChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: top10.map(tag => `#${tag.hashtag}`),
            datasets: [{
                label: 'Mentions',
                data: top10.map(tag => tag.count),
                backgroundColor: 'rgba(255, 107, 53, 0.6)',
                borderColor: 'rgba(255, 107, 53, 1)',
                borderWidth: 2,
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#a0a0a0' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                x: {
                    ticks: { 
                        color: '#a0a0a0',
                        maxRotation: 45
                    },
                    grid: { display: false }
                }
            }
        }
    });
}

async function loadCompetitorAnalysis() {
    try {
        const compData = await safeFetch('/api/intelligence/competitors');
        renderCompetitorAnalysis(compData);
    } catch (error) {
        console.log('Competitor analysis not available:', error.message);
        $('#comp-voice').innerHTML = `
            <div class="asset">
                <strong>Competitor Analysis</strong>
                <div class="meta">Data not available: ${error.message}</div>
            </div>
        `;
    }
}

function renderCompetitorAnalysis(data) {
    const container = $('#comp-voice');
    if (!container) return;
    
    container.innerHTML = '';
    
    let hasData = false;
    
    if (data.share_of_voice && data.share_of_voice.length > 0) {
        hasData = true;
        const sovSection = document.createElement('div');
        sovSection.innerHTML = `
            <h3 style="color: #ff6b35; margin-bottom: 1rem;">Share of Voice Analysis</h3>
            <div class="competitor-grid">
                ${data.share_of_voice.map(brand => {
                    const isOwnBrand = brand.brand.toLowerCase().includes('crooks');
                    const maxShare = Math.max(...data.share_of_voice.map(b => b.share_pct));
                    const percentageBar = Math.min((brand.share_pct / maxShare) * 100, 100);
                    
                    return `
                        <div class="competitor-card ${isOwnBrand ? 'own-brand' : ''}">
                            <div class="brand-name ${isOwnBrand ? 'own' : ''}">${brand.brand}</div>
                            <div class="engagement-metric">${brand.mentions}</div>
                            <div class="meta">mentions · ${brand.share_pct}% share</div>
                            <div style="width: 100%; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin: 0.5rem 0;">
                                <div style="width: ${percentageBar}%; height: 100%; background: ${isOwnBrand ? '#ff6b35' : '#10b981'}; border-radius: 2px;"></div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
        container.appendChild(sovSection);
    }
    
    if (data.brand_engagement && data.brand_engagement.length > 0) {
        hasData = true;
        const engSection = document.createElement('div');
        engSection.innerHTML = `
            <h3 style="color: #ff6b35; margin: ${hasData ? '2rem' : '0'} 0 1rem 0;">Brand Engagement Analysis</h3>
            <div class="competitor-grid">
                ${data.brand_engagement.map(brand => {
                    const isOwnBrand = brand.brand.toLowerCase().includes('crooks');
                    
                    return `
                        <div class="competitor-card ${isOwnBrand ? 'own-brand' : ''}">
                            <div class="brand-name ${isOwnBrand ? 'own' : ''}">${brand.brand}</div>
                            <div class="engagement-metric">${brand.avg_engagement.toLocaleString()}</div>
                            <div class="meta">avg engagement</div>
                            <div style="margin: 0.5rem 0;">
                                <div class="meta">${brand.posts} posts · ${brand.avg_views.toLocaleString()} avg views</div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
        container.appendChild(engSection);
    }
    
    if (!hasData) {
        container.innerHTML = `
            <div class="asset">
                <div style="font-weight: 600; color: #f59e0b; margin-bottom: 0.5rem;">No Competitor Data Available</div>
                <div class="meta">Competitor analysis data not found in your dataset</div>
            </div>
        `;
    }
}

function renderStrategicRecommendations(recommendations) {
    const container = $('#strategic-recommendations');
    if (!container) return;
    
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = `
            <div class="recommendation">
                <div class="recommendation-title">AI Analysis in Progress</div>
                <div>Strategic recommendations are being generated from your competitive data...</div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = '';
    
    recommendations.forEach((rec, index) => {
        const recEl = document.createElement('div');
        recEl.className = 'recommendation';
        recEl.innerHTML = `
            <div class="recommendation-title">
                ${index === 0 ? '🎯' : index === 1 ? '⚡' : '🚀'} ${rec.title}
            </div>
            <div>${rec.description}</div>
        `;
        container.appendChild(recEl);
    });
}

/* ---------- ASSETS ---------- */
async function loadAssets(){
    try {
        const data = await safeFetch('/api/assets');
        renderAssets(data.assets || data);
        setStatus('Assets loaded', true);
    } catch (error) {
        console.error('Assets loading failed:', error);
        renderErrorState('asset-grid', error);
        setStatus(`Assets error: ${error.message}`, false);
    }
}

function renderAssets(assets) {
    const grid = $('#asset-grid');
    if (!grid) return;
    
    if (!assets || assets.length === 0) {
        grid.innerHTML = '<div class="asset">No assets available</div>';
        return;
    }
    
    grid.innerHTML = '';
    
    assets.forEach(asset => {
        const url = `/api/assets/${asset.id}/download`;
        const assetEl = document.createElement('div');
        assetEl.className = 'asset';
        assetEl.innerHTML = `
            <div style="text-align: center; padding: 2rem; background: rgba(255,255,255,0.05); border-radius: 8px; margin-bottom: 1rem;">
                ${asset.thumbnail ? `<img src="${asset.thumbnail}" alt="${asset.filename}" style="max-width: 100%; height: auto;">` : 
                  `<div style="font-size: 2rem;">📄</div>`}
            </div>
            <div style="font-weight: 600; margin-bottom: 0.5rem;">${asset.filename}</div>
            <div class="meta">${(asset.type || 'file').toUpperCase()} · ${formatSize(asset.size_bytes || asset.bytes || 0)}</div>
            <a class="btn btn-primary" href="${url}" style="margin-top: 0.5rem;">Download</a>
        `;
        grid.appendChild(assetEl);
    });
}

function formatSize(bytes) {
    if (!bytes) return '—';
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size > 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex++;
    }
    
    return `${size.toFixed(1)} ${units[unitIndex]}`;
}

/* ---------- CALENDAR ---------- */
async function loadCalendar(view = '7_day_view') {
    $$('.view-switch button').forEach(b => b.classList.toggle('active', b.dataset.view === view));
    
    try {
        const data = await safeFetch(`/api/calendar/${view}`);
        renderCalendar(data.events || data[view] || []);
        setStatus('Calendar loaded', true);
    } catch (error) {
        console.error('Calendar loading failed:', error);
        renderErrorState('calendar-events', error);
        setStatus(`Calendar error: ${error.message}`, false);
    }
}

function renderCalendar(events) {
    const container = $('#calendar-events');
    if (!container) return;
    
    if (!events || events.length === 0) {
        container.innerHTML = '<div class="asset">No calendar events scheduled</div>';
        return;
    }
    
    container.innerHTML = '';
    
    events.forEach(event => {
        const eventEl = document.createElement('div');
        eventEl.className = 'asset';
        eventEl.innerHTML = `
            <div style="font-weight: 700; margin-bottom: 0.5rem;">${event.title}</div>
            <div class="meta">${event.date} — ${event.cultural_context || 'Standard campaign'}</div>
            <div style="margin: 0.5rem 0;">
                <strong>Deliverables:</strong> ${(event.deliverables || []).join(', ') || '—'}
            </div>
            <div style="margin: 0.5rem 0;">
                <strong>Assets:</strong> ${(event.assets_mapped || []).join(', ') || '—'}
            </div>
            <div class="status ${event.status === 'completed' ? 'ok' : 'err'}">${event.status || 'planned'}</div>
        `;
        container.appendChild(eventEl);
    });
}

function bindCalendar() {
    $$('.view-switch [data-view]').forEach(button => {
        button.addEventListener('click', () => loadCalendar(button.dataset.view));
    });
}

/* ---------- AGENCY ---------- */
async function loadAgency(){
    try {
        const data = await safeFetch('/api/agency');
        renderAgency(data);
        setStatus('Agency data loaded', true);
    } catch (error) {
        console.error('Agency loading failed:', error);
        renderErrorState('agency-kpis', error);
        setStatus(`Agency error: ${error.message}`, false);
    }
}

function renderAgency(agency) {
    renderAgencyKPIs(agency);
    renderAgencyProjects(agency);
    renderAgencyDeliverables(agency);
}

function renderAgencyKPIs(agency) {
    const container = $('#agency-kpis');
    if (!container) return;
    
    container.innerHTML = '';
    
    const kpis = [
        ['Phase', agency.phase || '—'],
        ['Budget', `$${(agency.monthly_budget || 0).toLocaleString()}`],
        ['Used', `$${(agency.budget_used || 0).toLocaleString()}`],
        ['On-Time', `${agency.on_time_delivery || 0}%`],
        ['Quality', agency.quality_score || '—'],
        ['Response', agency.response_time || '—'],
    ];
    
    kpis.forEach(([label, value]) => {
        const kpiEl = document.createElement('div');
        kpiEl.className = 'kpi';
        kpiEl.innerHTML = `
            <div class="meta">${label}</div>
            <div style="font-weight: 700; font-size: 1.3rem;">${value}</div>
        `;
        container.appendChild(kpiEl);
    });
}

function renderAgencyProjects(agency) {
    const container = $('#agency-projects');
    if (!container) return;
    
    const projects = agency.current_projects || [];
    
    if (projects.length === 0) {
        container.innerHTML = '<div class="asset">No active projects</div>';
        return;
    }
    
    container.innerHTML = '';
    
    projects.forEach(project => {
        const projectEl = document.createElement('div');
        projectEl.className = 'asset';
        projectEl.innerHTML = `
            <div style="font-weight: 700;">${project.name}</div>
            <div class="meta">${project.status} · due ${project.due_date || '—'}</div>
        `;
        container.appendChild(projectEl);
    });
}

function renderAgencyDeliverables(agency) {
    const container = $('#agency-deliverables');
    if (!container) return;
    
    const breakdown = agency.deliverables_breakdown || {};
    const buckets = ['completed', 'in_progress', 'pending'];
    
    container.innerHTML = '';
    
    buckets.forEach(bucket => {
        const items = breakdown[bucket] || [];
        const bucketEl = document.createElement('div');
        bucketEl.className = 'asset';
        bucketEl.innerHTML = `
            <div style="font-weight: 700; text-transform: uppercase; margin-bottom: 0.5rem;">
                ${bucket.replace('_', ' ')} (${items.length})
            </div>
            ${items.length ? items.map(item => `<div class="meta">• ${item}</div>`).join('') : '<div class="meta">No items</div>'}
        `;
        container.appendChild(bucketEl);
    });
}

/* ---------- FILE UPLOAD ---------- */
function enableUpload() {
    const drop = $('#drop');
    const picker = $('#picker'); 
    const browse = $('#browse');
    const bar = $('#bar');
    const log = $('#upload-log');
    const grid = $('#uploaded');
    
    if (!drop || !picker || !browse) return;
    
    const maxSize = 100 * 1024 * 1024; // 100MB

    function pickFiles() { picker.click(); }
    function setDragging(active) { drop.classList.toggle('drag', active); }
    
    function getFiles(event) {
        return event.dataTransfer?.files || event.target?.files || [];
    }

    async function uploadFile(file) {
        if (file.size > maxSize) {
            throw new Error(`${file.name}: File too large (max 100MB)`);
        }
        
        const formData = new FormData();
        formData.append('files', file);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`${file.name}: Upload failed - ${errorText}`);
        }
        
        return await response.json();
    }

    function addUploadedAsset(asset) {
        const assetEl = document.createElement('div');
        assetEl.className = 'asset';
        assetEl.innerHTML = `
            <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px; margin-bottom: 0.5rem;">
                ${asset.thumbnail ? `<img src="${asset.thumbnail}" alt="${asset.filename}">` : '<div style="font-size: 1.5rem;">📄</div>'}
            </div>
            <div style="font-weight: 600; font-size: 0.9rem;">${asset.filename}</div>
            <div class="meta">${(asset.type || 'file').toUpperCase()} · ${formatSize(asset.size_bytes || asset.bytes || 0)}</div>
        `;
        grid.prepend(assetEl);
    }

    browse.addEventListener('click', pickFiles);
    
    ['dragenter', 'dragover'].forEach(evt => 
        drop.addEventListener(evt, e => {
            e.preventDefault();
            setDragging(true);
        })
    );
    
    ['dragleave', 'dragend', 'drop'].forEach(evt => 
        drop.addEventListener(evt, e => {
            e.preventDefault();
            setDragging(false);
        })
    );

    drop.addEventListener('drop', handleFiles);
    picker.addEventListener('change', handleFiles);
    
    async function handleFiles(event) {
        const files = Array.from(getFiles(event));
        if (!files.length) return;
        
        bar.style.width = '0%';
        log.textContent = '';
        
        let completed = 0;
        
        for (const file of files) {
            try {
                const result = await uploadFile(file);
                const assets = Array.isArray(result.assets) ? result.assets : [result];
                assets.forEach(addUploadedAsset);
                
                completed++;
                bar.style.width = `${Math.round((completed / files.length) * 100)}%`;
                
            } catch (error) {
                console.error('Upload error:', error);
                log.textContent += (log.textContent ? '\n' : '') + error.message;
            }
        }
        
        if (completed > 0) {
            await loadAssets();
        }
    }
}

/* ---------- Error Handling ---------- */
function renderErrorState(containerId, error) {
    const container = $(`#${containerId}`);
    if (!container) return;
    
    container.innerHTML = `
        <div class="asset" style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3);">
            <div style="color: #ef4444; font-weight: 600; margin-bottom: 0.5rem;">Error Loading Data</div>
            <div class="meta">${error.message}</div>
            <button class="btn btn-secondary" onclick="location.reload()" style="margin-top: 0.5rem;">
                Retry
            </button>
        </div>
    `;
}

/* ---------- Auto-refresh ---------- */
function startAutoRefresh() {
    autoRefreshInterval = setInterval(async () => {
        const activeTab = $('.tabs button.active')?.dataset?.tab;
        if (activeTab === 'intel') {
            console.log('Auto-refreshing intelligence data...');
            await loadIntelligence();
        }
    }, 5 * 60 * 1000); // 5 minutes
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

/* ---------- Application Boot ---------- */
window.addEventListener('DOMContentLoaded', async () => {
    console.log('Crooks & Castles Command Center initializing...');
    
    try {
        bindTabs();
        bindCalendar();
        enableUpload();
        
        await loadIntelligence();
        startAutoRefresh();
        
        console.log('Command Center initialized successfully');
        setStatus('Command Center ready', true);
        
    } catch (error) {
        console.error('Initialization failed:', error);
        setStatus('Initialization failed', false);
    }
});

// Global error handling
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
    setStatus('Application error', false);
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
    setStatus('Promise error', false);
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopAutoRefresh();
    if (hashtagChart) hashtagChart.destroy();
});

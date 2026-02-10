/**
 * SEO Audit Tool - Main Application v2.0
 * Dashboard with all feature sections
 */

const API_BASE_URL = window.location.origin;

// DOM Elements
const elements = {
    navItems: document.querySelectorAll('.nav-item'),
    pages: document.querySelectorAll('.page'),
    navReport: document.getElementById('nav-report'),
    form: document.getElementById('analyze-form'),
    urlInput: document.getElementById('url-input'),
    competitorInput: document.getElementById('competitor-input'),
    keywordInput: document.getElementById('keyword-input'),
    analyzeBtn: document.getElementById('analyze-btn'),
    compareBtn: document.getElementById('compare-btn'),
    btnContent: document.querySelector('.btn-content'),
    btnLoader: document.querySelector('.btn-loader'),
    errorContainer: document.getElementById('error-container'),
    errorMessage: document.getElementById('error-message'),
    errorClose: document.getElementById('error-close'),
    analyzedUrlDisplay: document.getElementById('analyzed-url-display'),
    overallScore: document.getElementById('overall-score'),
    mainAuditCircle: document.getElementById('main-audit-circle'),
    subCircle1: document.getElementById('sub-circle-1'),
    subCircle2: document.getElementById('sub-circle-2'),
    subCircle3: document.getElementById('sub-circle-3'),
    subScore1: document.getElementById('sub-score-1'),
    subScore2: document.getElementById('sub-score-2'),
    subScore3: document.getElementById('sub-score-3'),
    issuesList: document.getElementById('issues-list'),
    recommendationsList: document.getElementById('recommendations-list'),
    exportPdfBtn: document.getElementById('export-pdf-btn'),
    exportJsonBtn: document.getElementById('export-json-btn'),
    comparisonSection: document.getElementById('comparison-section')
};

let currentAnalysis = null;
let comparisonChart = null;
let historyChart = null;

function init() {
    elements.navItems.forEach(item => item.addEventListener('click', handleNavClick));
    elements.form.addEventListener('submit', handleFormSubmit);
    elements.errorClose.addEventListener('click', hideError);

    // Competitor input toggles compare button
    elements.competitorInput.addEventListener('input', () => {
        elements.compareBtn.classList.toggle('hidden', !elements.competitorInput.value.trim());
    });
    elements.compareBtn.addEventListener('click', handleCompare);

    // Issue tabs
    document.querySelectorAll('.tab-btn').forEach(btn => btn.addEventListener('click', handleTabClick));
    // Social tabs
    document.querySelectorAll('.social-tab').forEach(btn => btn.addEventListener('click', handleSocialTabClick));
    // Screenshot button
    document.getElementById('take-screenshot-btn').addEventListener('click', handleScreenshot);
    // Export buttons
    elements.exportPdfBtn.addEventListener('click', () => { if (currentAnalysis) window.SEOExport.generatePDFReport(currentAnalysis); });
    elements.exportJsonBtn.addEventListener('click', () => { if (currentAnalysis) window.SEOExport.exportAsJSON(currentAnalysis); });
}

function handleNavClick(e) {
    e.preventDefault();
    const page = e.currentTarget.dataset.page;
    elements.navItems.forEach(item => item.classList.toggle('active', item.dataset.page === page));
    elements.pages.forEach(p => {
        p.classList.toggle('active', p.id === `${page}-page`);
        p.classList.toggle('hidden', p.id !== `${page}-page`);
    });
    if (page === 'history') loadHistory();
}

function switchToReportPage() {
    elements.navItems.forEach(item => item.classList.toggle('active', item.dataset.page === 'report'));
    document.getElementById('analyzer-page').classList.remove('active');
    document.getElementById('analyzer-page').classList.add('hidden');
    document.getElementById('report-page').classList.add('active');
    document.getElementById('report-page').classList.remove('hidden');
    document.getElementById('history-page').classList.remove('active');
    document.getElementById('history-page').classList.add('hidden');
}

async function handleFormSubmit(e) {
    e.preventDefault();
    const url = elements.urlInput.value.trim();
    const keyword = elements.keywordInput.value.trim();
    if (!url) { showError('Please enter a URL'); return; }
    await analyzeURL(url, keyword);
}

async function handleCompare() {
    const url = elements.urlInput.value.trim();
    const competitorUrl = elements.competitorInput.value.trim();
    const keyword = elements.keywordInput.value.trim();
    if (!url || !competitorUrl) { showError('Both URLs are required'); return; }
    setLoading(true); hideError();
    try {
        const resp = await fetch(`${API_BASE_URL}/api/compare`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, competitor_url: competitorUrl, keyword })
        });
        const data = await resp.json();
        if (!resp.ok || !data.success) throw new Error(data.error || 'Comparison failed');
        await analyzeURL(url, keyword);
        renderComparison(data);
    } catch (err) { showError(err.message); }
    finally { setLoading(false); }
}

async function analyzeURL(url, keyword = '') {
    setLoading(true); hideError();
    try {
        const resp = await fetch(`${API_BASE_URL}/api/analyze`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, keyword })
        });
        const data = await resp.json();
        if (!resp.ok || !data.success) throw new Error(data.error || 'Analysis failed');
        currentAnalysis = data;
        renderResults(data);
        switchToReportPage();
    } catch (err) { showError(err.message); }
    finally { setLoading(false); }
}

function setLoading(v) {
    elements.analyzeBtn.disabled = v;
    elements.btnContent.style.display = v ? 'none' : 'flex';
    elements.btnLoader.classList.toggle('hidden', !v);
}
function showError(msg) { elements.errorMessage.textContent = msg; elements.errorContainer.classList.remove('hidden'); }
function hideError() { elements.errorContainer.classList.add('hidden'); }

// ========== RENDER RESULTS ==========
function renderResults(data) {
    elements.analyzedUrlDisplay.textContent = data.url;
    animateCircle(elements.mainAuditCircle, data.overall_score, 251);
    elements.overallScore.textContent = `${data.overall_score}%`;

    const scores = data.summary?.category_scores || {};
    const titleMeta = Math.round(((scores.title || 0) + (scores.meta_description || 0)) / 2);
    const structure = Math.round(((scores.url_structure || 0) + (scores.content || 0) + (scores.headings || 0)) / 3);
    const media = Math.round(((scores.images || 0) + (scores.links || 0) + (scores.performance || 0)) / 3);

    animateCircle(elements.subCircle1, titleMeta, 151);
    animateCircle(elements.subCircle2, structure, 151);
    animateCircle(elements.subCircle3, media, 151);
    elements.subScore1.textContent = `${titleMeta}%`;
    elements.subScore2.textContent = `${structure}%`;
    elements.subScore3.textContent = `${media}%`;

    window.SEOCharts.updateCharts(data);
    renderIssues(data.priority_issues, 'high');
    renderRecommendations(data.recommendations);
    updateProgressBars(data);

    if (data.keyword_analysis) renderKeywordAnalysis(data.keyword_analysis);
    if (data.social_preview) renderSocialPreview(data.social_preview);
    if (data.mobile_friendly) renderMobileTest(data.mobile_friendly);
    if (data.schema_data) renderSchemaMarkup(data.schema_data);
    if (data.broken_links_data) renderBrokenLinks(data.broken_links_data);
    if (data.security_data) renderSecurity(data.security_data);
    if (data.sitemap_data) renderSitemap(data.sitemap_data);
    if (data.vitals_data) renderVitals(data.vitals_data);
    if (data.i18n_data) renderI18n(data.i18n_data);
    if (data.readability_data) renderReadability(data.readability_data);
    renderSERPPreview(data);
}

function animateCircle(el, score, circ) {
    if (!el) return;
    setTimeout(() => { el.style.strokeDashoffset = circ - (score / 100) * circ; }, 100);
}

function updateProgressBars(data) {
    const s = data.summary?.category_scores || {};
    const set = (id, v) => { const e = document.getElementById(id); if (e) e.style.width = `${v || 0}%`; };
    set('bar-title', s.title); set('bar-content', s.content); set('bar-links', s.links);
    set('speed-server', s.performance); set('speed-content', s.content); set('speed-url', s.url_structure);
    set('url-meta', s.meta_description); set('url-headings', s.headings); set('url-images', s.images); set('url-structure', s.url_structure);
}

// ========== KEYWORD ==========
function renderKeywordAnalysis(kd) {
    document.getElementById('keyword-score').textContent = `${kd.score}%`;
    document.getElementById('total-words').textContent = kd.total_words?.toLocaleString() || '-';
    document.getElementById('unique-words').textContent = kd.unique_words?.toLocaleString() || '-';

    const ta = kd.target_keyword_analysis;
    if (ta) {
        document.getElementById('keyword-density').textContent = `${ta.density}%`;
        const pc = document.getElementById('keyword-placements');
        pc.innerHTML = '';
        [{ key: 'in_title', label: 'Title' }, { key: 'in_h1', label: 'H1' }, { key: 'in_meta', label: 'Meta' }, { key: 'in_first_paragraph', label: '1st Paragraph' }].forEach(p => {
            const tag = document.createElement('span');
            tag.className = `placement-tag ${ta[p.key] ? '' : 'missing'}`;
            tag.innerHTML = `<i class="fas ${ta[p.key] ? 'fa-check' : 'fa-times'}"></i> ${p.label}`;
            pc.appendChild(tag);
        });
    } else { document.getElementById('keyword-density').textContent = '-'; }

    const tkc = document.getElementById('top-keywords');
    tkc.innerHTML = '';
    (kd.top_keywords || []).slice(0, 8).forEach(kw => {
        const tag = document.createElement('span');
        tag.className = 'keyword-tag';
        tag.innerHTML = `${kw.word} <span class="density">${kw.density}%</span>`;
        tkc.appendChild(tag);
    });
}

// ========== SOCIAL ==========
function renderSocialPreview(sd) {
    document.getElementById('social-score').textContent = `${sd.score}%`;
    const fb = sd.facebook_preview || {};
    if (fb.image) document.getElementById('fb-preview-image').style.backgroundImage = `url(${fb.image})`;
    document.getElementById('fb-preview-url').textContent = fb.url || '';
    document.getElementById('fb-preview-title').textContent = fb.title || 'No title';
    document.getElementById('fb-preview-description').textContent = fb.description || '';

    const tw = sd.twitter_preview || {};
    if (tw.image) document.getElementById('tw-preview-image').style.backgroundImage = `url(${tw.image})`;
    document.getElementById('tw-preview-title').textContent = tw.title || 'No title';
    document.getElementById('tw-preview-description').textContent = tw.description || '';
    document.getElementById('tw-preview-url').textContent = tw.url || '';

    const li = sd.linkedin_preview || {};
    if (li.image) document.getElementById('li-preview-image').style.backgroundImage = `url(${li.image})`;
    document.getElementById('li-preview-title').textContent = li.title || 'No title';
    document.getElementById('li-preview-description').textContent = li.description || '';
}

function handleSocialTabClick(e) {
    const p = e.target.closest('.social-tab').dataset.platform;
    document.querySelectorAll('.social-tab').forEach(b => b.classList.toggle('active', b.dataset.platform === p));
    document.querySelectorAll('.social-preview').forEach(pr => pr.classList.add('hidden'));
    document.getElementById(`${p}-preview`).classList.remove('hidden');
}

// ========== MOBILE ==========
function renderMobileTest(md) {
    document.getElementById('mobile-score').textContent = `${md.score}%`;
    const sc = document.getElementById('mobile-status');
    const icon = sc.querySelector('.status-icon i');
    const text = sc.querySelector('.status-text');
    if (md.status === 'mobile_friendly') { icon.className = 'fas fa-check-circle'; }
    else if (md.status === 'partially_mobile') { icon.className = 'fas fa-exclamation-circle'; }
    else { icon.className = 'fas fa-times-circle'; }
    text.textContent = md.status_text;

    setCheckStatus(document.getElementById('viewport-check'), md.viewport?.is_valid);
    setCheckStatus(document.getElementById('text-check'), md.text_size?.is_readable);
    setCheckStatus(document.getElementById('tap-check'), md.tap_targets?.is_adequate);
    setCheckStatus(document.getElementById('responsive-check'), md.responsive_design?.responsive_images > 0 || md.responsive_design?.uses_flexbox);
}

function setCheckStatus(el, passed) {
    if (!el) return;
    el.textContent = passed ? 'Pass' : 'Fail';
    el.className = `check-status ${passed ? 'pass' : 'fail'}`;
}

// ========== SCHEMA ==========
function renderSchemaMarkup(sd) {
    document.getElementById('schema-score').textContent = `${sd.score}%`;
    document.getElementById('jsonld-count').textContent = sd.jsonld_count;
    document.getElementById('microdata-count').textContent = sd.microdata_count;
    document.getElementById('total-schemas').textContent = sd.total_schemas;

    const dc = document.getElementById('schema-details');
    dc.innerHTML = '';

    if (!sd.has_structured_data) {
        dc.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:20px;">No structured data found. Add JSON-LD to improve rich snippet eligibility.</p>';
        return;
    }

    (sd.jsonld_schemas || []).forEach(s => {
        const item = document.createElement('div');
        item.className = 'schema-item';
        let fieldsHtml = '';
        (s.fields_found || []).forEach(f => { fieldsHtml += `<span class="field-tag found">✓ ${f}</span>`; });
        (s.fields_missing || []).forEach(f => { fieldsHtml += `<span class="field-tag missing">✗ ${f}</span>`; });
        item.innerHTML = `
            <div class="schema-type">${s.type}</div>
            <div class="schema-format">${s.format} ${s.valid ? '— Valid' : '— Incomplete'}</div>
            <div class="schema-fields">${fieldsHtml}</div>
        `;
        dc.appendChild(item);
    });
}

// ========== BROKEN LINKS ==========
function renderBrokenLinks(ld) {
    document.getElementById('link-health-score').textContent = `${ld.score}%`;
    document.getElementById('links-working').textContent = ld.working;
    document.getElementById('links-redirected').textContent = ld.redirected;
    document.getElementById('links-broken').textContent = ld.broken;

    const bl = document.getElementById('broken-list');
    bl.innerHTML = '';

    if (ld.broken === 0) {
        bl.innerHTML = '<p style="color:var(--accent-green);text-align:center;padding:16px;"><i class="fas fa-check-circle"></i> All links are healthy!</p>';
        return;
    }

    (ld.broken_links || []).forEach(l => {
        const item = document.createElement('div');
        item.className = 'broken-link-item';
        item.innerHTML = `<i class="fas fa-unlink"></i><span class="link-url">${l.url}</span><span class="link-code">${l.status_code || 'Timeout'}</span>`;
        bl.appendChild(item);
    });
}

// ========== SERP PREVIEW ==========
function renderSERPPreview(data) {
    const title = data.analysis?.title?.title || data.url;
    const desc = data.analysis?.meta_description?.description || '';
    const url = data.url;

    try {
        const urlObj = new URL(url);
        document.getElementById('serp-site-name').textContent = urlObj.hostname;
        document.getElementById('serp-breadcrumb').textContent = url;
    } catch (e) {
        document.getElementById('serp-site-name').textContent = url;
        document.getElementById('serp-breadcrumb').textContent = url;
    }

    document.getElementById('serp-title').textContent = title;
    document.getElementById('serp-description').textContent = desc;
}

// ========== SCREENSHOT ==========
async function handleScreenshot() {
    if (!currentAnalysis) return;
    const btn = document.getElementById('take-screenshot-btn');
    const container = document.getElementById('screenshot-container');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Capturing...';
    container.innerHTML = '<p class="screenshot-placeholder">Capturing screenshot...</p>';

    try {
        const resp = await fetch(`${API_BASE_URL}/api/screenshot`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: currentAnalysis.url })
        });
        const data = await resp.json();
        if (data.success) {
            container.innerHTML = `<img src="${data.screenshot}" alt="Page Screenshot">`;
        } else {
            container.innerHTML = `<p class="screenshot-placeholder" style="color:var(--accent-red);">Failed: ${data.error}</p>`;
        }
    } catch (err) {
        container.innerHTML = `<p class="screenshot-placeholder" style="color:var(--accent-red);">Error: ${err.message}</p>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-sync-alt"></i> Capture';
    }
}

// ========== SECURITY ==========
function renderSecurity(sd) {
    document.getElementById('security-score').textContent = `${sd.score}%`;
    const badge = document.getElementById('ssl-badge');
    const sslText = document.getElementById('ssl-text');
    const icon = badge.querySelector('.status-icon i');
    if (sd.is_https) {
        icon.className = 'fas fa-lock';
        icon.style.color = 'var(--accent-green)';
        sslText.textContent = 'HTTPS — Secure Connection';
    } else {
        icon.className = 'fas fa-unlock';
        icon.style.color = 'var(--accent-red)';
        sslText.textContent = 'HTTP — Not Secure';
    }

    // HTTPS check
    const httpsEl = document.getElementById('https-check');
    httpsEl.textContent = sd.is_https ? 'Secure' : 'Not Secure';
    httpsEl.className = `check-status ${sd.is_https ? 'pass' : 'fail'}`;

    // Security headers count
    const found = sd.security_headers?.found?.length || 0;
    const total = found + (sd.security_headers?.missing?.length || 0);
    const headersEl = document.getElementById('sec-headers-count');
    headersEl.textContent = `${found}/${total}`;
    headersEl.className = `check-status ${found >= total / 2 ? 'pass' : 'fail'}`;

    // Mixed content
    const mcEl = document.getElementById('mixed-content-check');
    if (sd.mixed_content?.has_mixed_content) {
        mcEl.textContent = `${sd.mixed_content.count} found`;
        mcEl.className = 'check-status fail';
    } else {
        mcEl.textContent = 'Clean';
        mcEl.className = 'check-status pass';
    }

    // Header tags
    const hl = document.getElementById('security-headers-list');
    hl.innerHTML = '';
    (sd.security_headers?.found || []).forEach(h => {
        const tag = document.createElement('span');
        tag.className = 'header-tag found';
        tag.innerHTML = `<i class="fas fa-check"></i> ${h.label}`;
        hl.appendChild(tag);
    });
    (sd.security_headers?.missing || []).forEach(h => {
        const tag = document.createElement('span');
        tag.className = 'header-tag missing';
        tag.innerHTML = `<i class="fas fa-times"></i> ${h.label}`;
        hl.appendChild(tag);
    });
}

// ========== SITEMAP ==========
function renderSitemap(sd) {
    document.getElementById('sitemap-score').textContent = `${sd.score}%`;

    // Status area
    const statusArea = document.getElementById('sitemap-status-area');
    const statusIcon = statusArea.querySelector('.status-icon i');
    const statusText = document.getElementById('sitemap-status-text');
    const hasAll = sd.robots?.exists && sd.sitemap?.exists;
    if (hasAll) {
        statusIcon.className = 'fas fa-check-circle';
        statusIcon.style.color = 'var(--accent-green)';
        statusText.textContent = 'All files found';
    } else if (sd.robots?.exists || sd.sitemap?.exists) {
        statusIcon.className = 'fas fa-exclamation-circle';
        statusIcon.style.color = 'var(--accent-orange)';
        statusText.textContent = 'Partially configured';
    } else {
        statusIcon.className = 'fas fa-times-circle';
        statusIcon.style.color = 'var(--accent-red)';
        statusText.textContent = 'Not configured';
    }

    const setStatus = (id, exists) => {
        const el = document.getElementById(id);
        el.textContent = exists ? 'Found' : 'Missing';
        el.className = `check-status ${exists ? 'pass' : 'fail'}`;
    };
    setStatus('robots-status', sd.robots?.exists);
    setStatus('sitemap-status', sd.sitemap?.exists);
    setStatus('sitemap-in-robots', sd.robots?.has_sitemap_directive);
    const pagesEl = document.getElementById('sitemap-pages');
    pagesEl.textContent = sd.sitemap?.url_count || '0';
    pagesEl.className = 'check-status';
}

// ========== CORE WEB VITALS ==========
function renderVitals(vd) {
    document.getElementById('vitals-score').textContent = `${vd.score}%`;

    // Status area
    const statusArea = document.getElementById('vitals-status-area');
    const statusIcon = statusArea.querySelector('.status-icon i');
    const statusText = document.getElementById('vitals-status-text');
    if (vd.score >= 80) {
        statusIcon.className = 'fas fa-check-circle';
        statusIcon.style.color = 'var(--accent-green)';
        statusText.textContent = 'Good Performance';
    } else if (vd.score >= 50) {
        statusIcon.className = 'fas fa-exclamation-circle';
        statusIcon.style.color = 'var(--accent-orange)';
        statusText.textContent = 'Needs Improvement';
    } else {
        statusIcon.className = 'fas fa-times-circle';
        statusIcon.style.color = 'var(--accent-red)';
        statusText.textContent = 'Poor Performance';
    }

    const riskColor = (r) => r === 'good' ? 'pass' : 'fail';

    const lcpEl = document.getElementById('vital-lcp');
    lcpEl.textContent = `${(vd.lcp?.estimated_ms / 1000).toFixed(1)}s`;
    lcpEl.className = `check-status ${riskColor(vd.lcp?.risk_level)}`;

    const clsEl = document.getElementById('vital-cls');
    clsEl.textContent = vd.cls?.estimated_score?.toFixed(3) || '0';
    clsEl.className = `check-status ${riskColor(vd.cls?.risk_level)}`;

    const inpEl = document.getElementById('vital-inp');
    inpEl.textContent = `${vd.inp?.estimated_ms || 0}ms`;
    inpEl.className = `check-status ${riskColor(vd.inp?.risk_level)}`;

    const fc = document.getElementById('vitals-factors');
    fc.innerHTML = '';
    const allFactors = [...(vd.lcp?.risk_factors || []), ...(vd.cls?.risk_factors || []), ...(vd.inp?.risk_factors || [])];
    allFactors.slice(0, 5).forEach(f => {
        const item = document.createElement('div');
        item.className = 'factor-item';
        item.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${f}`;
        fc.appendChild(item);
    });
}

// ========== I18N ==========
function renderI18n(id) {
    document.getElementById('i18n-score').textContent = `${id.score}%`;

    // Status area
    const statusArea = document.getElementById('i18n-status-area');
    const statusIcon = statusArea.querySelector('.status-icon i');
    const statusText = document.getElementById('i18n-status-text');
    if (id.score >= 70) {
        statusIcon.className = 'fas fa-check-circle';
        statusIcon.style.color = 'var(--accent-green)';
        statusText.textContent = 'Well Configured';
    } else if (id.score >= 40) {
        statusIcon.className = 'fas fa-exclamation-circle';
        statusIcon.style.color = 'var(--accent-orange)';
        statusText.textContent = 'Partially Configured';
    } else {
        statusIcon.className = 'fas fa-times-circle';
        statusIcon.style.color = 'var(--accent-red)';
        statusText.textContent = 'Needs Attention';
    }

    const lang = id.language;
    const langEl = document.getElementById('i18n-lang');
    langEl.textContent = lang?.has_lang ? `${lang.language_name} (${lang.html_lang})` : 'Not set';
    langEl.className = `check-status ${lang?.has_lang ? 'pass' : 'fail'}`;

    const cs = id.charset;
    const csEl = document.getElementById('i18n-charset');
    csEl.textContent = cs?.has_charset ? cs.charset : 'Not set';
    csEl.className = `check-status ${cs?.has_charset ? 'pass' : 'fail'}`;

    const hr = id.hreflang;
    const hrEl = document.getElementById('i18n-hreflang');
    hrEl.textContent = hr?.has_hreflang ? `${hr.language_count} language(s)` : 'None';
    hrEl.className = `check-status ${hr?.has_hreflang ? 'pass' : 'fail'}`;

    const dirEl = document.getElementById('i18n-dir');
    dirEl.textContent = id.direction?.direction || 'ltr';
    dirEl.className = 'check-status pass';
}

// ========== READABILITY ==========
function renderReadability(rd) {
    document.getElementById('readability-score').textContent = `${rd.score}%`;

    // Status area
    const statusArea = document.getElementById('readability-status-area');
    const statusIcon = statusArea.querySelector('.status-icon i');
    const statusText = document.getElementById('readability-status-text');
    if (rd.score >= 70) {
        statusIcon.className = 'fas fa-check-circle';
        statusIcon.style.color = 'var(--accent-green)';
        statusText.textContent = 'Easy to Read';
    } else if (rd.score >= 40) {
        statusIcon.className = 'fas fa-exclamation-circle';
        statusIcon.style.color = 'var(--accent-orange)';
        statusText.textContent = 'Moderate Difficulty';
    } else {
        statusIcon.className = 'fas fa-times-circle';
        statusIcon.style.color = 'var(--accent-red)';
        statusText.textContent = 'Difficult to Read';
    }

    document.getElementById('flesch-score').textContent = rd.flesch_reading_ease || '—';
    document.getElementById('grade-level').textContent = rd.flesch_grade_level || '—';
    document.getElementById('fog-index').textContent = rd.gunning_fog || '—';
    document.getElementById('read-difficulty').textContent = rd.difficulty || '—';
    document.getElementById('read-sentence-len').textContent = rd.avg_sentence_length ? `${rd.avg_sentence_length} words` : '—';
    document.getElementById('read-sentences').textContent = rd.total_sentences || '—';
}

// ========== COMPARISON ==========
function renderComparison(data) {
    elements.comparisonSection.classList.remove('hidden');
    document.getElementById('your-score').textContent = `${data.your_site.overall_score}%`;
    document.getElementById('competitor-score').textContent = `${data.competitor.overall_score}%`;

    const badge = document.getElementById('comparison-winner');
    if (data.winner === 'your_site') { badge.textContent = '🏆 You Win!'; badge.style.background = 'rgba(16,185,129,0.3)'; }
    else if (data.winner === 'competitor') { badge.textContent = 'Competitor Leads'; badge.style.background = 'rgba(239,68,68,0.3)'; }
    else { badge.textContent = "It's a Tie"; }

    const ctx = document.getElementById('comparison-chart');
    if (ctx) {
        if (comparisonChart) comparisonChart.destroy();
        const cats = Object.keys(data.comparison.categories);
        comparisonChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: cats.map(c => c.replace('_', ' ')),
                datasets: [
                    { label: 'Your Site', data: cats.map(c => data.your_site.category_scores[c] || 0), backgroundColor: '#6366f1', borderRadius: 4 },
                    { label: 'Competitor', data: cats.map(c => data.competitor.category_scores[c] || 0), backgroundColor: '#ec4899', borderRadius: 4 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, max: 100 } }, plugins: { legend: { position: 'bottom' } } }
        });
    }
}

// ========== HISTORY ==========
async function loadHistory() {
    try {
        const resp = await fetch(`${API_BASE_URL}/api/history`);
        const data = await resp.json();
        if (!data.success) return;

        const tbody = document.getElementById('history-tbody');
        tbody.innerHTML = '';

        (data.history || []).forEach(item => {
            const gradeClass = `grade-${(item.grade || 'f')[0].toLowerCase()}`;
            const d = new Date(item.timestamp);
            const dateStr = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
            const row = document.createElement('tr');
            row.innerHTML = `
                <td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${item.url}</td>
                <td><strong>${item.score}%</strong></td>
                <td><span class="grade-badge ${gradeClass}">${item.grade}</span></td>
                <td>${dateStr}</td>
            `;
            tbody.appendChild(row);
        });

        // Chart
        const chartData = data.history.slice(0, 20).reverse();
        const ctx = document.getElementById('history-chart');
        if (ctx && chartData.length > 0) {
            if (historyChart) historyChart.destroy();
            historyChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: chartData.map(d => new Date(d.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
                    datasets: [{
                        label: 'SEO Score',
                        data: chartData.map(d => d.score),
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#6366f1'
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, max: 100 } }, plugins: { legend: { display: false } } }
            });
        }
    } catch (err) { console.error('History load error:', err); }
}

// ========== ISSUES & RECOMMENDATIONS ==========
function renderIssues(priorityIssues, priority = 'high') {
    const c = elements.issuesList;
    c.innerHTML = '';
    const issues = priorityIssues[priority] || [];
    if (issues.length === 0) {
        c.innerHTML = `<div class="issue-item ${priority}"><span class="issue-badge ${priority}">${getPriorityLabel(priority)}</span><div class="issue-content"><p class="issue-message">No ${getPriorityLabel(priority).toLowerCase()} issues found! 🎉</p></div></div>`;
        return;
    }
    issues.forEach(issue => {
        const item = document.createElement('div');
        item.className = `issue-item ${priority}`;
        item.innerHTML = `<span class="issue-badge ${priority}">${getPriorityLabel(priority)}</span><div class="issue-content"><p class="issue-category">${issue.category}</p><p class="issue-message">${issue.message}</p></div>`;
        c.appendChild(item);
    });
}

function getPriorityLabel(p) { return { high: 'Critical', medium: 'Warning', low: 'Notice' }[p] || p; }

function handleTabClick(e) {
    const tab = e.target.closest('.tab-btn').dataset.tab;
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
    if (currentAnalysis?.priority_issues) renderIssues(currentAnalysis.priority_issues, tab);
}

function renderRecommendations(recs) {
    const c = elements.recommendationsList;
    c.innerHTML = '';
    if (!recs || !recs.length) { c.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:20px;">No recommendations.</p>'; return; }
    recs.slice(0, 8).forEach((rec, i) => {
        const item = document.createElement('div');
        item.className = 'recommendation-item';
        item.innerHTML = `<span class="recommendation-number">${i + 1}</span><div class="recommendation-content"><p class="recommendation-category">${rec.category}</p><p class="recommendation-text">${rec.recommendation}</p></div>`;
        c.appendChild(item);
    });
}

document.addEventListener('DOMContentLoaded', init);

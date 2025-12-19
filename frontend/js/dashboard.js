// AutoAssess Dashboard JavaScript

// Configuration
const API_BASE_URL = (() => {
    const metaTag = document.querySelector('meta[name="api-base-url"]');
    const globalOverride = window.AUTOASSESS_API_BASE_URL;
    const sanitize = (url) => url.replace(/\/$/, '');
    if (metaTag && metaTag.content.trim()) {
        return sanitize(metaTag.content.trim());
    }
    if (globalOverride && typeof globalOverride === 'string' && globalOverride.trim()) {
        return sanitize(globalOverride.trim());
    }
    const origin = window.location.origin;
    const isFileProtocol = window.location.protocol === 'file:';
    if (!origin || origin === 'null' || isFileProtocol) {
        return 'http://localhost:5000';
    }
    return origin;
})();

// State Management
let submissions = [];
let statistics = {};
let monitoringActive = false;
let sortColumn = null;
let sortDirection = 'asc'; // 'asc' or 'desc'

// DOM Elements
const elements = {
    // Monitoring
    startMonitoringBtn: document.getElementById('startMonitoringBtn'),
    stopMonitoringBtn: document.getElementById('stopMonitoringBtn'),
    monitoringStatus: document.getElementById('monitoringStatus'),
    
    // Statistics
    totalSubmissions: document.getElementById('totalSubmissions'),
    evaluated: document.getElementById('evaluated'),
    pending: document.getElementById('pending'),
    avgScore: document.getElementById('avgScore'),
    passRate: document.getElementById('passRate'),
    
    // Actions
    searchInput: document.getElementById('searchInput'),
    statusFilter: document.getElementById('statusFilter'),
    refreshBtn: document.getElementById('refreshBtn'),
    downloadSpreadsheetBtn: document.getElementById('downloadSpreadsheetBtn'),
    
    // Table
    submissionsBody: document.getElementById('submissionsBody'),
    submissionCount: document.getElementById('submissionCount'),
    loadingIndicator: document.getElementById('loadingIndicator'),
    emptyState: document.getElementById('emptyState'),
    
    // Modal
    detailsModal: document.getElementById('detailsModal'),
    modalBody: document.getElementById('modalBody'),
    closeModalBtn: document.getElementById('closeModalBtn')
};

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('AutoAssess Dashboard Initialized');
    
    // Attach event listeners
    attachEventListeners();
    
    // Load initial data
    loadDashboardData();
    
    // Check monitoring status
    checkMonitoringStatus();
    
    // Auto-refresh every 30 seconds
    setInterval(loadDashboardData, 30000);
});

// Event Listeners
function attachEventListeners() {
    // Monitoring buttons
    elements.startMonitoringBtn.addEventListener('click', startMonitoring);
    elements.stopMonitoringBtn.addEventListener('click', stopMonitoring);
    
    // Action buttons
    elements.refreshBtn.addEventListener('click', loadDashboardData);
    elements.downloadSpreadsheetBtn.addEventListener('click', downloadSpreadsheet);
    
    // Search and filter
    elements.searchInput.addEventListener('input', filterSubmissions);
    elements.statusFilter.addEventListener('change', filterSubmissions);
    
    // Table header sorting
    attachSortingListeners();
    
    // Modal
    elements.closeModalBtn.addEventListener('click', closeModal);
    elements.detailsModal.addEventListener('click', (e) => {
        if (e.target === elements.detailsModal) {
            closeModal();
        }
    });
}

// API Functions
async function apiCall(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (body) {
            options.body = JSON.stringify(body);
        }
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const contentType = response.headers.get('content-type') || '';
        let data;
        
        if (contentType.includes('application/json')) {
            data = await response.json();
        } else {
            const text = await response.text();
            throw new Error(text || `Unexpected response format (status ${response.status})`);
        }
        
        if (!response.ok || !data.success) {
            const message = data?.error || data?.message || `Request failed with status ${response.status}`;
            throw new Error(message);
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showNotification('Error: ' + error.message, 'error');
        throw error;
    }
}

// Load Dashboard Data
async function loadDashboardData() {
    showLoading(true);
    
    try {
        // Load submissions
        const submissionsData = await apiCall('/api/submissions');
        submissions = submissionsData.submissions || [];
        
        // Load statistics
        const statsData = await apiCall('/api/stats/overview');
        statistics = statsData.statistics || {};
        
        // Update UI
        updateStatistics();
        renderSubmissions();
        
        showNotification('Data refreshed successfully', 'success');
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    } finally {
        showLoading(false);
    }
}

// Update Statistics Display
function updateStatistics() {
    elements.totalSubmissions.textContent = statistics.total_submissions || 0;
    elements.evaluated.textContent = statistics.evaluated || 0;
    elements.pending.textContent = statistics.pending || 0;
    elements.avgScore.textContent = statistics.average_score ? statistics.average_score.toFixed(2) : '0';
    elements.passRate.textContent = statistics.pass_rate ? statistics.pass_rate.toFixed(1) + '%' : '0%';
}

// Render Submissions Table
function renderSubmissions(filteredSubmissions = null) {
    const dataToRender = filteredSubmissions || submissions;
    
    elements.submissionCount.textContent = `${dataToRender.length} submission${dataToRender.length !== 1 ? 's' : ''}`;
    
    if (dataToRender.length === 0) {
        elements.emptyState.style.display = 'block';
        elements.submissionsBody.innerHTML = '';
        return;
    }
    
    elements.emptyState.style.display = 'none';
    
    elements.submissionsBody.innerHTML = dataToRender.map(submission => `
        <tr>
            <td>${submission.student_id || 'N/A'}</td>
            <td>${submission.student_name || 'N/A'}</td>
            <td>${submission.file_name || 'N/A'}</td>
            <td>${formatDate(submission.submitted_at)}</td>
            <td>
                <span class="status-badge status-${submission.status}">
                    ${submission.status.toUpperCase()}
                </span>
            </td>
            <td>${submission.assessment ? submission.assessment.total_score.toFixed(2) : '-'}</td>
            <td>
                <span class="grade grade-${getGradeClass(submission.assessment?.grade)}">
                    ${submission.assessment?.grade || '-'}
                </span>
            </td>
            <td>
                <div class="table-actions">
                    <button class="btn btn-sm btn-info" onclick="viewDetails('${submission._id}')">
                        📋 Details
                    </button>
                    ${submission.status === 'evaluated' ? `
                        <button class="btn btn-sm btn-download" onclick="downloadReport('${submission._id}')">
                            📥 Report
                        </button>
                    ` : ''}
                </div>
            </td>
        </tr>
    `).join('');
}

// Filter Submissions
function filterSubmissions() {
    const searchTerm = elements.searchInput.value.toLowerCase();
    const statusFilter = elements.statusFilter.value;
    
    const filtered = submissions.filter(submission => {
        const matchesSearch = 
            (submission.student_id && submission.student_id.toLowerCase().includes(searchTerm)) ||
            (submission.student_name && submission.student_name.toLowerCase().includes(searchTerm)) ||
            (submission.file_name && submission.file_name.toLowerCase().includes(searchTerm));
        
        const matchesStatus = !statusFilter || submission.status === statusFilter;
        
        return matchesSearch && matchesStatus;
    });
    
    renderSubmissions(filtered);
}

// Sorting Functions
function attachSortingListeners() {
    const table = document.getElementById('submissionsTable');
    if (!table) return;
    
    const headers = table.querySelectorAll('thead th');
    
    const sortableColumns = [
        { index: 0, key: 'student_id', type: 'string', label: 'Student ID' },
        { index: 1, key: 'student_name', type: 'string', label: 'Student Name' },
        { index: 2, key: 'file_name', type: 'string', label: 'File Name' },
        { index: 3, key: 'submitted_at', type: 'date', label: 'Submission Date' },
        { index: 4, key: 'status', type: 'string', label: 'Status' },
        { index: 5, key: 'score', type: 'number', label: 'Score' },
        { index: 6, key: 'grade', type: 'string', label: 'Grade' }
    ];
    
    sortableColumns.forEach(column => {
        const header = headers[column.index];
        if (!header) return;
        
        // Store original label
        header.setAttribute('data-column', column.key);
        header.setAttribute('data-label', column.label);
        
        header.style.cursor = 'pointer';
        header.style.userSelect = 'none';
        header.title = 'Click to sort';
        
        header.addEventListener('click', () => {
            sortTable(column.key, column.type);
        });
    });
}

function sortTable(column, type) {
    // Toggle sort direction if same column, otherwise default to ascending
    if (sortColumn === column) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        sortColumn = column;
        sortDirection = 'asc';
    }
    
    // Sort the submissions array
    submissions.sort((a, b) => {
        let valueA, valueB;
        
        if (column === 'score') {
            valueA = a.assessment?.total_score ?? -1;
            valueB = b.assessment?.total_score ?? -1;
        } else if (column === 'grade') {
            valueA = a.assessment?.grade || 'Z';
            valueB = b.assessment?.grade || 'Z';
        } else {
            valueA = a[column] || '';
            valueB = b[column] || '';
        }
        
        let comparison = 0;
        
        if (type === 'number') {
            comparison = valueA - valueB;
        } else if (type === 'date') {
            comparison = new Date(valueA) - new Date(valueB);
        } else {
            // String comparison
            comparison = String(valueA).localeCompare(String(valueB), undefined, { 
                numeric: true, 
                sensitivity: 'base' 
            });
        }
        
        return sortDirection === 'asc' ? comparison : -comparison;
    });
    
    // Update sort indicators and re-render
    updateSortIndicators();
    filterSubmissions(); // This will re-render with current filters
}

function updateSortIndicators() {
    const table = document.getElementById('submissionsTable');
    if (!table) return;
    
    const headers = table.querySelectorAll('thead th');
    
    // Remove all existing sort indicators and restore original labels
    headers.forEach(header => {
        const originalLabel = header.getAttribute('data-label');
        if (originalLabel) {
            header.textContent = originalLabel;
        }
    });
    
    // Add indicator to current sorted column
    if (sortColumn) {
        headers.forEach(header => {
            const columnKey = header.getAttribute('data-column');
            if (columnKey === sortColumn) {
                const originalLabel = header.getAttribute('data-label');
                const arrow = sortDirection === 'asc' ? ' ▲' : ' ▼';
                header.textContent = originalLabel + arrow;
            }
        });
    }
}

// Monitoring Functions
async function startMonitoring() {
    try {
        await apiCall('/api/monitor/start', 'POST');
        monitoringActive = true;
        updateMonitoringUI();
        showNotification('Monitoring started successfully', 'success');
    } catch (error) {
        console.error('Error starting monitoring:', error);
    }
}

async function stopMonitoring() {
    try {
        await apiCall('/api/monitor/stop', 'POST');
        monitoringActive = false;
        updateMonitoringUI();
        showNotification('Monitoring stopped', 'info');
    } catch (error) {
        console.error('Error stopping monitoring:', error);
    }
}

async function checkMonitoringStatus() {
    try {
        const data = await apiCall('/api/monitor/status');
        monitoringActive = data.monitoring_active;
        updateMonitoringUI();
    } catch (error) {
        console.error('Error checking monitoring status:', error);
    }
}

function updateMonitoringUI() {
    const statusDot = elements.monitoringStatus.querySelector('.status-dot');
    const statusText = elements.monitoringStatus.querySelector('.status-text');
    
    if (monitoringActive) {
        statusDot.classList.remove('inactive');
        statusDot.classList.add('active');
        statusText.textContent = 'Active';
        elements.startMonitoringBtn.disabled = true;
        elements.stopMonitoringBtn.disabled = false;
    } else {
        statusDot.classList.remove('active');
        statusDot.classList.add('inactive');
        statusText.textContent = 'Inactive';
        elements.startMonitoringBtn.disabled = false;
        elements.stopMonitoringBtn.disabled = true;
    }
}

// View Submission Details
async function viewDetails(submissionId) {
    try {
        const data = await apiCall(`/api/submissions/${submissionId}`);
        const submission = data.submission;
        
        if (!submission) {
            throw new Error('Submission not found');
        }
        
        const modalContent = generateDetailsHTML(submission);
        elements.modalBody.innerHTML = modalContent;
        elements.detailsModal.classList.add('active');
    } catch (error) {
        console.error('Error viewing details:', error);
    }
}

function generateDetailsHTML(submission) {
    const assessment = submission.assessment || {};
    const breakdown = assessment.breakdown || {};
    
    let html = `
        <div class="detail-group">
            <div class="detail-label">Student ID</div>
            <div class="detail-value">${submission.student_id || 'N/A'}</div>
        </div>
        
        <div class="detail-group">
            <div class="detail-label">Student Name</div>
            <div class="detail-value">${submission.student_name || 'N/A'}</div>
        </div>
        
        <div class="detail-group">
            <div class="detail-label">File Name</div>
            <div class="detail-value">${submission.file_name || 'N/A'}</div>
        </div>
        
        <div class="detail-group">
            <div class="detail-label">Submission Date</div>
            <div class="detail-value">${formatDate(submission.submitted_at)}</div>
        </div>
        
        <div class="detail-group">
            <div class="detail-label">Status</div>
            <div class="detail-value">
                <span class="status-badge status-${submission.status}">
                    ${submission.status.toUpperCase()}
                </span>
            </div>
        </div>
    `;
    
    if (submission.status === 'evaluated') {
        html += `
            <hr style="margin: 25px 0; border: none; border-top: 2px solid #eee;">
            
            <h3 style="color: var(--primary-color); margin-bottom: 20px;">Assessment Results</h3>
            
            <div class="detail-group">
                <div class="detail-label">Total Score</div>
                <div class="detail-value">
                    <span style="font-size: 1.5rem; font-weight: bold; color: var(--primary-color);">
                        ${assessment.total_score?.toFixed(2) || '0'}/100
                    </span>
                    <span class="grade grade-${getGradeClass(assessment.grade)}" style="margin-left: 15px; font-size: 1.3rem;">
                        ${assessment.grade || '-'}
                    </span>
                </div>
            </div>
            
            <div class="score-breakdown">
                <h4 style="margin-bottom: 15px;">Score Breakdown</h4>
                ${Object.entries(breakdown).map(([category, data]) => `
                    <div class="score-item">
                        <span>${category.replace(/_/g, ' ').toUpperCase()}</span>
                        <span><strong>${data.score?.toFixed(2) || 0}</strong> / ${data.max_score || 0} (${data.percentage?.toFixed(1) || 0}%)</span>
                    </div>
                `).join('')}
            </div>
            
            ${assessment.strengths && assessment.strengths.length > 0 ? `
                <div class="feedback-section">
                    <h4 style="color: var(--success-color);">✓ Strengths</h4>
                    <ul class="feedback-list">
                        ${assessment.strengths.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${assessment.improvements && assessment.improvements.length > 0 ? `
                <div class="feedback-section">
                    <h4 style="color: var(--warning-color);">○ Areas for Improvement</h4>
                    <ul class="feedback-list">
                        ${assessment.improvements.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${assessment.recommendations && assessment.recommendations.length > 0 ? `
                <div class="feedback-section">
                    <h4 style="color: var(--primary-color);">→ Recommendations</h4>
                    <ul class="feedback-list">
                        ${assessment.recommendations.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
    }
    
    return html;
}

// Download Functions
async function downloadReport(submissionId, format = 'pdf') {
    try {
        showNotification(`Generating ${format.toUpperCase()} report...`, 'info');
        const data = await apiCall(`/api/reports/individual/${submissionId}?format=${format}`);
        
        if (data.download_url) {
            window.open(`${API_BASE_URL}${data.download_url}`, '_blank');
            showNotification(`${format.toUpperCase()} report downloaded successfully`, 'success');
        }
    } catch (error) {
        console.error('Error downloading report:', error);
    }
}

async function downloadSpreadsheet() {
    try {
        showNotification('Generating spreadsheet...', 'info');
        const data = await apiCall('/api/reports/spreadsheet');
        
        if (data.download_url) {
            window.open(`${API_BASE_URL}${data.download_url}`, '_blank');
            showNotification('Spreadsheet downloaded successfully', 'success');
        }
    } catch (error) {
        console.error('Error downloading spreadsheet:', error);
    }
}

// Modal Functions
function closeModal() {
    elements.detailsModal.classList.remove('active');
}

// Utility Functions
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getGradeClass(grade) {
    if (!grade) return 'f';
    const firstChar = grade.charAt(0).toLowerCase();
    return firstChar;
}

function showLoading(show) {
    elements.loadingIndicator.style.display = show ? 'block' : 'none';
}

function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#F44336' : '#2196F3'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 2000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);

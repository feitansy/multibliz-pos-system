/**
 * Multibliz POS - Data Visualization Library
 * Handles all Chart.js initialization, sparklines, and KPI displays
 */

// Initialize 7-day sales sparkline chart
function initializeSparklineChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = data.map(item => item.date);
    const amounts = data.map(item => item.amount);

    // Determine a nice step size and suggested max based on data so small values render well
    const maxAmount = amounts.length ? Math.max(...amounts) : 0;
    // Default fallback step (if max is 0)
    let computedStep = 1;
    if (maxAmount > 0) {
        // Aim for roughly 3 steps on y-axis
        const rawStep = Math.ceil(maxAmount / 3);
        // Round rawStep to a "nice" number (1,2,5 * pow10)
        const pow10 = Math.pow(10, Math.floor(Math.log10(rawStep)));
        const leading = Math.ceil(rawStep / pow10);
        let niceLead;
        if (leading <= 1) niceLead = 1;
        else if (leading <= 2) niceLead = 2;
        else if (leading <= 5) niceLead = 5;
        else niceLead = 10;
        computedStep = niceLead * pow10;
    }
    const suggestedMax = Math.max(computedStep * 3, computedStep);

    // (Threshold plugin removed) Sparkline will render without horizontal reference lines.

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '7-Day Sales Trend',
                data: amounts,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.08)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointBackgroundColor: '#10b981',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 5,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(31, 41, 55, 0.9)',
                    padding: 12,
                    titleFont: { size: 12, weight: 600 },
                    bodyFont: { size: 11 },
                    borderColor: '#d1d5db',
                    borderWidth: 1,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return '₱' + context.raw.toLocaleString('en-PH', {minimumFractionDigits: 2});
                        }
                    }
                }
            },
            scales: {
                y: {
                        beginAtZero: true,
                        // Suggested max and step are computed from the data for better scaling
                        suggestedMax: suggestedMax,
                        border: { display: false },
                        grid: {
                            color: 'rgba(209, 213, 219, 0.3)',
                            drawBorder: false,
                        },
                        ticks: {
                            color: '#9ca3af',
                            font: { size: 11 },
                            stepSize: computedStep,
                            callback: function(value) {
                                if (typeof value === 'number') {
                                    return '₱' + value.toLocaleString();
                                }
                                return value;
                            }
                        }
                    },
                x: {
                    border: { display: false },
                    grid: { display: false },
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 11 }
                    }
                }
            }
        },
        // no per-chart plugins attached
    });
}

// Initialize sales by day of week bar chart
function initializeBarChart(canvasId, salesByDay) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const data = daysOfWeek.map(day => salesByDay[day] || 0);
    
    // Get max value for scaling
    const maxValue = Math.max(...data);
    const stepSize = Math.ceil(maxValue / 5);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Sales Count',
                data: data,
                backgroundColor: [
                    'rgba(37, 99, 235, 0.8)',      // Blue - Mon
                    'rgba(59, 130, 246, 0.8)',     // Light Blue - Tue
                    'rgba(96, 165, 250, 0.8)',     // Sky Blue - Wed
                    'rgba(16, 185, 129, 0.8)',     // Green - Thu
                    'rgba(34, 197, 94, 0.8)',      // Light Green - Fri
                    'rgba(139, 92, 246, 0.8)',     // Purple - Sat
                    'rgba(236, 72, 153, 0.8)',     // Pink - Sun
                ],
                borderColor: [
                    '#2563eb',
                    '#3b82f6',
                    '#60a5fa',
                    '#10b981',
                    '#22c55e',
                    '#8b5cf6',
                    '#ec4899',
                ],
                borderWidth: 1,
                borderRadius: 8,
                borderSkipped: false,
                hoverBackgroundColor: [
                    'rgba(37, 99, 235, 1)',
                    'rgba(59, 130, 246, 1)',
                    'rgba(96, 165, 250, 1)',
                    'rgba(16, 185, 129, 1)',
                    'rgba(34, 197, 94, 1)',
                    'rgba(139, 92, 246, 1)',
                    'rgba(236, 72, 153, 1)',
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'x',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(31, 41, 55, 0.9)',
                    padding: 12,
                    titleFont: { size: 12, weight: 600 },
                    bodyFont: { size: 11 },
                    borderColor: '#d1d5db',
                    borderWidth: 1,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return context.raw + ' transactions';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    border: { display: false },
                    grid: {
                        color: 'rgba(209, 213, 219, 0.3)',
                        drawBorder: false,
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 11 },
                        stepSize: stepSize,
                    }
                },
                x: {
                    border: { display: false },
                    grid: { display: false },
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 11 }
                    }
                }
            }
        }
    });
}

// Create KPI change indicator with arrow and color
function createKPIIndicator(value) {
    const isPositive = value >= 0;
    const arrowIcon = isPositive ? '↑' : '↓';
    const colorClass = isPositive ? 'text-success' : 'text-danger';
    const absValue = Math.abs(value);
    
    return `<span class="kpi-indicator ${colorClass} fw-bold">
        ${arrowIcon} ${absValue.toFixed(1)}%
    </span>`;
}

// Add KPI indicators to metric cards (injected via JS)
function addKPIIndicators() {
    // Sales KPI - will be updated via data attribute
    const salesCard = document.querySelector('[data-kpi="sales"]');
    if (salesCard && window.salesChangePercent !== undefined) {
        const indicator = createKPIIndicator(window.salesChangePercent);
        const kpiContainer = salesCard.querySelector('.kpi-container');
        if (kpiContainer) {
            kpiContainer.innerHTML = indicator;
        }
    }
}

// Animate number counters for metric values
function animateCounter(element, target, duration = 1000) {
    if (!element || isNaN(target)) return;
    
    const start = 0;
    const startTime = performance.now();
    
    function animate(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const current = Math.floor(start + (target - start) * progress);
        
        element.textContent = current.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            element.textContent = target.toLocaleString();
        }
    }
    
    requestAnimationFrame(animate);
}

// Initialize all charts on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize sparkline (7-day trend)
    if (window.sevenDaySalesData) {
        initializeSparklineChart('salesSparklineChart', JSON.parse(window.sevenDaySalesData));
    }
    
    // Initialize bar chart (sales by day of week)
    if (window.salesByDayData) {
        initializeBarChart('salesByDayChart', JSON.parse(window.salesByDayData));
    }
    
    // Add KPI indicators
    addKPIIndicators();
    
    // Animate metric counters
    setTimeout(() => {
        const salesCountElement = document.querySelector('[data-metric="sales-count"]');
        if (salesCountElement && salesCountElement.textContent) {
            const count = parseInt(salesCountElement.textContent);
            animateCounter(salesCountElement, count, 1500);
        }
    }, 100);
});

// Export for use in other contexts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeSparklineChart,
        initializeBarChart,
        createKPIIndicator,
        addKPIIndicators,
        animateCounter
    };
}

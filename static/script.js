const ctx = document.getElementById('priceChart').getContext('2d');
let priceChart;

// Digital Clock Update
setInterval(() => {
    const now = new Date();
    // Offset for Bangkok if local time isn't already UTC+7 (for display consistency)
    // Actually simpler: just use a formatter for the UI clock
    const options = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false, timeZone: 'Asia/Bangkok' };
    const timeString = new Intl.DateTimeFormat('en-US', options).format(now);
    const clockEl = document.getElementById('digital-clock');
    if (clockEl) clockEl.innerText = timeString;
}, 1000);

async function fetchData() {
    try {
        const response = await fetch('/api/latest');
        const data = await response.json();
        console.log("Data fetched:", data.last_updated);

        if (data.price) {
            document.getElementById('current-price').innerText = `$${data.price.toFixed(2)}`;

            // Handle raw prediction string or numbers
            const predEl = document.getElementById('prediction-price');
            const trendEl = document.getElementById('trend-indicator');
            const trend = (data.trend || "").toUpperCase();

            // Display numerical price if available
            if (data.prediction) {
                predEl.innerText = `$${data.prediction.toFixed(2)}`;
            } else if (typeof data.prediction_raw === 'string') {
                predEl.innerText = data.prediction_raw;
            }

            document.getElementById('last-updated').innerText = data.last_updated;

            if (data.accuracy !== undefined) {
                document.getElementById('accuracy-rate').innerText = `${data.accuracy.toFixed(1)}%`;

                const lastEl = document.getElementById('last-prediction-status');
                if (lastEl) {
                    if (data.last_correct === true) {
                        lastEl.innerHTML = 'Last 1h: <span style="color: #4dFF4d;">Correct</span>';
                    } else if (data.last_correct === false) {
                        lastEl.innerHTML = 'Last 1h: <span style="color: #FF4d4d;">Incorrect</span>';
                    } else {
                        lastEl.innerText = 'Last 1h: N/A';
                    }
                }
            }

            // Update Confidence and Reasoning
            if (data.confidence !== undefined) {
                const confScoreEl = document.getElementById('confidence-score');
                const confReasonEl = document.getElementById('confidence-reasoning');

                confScoreEl.innerText = `${data.confidence}%`;
                confReasonEl.innerText = data.reasoning;

                // Colorize confidence score
                if (data.confidence >= 100) confScoreEl.style.color = 'var(--green)';
                else if (data.confidence >= 66) confScoreEl.style.color = '#FDB931';
                else confScoreEl.style.color = 'var(--red)';
            }

            const pctVal = data.pct_change !== undefined ? ` (${data.pct_change >= 0 ? '+' : ''}${data.pct_change.toFixed(2)}%)` : '';

            if (trend.includes('UP')) {
                trendEl.innerHTML = (trend.includes('STRONG') ? '🚀 STRONG UP' : '▲ Trending UP') + pctVal;
                trendEl.className = 'trend trend-up';
            } else if (trend.includes('DOWN')) {
                trendEl.innerHTML = (trend.includes('STRONG') ? '📉 STRONG DOWN' : '▼ Trending DOWN') + pctVal;
                trendEl.className = 'trend trend-down';
            } else {
                trendEl.innerHTML = '〓 SIDEWAYS' + pctVal;
                trendEl.className = 'trend trend-neutral';
            }

            // Display Sentiment and RSI if available
            if (data.sentiment) {
                const sentimentEl = document.getElementById('sentiment-val');
                if (sentimentEl) sentimentEl.innerText = data.sentiment;
            }
            if (data.rsi) {
                const rsiEl = document.getElementById('rsi-val');
                if (rsiEl) rsiEl.innerText = `${data.rsi.toFixed(2)}`;
            }

            // Update Market Sentiment List
            if (data.market_news) {
                const newsList = document.getElementById('news-summary-list');
                if (newsList) {
                    newsList.innerHTML = '';
                    data.market_news.forEach(news => {
                        const impactColor = news.impact === 'Positive' ? 'var(--green)' : news.impact === 'Negative' ? 'var(--red)' : '#FDB931';
                        const item = document.createElement('div');
                        item.style.padding = '10px';
                        item.style.borderLeft = `4px solid ${impactColor}`;
                        item.style.background = 'rgba(255,255,255,0.02)';
                        item.style.fontSize = '0.9rem';
                        item.innerHTML = `<b style="color: #fff">${news.title}</b> <span style="color: ${impactColor}; font-weight: bold;">[${news.impact}]</span><br>
                                          <span style="color: #a1a1a1; font-size: 0.85rem;">${news.summary_th}</span>`;
                        newsList.appendChild(item);
                    });
                }
            }

            // Update percentage
            if (data.pct_change !== undefined) {
                const sign = data.pct_change >= 0 ? '+' : '';
                const pctEl = document.createElement('span');
                pctEl.style.fontWeight = 'bold';
                pctEl.style.marginLeft = '8px';
                pctEl.innerText = `(${sign}${data.pct_change.toFixed(2)}%)`;
                trendEl.appendChild(pctEl);
            }

            // Update Chart (Simple simulation since we only have single points for now)
            // In a real app we would fetch history. For now let's just plot these two points.
            updateChart(data);
        }
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function updateChart(data) {
    // Expecting data.chart to have { labels, prices, prediction_point }
    if (!data.chart) return;

    const labels = data.chart.labels;
    const historyData = data.chart.prices;
    const predictionData = data.chart.prediction_point;

    if (priceChart) {
        priceChart.data.labels = labels;
        priceChart.data.datasets[0].data = historyData; // Actual
        priceChart.data.datasets[1].data = predictionData; // Backtest + Prediction
        priceChart.update();
    } else {
        priceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Actual Price',
                        data: historyData,
                        borderColor: '#FFD700', // Gold
                        backgroundColor: 'rgba(255, 215, 0, 0.1)',
                        borderWidth: 3,
                        pointBackgroundColor: '#fff',
                        pointRadius: 4,
                        tension: 0.3,
                        fill: true,
                        spanGaps: true
                    },
                    {
                        label: 'AI Model (Backtest & Forecast)',
                        data: predictionData,
                        borderColor: '#4dFF4d', // Green
                        borderDash: [5, 5],
                        borderWidth: 2,
                        pointBackgroundColor: '#4dFF4d',
                        pointRadius: 3,
                        tension: 0.3,
                        fill: false,
                        spanGaps: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#a1a1a1' } }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#a1a1a1' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#a1a1a1' }
                    }
                }
            }
        });
    }
    // Update history table
    updateHistoryTable(labels, historyData, predictionData);
}

function updateHistoryTable(labels, actuals, predictions) {
    const tableBody = document.getElementById('history-body');
    if (!tableBody) return;

    tableBody.innerHTML = '';

    // We want the last 6 indices (history excluding the future point)
    // The last element in labels is the future prediction.
    const historyCount = labels.length - 1;
    const startIndex = Math.max(0, historyCount - 6);

    for (let i = historyCount - 1; i >= startIndex; i--) {
        const time = labels[i];
        const actual = actuals[i];
        const predicted = predictions[i];

        if (actual === null || predicted === null) continue;

        const diff = Math.abs(actual - predicted);
        const accuracy = Math.max(0, 100 - (diff / actual * 100));

        let accClass = 'acc-mid';
        if (accuracy > 99) accClass = 'acc-high';
        else if (accuracy < 97) accClass = 'acc-low';

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${time}</td>
            <td style="font-weight: 600;">$${actual.toFixed(2)}</td>
            <td style="color: var(--cyan);">$${predicted.toFixed(2)}</td>
            <td class="${accClass}">${accuracy.toFixed(2)}%</td>
        `;
        tableBody.appendChild(row);
    }
}

// Fetch immediately and then every 10 seconds
fetchData();
setInterval(fetchData, 10000);

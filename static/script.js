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
    if (!data.chart) return;

    // Full labels for history table (12 hours)
    const fullLabels = data.chart.labels.map(ts => ts * 1000);
    const fullActuals = data.chart.prices;
    const fullPredictions = data.chart.prediction_point;

    // Slice for Chart display (6 hours history + 2 real-time/forecast points)
    // Slice for Chart display (6 history + 1 now + 1 forecast = 8 points total)
    const L = data.chart.labels.length;
    const chartSlice = L - 8;
    const labels = fullLabels.slice(chartSlice);
    const historyData = fullActuals.slice(chartSlice);
    const predictionData = fullPredictions.slice(chartSlice);

    const allValues = [...historyData.filter(v => v !== null), ...predictionData.filter(v => v !== null)];
    const yMin = Math.min(...allValues) * 0.998;
    const yMax = Math.max(...allValues) * 1.002;

    if (typeof ChartDataLabels !== 'undefined') {
        Chart.register(ChartDataLabels);
    }

    if (priceChart) {
        priceChart.data.labels = labels;
        priceChart.data.datasets[0].data = historyData;
        priceChart.data.datasets[1].data = predictionData;
        priceChart.options.scales.y.min = yMin;
        priceChart.options.scales.y.max = yMax;
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
                        borderColor: '#FFD700',
                        backgroundColor: 'rgba(255, 215, 0, 0.1)',
                        borderWidth: 3,
                        pointBackgroundColor: '#fff',
                        pointRadius: 3,
                        pointBorderWidth: 2,
                        tension: 0.3,
                        fill: true,
                        spanGaps: true
                    },
                    {
                        label: 'AI Model (Backtest & Forecast)',
                        data: predictionData,
                        borderColor: '#4dFF4d',
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
                animation: {
                    duration: 0
                },
                plugins: {
                    legend: { labels: { color: '#a1a1a1' } },
                    datalabels: {
                        color: '#fff',
                        align: 'top',
                        offset: 4,
                        font: {
                            family: 'Outfit',
                            size: 10,
                            weight: '600'
                        },
                        formatter: function (value) {
                            return value ? '$' + value.toFixed(1) : '';
                        },
                        display: function (context) {
                            // Only show for non-null values
                            return context.dataset.data[context.dataIndex] !== null;
                        }
                    }
                },
                layout: {
                    padding: {
                        top: 20,
                        bottom: 20,
                        left: 10,
                        right: 25
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#a1a1a1' }
                    },
                    x: {
                        type: 'time',
                        time: {
                            unit: 'hour',
                            stepSize: 1,
                            displayFormats: {
                                hour: 'h a'
                            },
                            tooltipFormat: 'h:mm:ss a',
                            round: 'hour'
                        },
                        grid: { display: false },
                        ticks: {
                            color: '#a1a1a1',
                            maxRotation: 0,
                            autoSkip: false,
                            maxTicksLimit: 10,
                            source: 'auto'
                        }
                    }
                }
            }
        });
    }


    // Smooth Pulse Animation (matching LIVE indicator)
    if (!window.pulseInited) {
        window.pulseInited = true;
        const animate = () => {
            if (priceChart) {
                const now = Date.now();
                const t = (now % 1500) / 1500; // 1.5s period
                const pulse = 0.5 + 0.5 * Math.cos(2 * Math.PI * t);

                const cur_L = priceChart.data.labels.length;
                if (cur_L >= 2) {
                    const glowEffect = {
                        radius: 7 + (3 * (1 - pulse)), // Size 7 to 10 (matching 10px LIVE dot)
                        alpha: 0.1 + (0.9 * (1 - pulse)), // Opacity 0.1 to 1.0
                        glow: 2 + (8 * (1 - pulse)) // Glow effect
                    };

                    // Dataset 0: Actual Price (second-to-last point)
                    priceChart.data.datasets[0].pointRadius = (c) => (c.dataIndex === cur_L - 2) ? glowEffect.radius : 3;
                    priceChart.data.datasets[0].pointBackgroundColor = (c) => (c.dataIndex === cur_L - 2) ? `rgba(255, 215, 0, ${glowEffect.alpha})` : '#FFD700';
                    priceChart.data.datasets[0].pointBorderWidth = (c) => (c.dataIndex === cur_L - 2) ? glowEffect.glow : 1;
                    priceChart.data.datasets[0].pointBorderColor = (c) => (c.dataIndex === cur_L - 2) ? `rgba(255, 215, 0, ${glowEffect.alpha * 0.3})` : 'rgba(255, 215, 0, 0.2)';

                    // Dataset 1: AI Forecast (last point)
                    priceChart.data.datasets[1].pointRadius = (c) => (c.dataIndex === cur_L - 1) ? glowEffect.radius : 3;
                    priceChart.data.datasets[1].pointBackgroundColor = (c) => (c.dataIndex === cur_L - 1) ? `rgba(77, 255, 77, ${glowEffect.alpha})` : '#4dFF4d';
                    priceChart.data.datasets[1].pointBorderWidth = (c) => (c.dataIndex === cur_L - 1) ? glowEffect.glow : 0;
                    priceChart.data.datasets[1].pointBorderColor = (c) => (c.dataIndex === cur_L - 1) ? `rgba(77, 255, 77, ${glowEffect.alpha * 0.3})` : 'transparent';
                }
                priceChart.update('none');
            }
            requestAnimationFrame(animate);
        };
        requestAnimationFrame(animate);
    }

    updateHistoryTable(fullLabels, fullActuals, fullPredictions);
}

function updateHistoryTable(labels, actuals, predictions) {
    const tableBody = document.getElementById('history-body');
    if (!tableBody) return;

    tableBody.innerHTML = '';

    // Convert ms back to localized HH:mm:ss for table
    const timeOptions = { hour: 'numeric', minute: '2-digit', hour12: true, timeZone: 'Asia/Bangkok' };
    const formatter = new Intl.DateTimeFormat('en-US', timeOptions);

    const nowMs = Date.now();
    const historyEntries = [];

    for (let i = 0; i < labels.length; i++) {
        // Only take points that are strictly in the historical group (before the real-time point)
        if (labels[i] < nowMs - 120000) {
            historyEntries.push({
                ts: labels[i],
                actual: actuals[i],
                predicted: predictions[i]
            });
        }
    }

    // Show 6 latest historical entries
    const displayList = historyEntries.slice(-6).reverse();

    displayList.forEach(entry => {
        const timeStr = formatter.format(new Date(entry.ts));
        const actual = entry.actual;
        const predicted = entry.predicted;

        if (actual === null || predicted === null) return;

        const diff = Math.abs(actual - predicted);
        const accuracy = Math.max(0, 100 - (diff / actual * 100));

        let accClass = 'acc-mid';
        if (accuracy > 99) accClass = 'acc-high';
        else if (accuracy < 97) accClass = 'acc-low';

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${timeStr}</td>
            <td style="font-weight: 600;">$${actual.toFixed(2)}</td>
            <td style="color: var(--cyan);">$${predicted.toFixed(2)}</td>
            <td class="${accClass}">${accuracy.toFixed(2)}%</td>
        `;
        tableBody.appendChild(row);
    });
}

// Fetch immediately and then every 10 seconds
fetchData();
setInterval(fetchData, 10000);

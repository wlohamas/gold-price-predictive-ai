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
            if (data.forecast_time) {
                document.getElementById('forecast-time').innerText = data.forecast_time;
            }

            if (data.accuracy !== undefined) {
                document.getElementById('accuracy-rate').innerText = `${data.accuracy.toFixed(1)}%`;
                if (data.accuracy_reason) {
                    document.getElementById('accuracy-reason').innerText = data.accuracy_reason;
                }

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
                const lastUpdatedEl = document.getElementById('news-last-updated');

                if (lastUpdatedEl && data.news_last_updated) {
                    lastUpdatedEl.innerText = `Refreshed: ${data.news_last_updated}`;
                }

                if (newsList) {
                    newsList.innerHTML = '';
                    data.market_news.forEach(news => {
                        const impactColor = news.impact === 'Positive' ? 'var(--green)' : news.impact === 'Negative' ? 'var(--red)' : '#FDB931';
                        const item = document.createElement('div');
                        item.style.padding = '10px';
                        item.style.borderLeft = `4px solid ${impactColor}`;
                        item.style.background = 'rgba(255,255,255,0.02)';
                        item.style.fontSize = '0.9rem';

                        const newsLink = news.link || "https://www.investing.com/news/commodities/gold";
                        item.innerHTML = `<a href="${newsLink}" target="_blank" style="text-decoration: none; display: block;">
                                            <b style="color: #fff; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.1);">${news.title}</b>
                                          </a>
                                          <span style="color: ${impactColor}; font-weight: bold;">[${news.impact}]</span><br>
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

    // Slice for Chart display: Show only latest 6 points (5 hours history + 1 forecast)
    // Safety check: ensure chartSlice is at least 0.
    const L = data.chart.labels.length;
    const chartSlice = Math.max(0, L - 6);
    const labels = fullLabels.slice(chartSlice);
    const historyData = fullActuals.slice(chartSlice);
    const predictionData = fullPredictions.slice(chartSlice);

    // Calculate Performance Data for Accuracy Chart
    // Line 1: Actual (Target) = Always 100%
    // Line 2: Predicted = Model Accuracy %
    const actualPerf = labels.map(() => 100);
    const predictedPerf = labels.map((_, i) => {
        const actual = historyData[i];
        const predicted = predictionData[i];
        if (actual === null || predicted === null || actual === 0) return null;
        const diff = Math.abs(actual - predicted);
        return Math.max(0, 100 - (diff / actual * 100));
    });

    const yMin = 0;
    const yMax = 100;

    if (typeof ChartDataLabels !== 'undefined') {
        Chart.register(ChartDataLabels);
    }

    if (priceChart) {
        priceChart.data.labels = labels;
        priceChart.data.datasets[0].data = actualPerf;
        priceChart.data.datasets[1].data = predictedPerf;
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
                        label: 'Actual (Target 100%)',
                        data: actualPerf,
                        borderColor: '#FFD700',
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        pointRadius: 0,
                        tension: 0,
                        fill: false
                    },
                    {
                        label: 'AI prediction Performance (%)',
                        data: predictedPerf,
                        borderColor: '#4dFF4d',
                        backgroundColor: 'rgba(77, 255, 77, 0.1)',
                        borderWidth: 3,
                        pointBackgroundColor: '#4dFF4d',
                        pointRadius: 4,
                        tension: 0.3,
                        fill: true,
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
                        formatter: function (value, context) {
                            if (context.datasetIndex === 0) return ''; // Hide 100% labels
                            return value ? value.toFixed(1) + '%' : '';
                        },
                        display: function (context) {
                            // Show Accuracy for AI Prediction points only
                            return context.datasetIndex === 1 && context.dataset.data[context.dataIndex] !== null;
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
                        beginAtZero: true,
                        min: 0,
                        max: 100,
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: {
                            color: '#a1a1a1',
                            stepSize: 20,
                            callback: function (value) { return value + '%'; }
                        }
                    },
                    x: {
                        type: 'time',
                        time: {
                            unit: 'hour',
                            stepSize: 1,
                            displayFormats: {
                                hour: 'h a'
                            },
                            tooltipFormat: 'h:mm:ss a'
                        },
                        grid: { display: false },
                        ticks: {
                            color: '#a1a1a1',
                            maxRotation: 0,
                            autoSkip: false,
                            maxTicksLimit: 6,
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

                // Real-time "Streaming Jitter" for Actual Price
                // Uses sine wave + small noise to vibrate vertically without drifting
                const streamOscillation = Math.sin(now / 200) * 0.15;
                const microNoise = (Math.random() - 0.5) * 0.05;
                const totalJitter = streamOscillation + microNoise;

                const cur_L = priceChart.data.labels.length;

                if (cur_L >= 2) {
                    const glowEffect = {
                        radius: 8,
                        alpha: 0.1 + (0.9 * (1 - pulse)),
                        glow: 2 + (8 * (1 - pulse))
                    };

                    // Pulse for AI Prediction Accuracy (Dataset 1)
                    priceChart.data.datasets[1].pointRadius = (c) => (c.dataIndex === cur_L - 2) ? glowEffect.radius : 4;
                    priceChart.data.datasets[1].pointBackgroundColor = (c) => (c.dataIndex === cur_L - 2) ? `rgba(77, 255, 77, ${glowEffect.alpha})` : '#4dFF4d';
                    priceChart.data.datasets[1].pointBorderWidth = (c) => (c.dataIndex === cur_L - 2) ? glowEffect.glow : 1;
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

// Fetch immediately and then every 2.5 seconds for real-time movement
fetchData();
setInterval(fetchData, 2500);

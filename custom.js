window.onload = function() {
    const url = "https://opendata.dc.gov/api/download/v1/items/70392a096a8e431381f1f692aaa06afd/csv?layers=24";

    // Fetch data from the URL
    fetch(url)
        .then(response => response.text())
        .then(data => {
            const csvData = Papa.parse(data, { header: true, dynamicTyping: true });
            const df = csvData.data;

            // Preprocess the data
            df.forEach(row => {
                if (row.REPORTDATE) {
                    row.REPORTDATE = new Date(row.REPORTDATE);
                    row.YearMonth = row.REPORTDATE.getFullYear() + '-' + (row.REPORTDATE.getMonth() + 1).toString().padStart(2, '0');
                }
            });

            // Filter data between 2020 and 2025
            const filteredData = df.filter(row => row.REPORTDATE.getFullYear() >= 2020 && row.REPORTDATE.getFullYear() <= 2025);

            // Generate heatmap
            const heatmapData = generateHeatmapData(filteredData);
            plotHeatmap(heatmapData);

            // Initialize map
            const map = L.map('map').setView([38.89511, -77.03637], 11);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

            // Plot accidents by severity on the map
            plotMap(filteredData, map);

            // Bar Chart
            const barData = generateBarChartData(filteredData);
            plotBarChart(barData);

            // Time Series Chart
            const timeSeriesData = generateTimeSeriesData(filteredData);
            plotTimeSeries(timeSeriesData);

            // Event listener for the dropdown
            document.querySelector('#severity-dropdown').addEventListener('change', function(e) {
                const selectedSeverity = e.target.value;
                const filteredBySeverity = selectedSeverity === 'All' ? filteredData : filteredData.filter(row => row.CrashSeverity === selectedSeverity);
                plotMap(filteredBySeverity, map);
            });
        });
};

function generateHeatmapData(data) {
    // Implement logic to prepare data for heatmap
}

function plotHeatmap(data) {
    // Use Plotly to create a heatmap
    const trace = {
        z: data.map(row => row.incidents),  // Update according to actual data
        x: data.map(row => row.month),  // Update according to actual data
        y: data.map(row => row.ward),  // Update according to actual data
        type: 'heatmap'
    };

    const layout = {
        title: 'Heatmap of Incidents',
        xaxis: { title: 'Month' },
        yaxis: { title: 'Ward' }
    };

    Plotly.newPlot('heatmap', [trace], layout);
}

function plotMap(data, map) {
    data.forEach(row => {
        const marker = L.marker([row.LATITUDE, row.LONGITUDE]).addTo(map);
        marker.bindPopup(`Severity: ${row.CrashSeverity}`);
    });
}

function generateBarChartData(data) {
    // Implement logic for bar chart data
}

function plotBarChart(data) {
    const trace = {
        x: data.map(row => row.ward),  // Update according to actual data
        y: data.map(row => row.incidents),  // Update according to actual data
        type: 'bar'
    };

    const layout = {
        title: 'Accidents per Ward',
        xaxis: { title: 'Ward' },
        yaxis: { title: 'Number of Accidents' }
    };

    Plotly.newPlot('bar-chart', [trace], layout);
}

function generateTimeSeriesData(data) {
    // Implement logic for time series data
}

function plotTimeSeries(data) {
    const trace = {
        x: data.map(row => row.yearMonth),  // Update according to actual data
        y: data.map(row => row.incidents),  // Update according to actual data
        mode: 'lines+markers',
        name: 'Incidents'
    };

    const layout = {
        title: 'Monthly Incidents and Injuries Over Time',
        xaxis: { title: 'Year-Month' },
        yaxis: { title: 'Incidents & Injuries' }
    };

    Plotly.newPlot('time-series', [trace], layout);
}

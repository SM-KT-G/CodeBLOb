<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ data.title | default('My Dashboard') }}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        {% for metric in data.metrics %}
        <div class="card">
            <h2>{{ metric.name }}</h2>
            <p class="value">{{ metric.value }}</p>
        </div>
        {% endfor %}
    </div>

    <div class="container">
        <div class="card">
            <h2>Sales Chart</h2>
            <canvas id="myChart"></canvas>
        </div>
    </div>
</body>
</html>
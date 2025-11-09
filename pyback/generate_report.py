<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ data.title | default('My Dashboard') }}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <header>
        <h1>{{ data.title | default('My Dashboard') }}</h1> </header>
    
    <div class="container">
        {% for metric in data.metrics %}
        <div class="card">
            <h2>{{ metric.name }}</h2>
            <p class="value">{{ metric.value }}</p>
        </div>
        {% endfor %}
    </div>
</body>
</html>
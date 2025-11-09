<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Dashboard</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <header>
        <h1>My Simple Dashboard</h1>
    </header>
    
    <div class="container">
        <div class="card">
            <h2>Card 1</h2>
            <p>Some data point.</p>
        </div>
        <div class="card">
            <h2>Card 2</h2>
            <p>Another data point.</p>
        </div>
    </div>
</body>
</html>
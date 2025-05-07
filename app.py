<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PDF Certificate Extractor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .certificate-card {
            border-left: 4px solid #0d6efd;
            margin-bottom: 20px;
        }
    </style>
</head>
<body class="bg-light">
<div class="container mt-5">
    <h2 class="mb-4">Upload Certificate PDFs</h2>
    
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            <div class="alert alert-warning">
                {% for message in messages %}
                    <p>{{ message }}</p>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}
    
    <form method="post" enctype="multipart/form-data">
        <div class="mb-3">
            <label class="form-label">Select up to 3 certificate PDFs:</label>
            <input class="form-control" type="file" name="pdf_files" accept=".pdf" multiple required>
            <div class="form-text">Hold Ctrl/Cmd to select multiple files</div>
        </div>
        <button class="btn btn-primary" type="submit">Extract Information</button>
    </form>

    {% if extracted_data %}
        <hr>
        <h4 class="mt-4">Extracted Certificates:</h4>
        
        {% for extracted in extracted_data %}
        <div class="card certificate-card mb-3">
            <div class="card-body">
                <h5 class="card-title">{{ extracted['Filename'] }}</h5>
                <ul class="list-group list-group-flush">
                    <li class="list-group-item"><strong>Name:</strong> {{ extracted['Name'] }}</li>
                    <li class="list-group-item"><strong>Course Title:</strong> {{ extracted['Course Title'] }}</li>
                    <li class="list-group-item"><strong>Completion Date:</strong> {{ extracted['Completion Date'] }}</li>
                </ul>
                <div class="mt-3">
                    <button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="collapse" 
                            data-bs-target="#rawText{{ loop.index }}">
                        Show Raw Text
                    </button>
                    <div class="collapse mt-2" id="rawText{{ loop.index }}">
                        <pre class="bg-dark text-white p-3 rounded">{{ extracted['Raw Text'] }}</pre>
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
    {% endif %}
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>

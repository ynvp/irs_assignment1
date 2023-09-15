from flask import *
app = Flask(__name__)


@app.route('/')
def main():
    return render_template("./index.html")

@app.route('/upload_query', methods=['POST'])
def upload_query():
    if request.method == 'POST':
        # Get the list of files from webpage
        files = request.files.getlist("file")

        # Iterate for each file in the files List, and Save them
        for file in files:
            file.save(file.filename)
        return render_template("query.html")

@app.route('/query_result', methods=['POST'])
def query_result():
    if request.method == 'POST':
        query = request.form.get("query")
        return render_template("results.html", query=query)

if __name__ == '__main__':
    app.run(debug=True)
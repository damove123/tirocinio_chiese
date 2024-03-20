from flask import Flask, render_template
import csv

app = Flask(__name__)


@app.route('/')
def index():
    data = []
    with open('/Users/albi/Desktop/Università/tirocinio_chiese/fileExcel/Chiese.CSV', 'r', encoding='latin-1') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            data.append(row)
    return render_template('index.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)

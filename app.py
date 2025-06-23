from flask import Flask, render_template_string
import os
import requests
import csv
import threading
import time

app = Flask(__name__)

# URL of the CSV file
csv_url = "https://www.atmos.albany.edu/products/nysm/nysm_latest.csv"

# Directory to save the file
save_directory = "/Users/swrcc/Downloads/cams/NYSMcsv"
file_name = "nysm_latest.csv"
file_path = os.path.join(save_directory, file_name)

# Global variable to store all accumulated data
accumulated_data = []
headers = []

def download_csv(url, save_path):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes

        # Write the content to a file
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully and saved to {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file: {e}")

def append_csv_data(file_path):
    global accumulated_data, headers
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        if not headers:
            headers = next(reader)  # Get the headers only once
        else:
            next(reader)  # Skip headers for subsequent files
        for row in reader:
            accumulated_data.append(row)

def periodic_download(interval, url, save_path):
    while True:
        try:
            download_csv(url, save_path)
        except Exception as e:
            print(f"Error in periodic download: {e}")
        time.sleep(interval)

def start_periodic_download():
    # Start a background thread to download the CSV every 5 minutes and 30 seconds
    interval = 5 * 60 + 30  # 5 minutes and 30 seconds in seconds
    thread = threading.Thread(target=periodic_download, args=(interval, csv_url, file_path), daemon=True)
    thread.start()

# Start the periodic download thread when the app starts
start_periodic_download()

@app.route("/")
def display_csv():
    # Ensure the directory exists and download the CSV
    os.makedirs(save_directory, exist_ok=True)
    download_csv(csv_url, file_path)

    # Append the new CSV data to the accumulated data
    append_csv_data(file_path)

    # Render the accumulated data in an HTML table
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NYSM Data</title>
    </head>
    <body>
        <h1>NYSM Accumulated Data</h1>
        <table border="1">
            <thead>
                <tr>
                    {% for header in headers %}
                    <th>{{ header }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for row in accumulated_data %}
                <tr>
                    {% for cell in row %}
                    <td>{{ cell }}</td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """
    return render_template_string(html_template, headers=headers, accumulated_data=accumulated_data)

if __name__ == "__main__":
    app.run(debug=True)

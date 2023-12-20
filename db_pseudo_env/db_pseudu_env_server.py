from flask import Flask, request, jsonify, render_template_string
import csv
import os

app = Flask(__name__)

# Directory to save the records file
file_path = os.path.abspath(__file__)
directory = os.path.dirname(file_path)
tasks_history_dir = directory + "/tasks_history"

if not os.path.exists(tasks_history_dir):
    os.makedirs(tasks_history_dir)

def save_record(task_id, task_content, reply):
    record_file = os.path.join(tasks_history_dir, f"history.csv")
    fieldnames = ['Index', 'Task ID', 'Task Content', 'Reply']
    new_index = 1

    # Check if file exists and determine the new index
    if os.path.exists(record_file):
        with open(record_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            if rows:
                new_index = int(rows[-1]['Index']) + 1

    # Write the new record
    with open(record_file, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerow({'Index': new_index, 'Task ID': task_id, 'Task Content': task_content, 'Reply': reply})


# HTML template for displaying the text with AJAX for form submission
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Task {{ task_id }}</title>
    <script>
        function sendReply() {
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/reply?task_id={{ task_id }}", true);
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.onreadystatechange = function() {
                if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
                    alert("Reply sent successfully");
                }
            }
            var replyText = document.getElementById("reply_text").value;
            xhr.send("reply_text=" + encodeURIComponent(replyText));
        }
    </script>
</head>
<body>
    <h1>Task ID</h1>
    <h2>{{ task_id }}</h2>
    <h1>Task Content:</h1>
    <p>{{ task_content }}</p>

    <h1>Input the DB env results</h1>
    <textarea id="reply_text" rows="10" cols="50"></textarea><br>
    <button onclick="sendReply()">Reply</button>
</body>
</html>
"""

# Global Variables
task_id = -1
task_content = ""
replies = {}

@app.route('/task', methods=["GET", "POST"])
def receive_text():
    global task_id
    global task_content
    if request.method == "POST":
        data = request.json
        task_id = data['task_id']
        task_content = data['task_content']
        #replies[task_id] = None  # Initialize reply as None
        return render_template_string(html_template, task_id=task_id, task_content=task_content)
    else:
        return render_template_string(html_template, task_id=task_id, task_content=task_content)

@app.route('/reply', methods=['POST'])
def reply():
    reply_text = request.form['reply_text']
    #task_id = request.args.get('task_id')
    replies[task_id] = reply_text

    # Save the record to the file
    save_record(task_id, task_content, reply_text)
    return 'Reply received'

@app.route('/result', methods=['GET'])
def get_reply():
    task_id = request.args.get('task_id')
    reply = replies.get(task_id, 'No reply yet')
    #print(f"Task[{task_id}]: {reply}")
    return jsonify({'task_id':task_id, 'response': reply})

if __name__ == '__main__':
    app.run(debug=True)

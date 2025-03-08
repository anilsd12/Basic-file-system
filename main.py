from flask import Flask, request, jsonify, render_template,redirect,url_for
import os

app = Flask(__name__)

# Stack to manage undo/redo
history_stack = []
redo_stack = []

@app.route('/')
def home():
    return render_template('home.html')


# Variable to store the latest result for the results page
latest_result = {}

@app.route('/perform', methods=['POST'])
def perform():
    operation = request.form.get('operation')
    path = request.form.get('path')
    data = request.form.get('data', '')

    if not path and operation not in ["undo", "redo"]:
        return jsonify({"error": "File name is required"}), 400

    try:
        # Initialize response object
        response = {}

        # Handle the operations
        if operation == 'create':
            response = {"message": create_file(path)}
        elif operation == 'write':
            response = {"message": write_file(path, data)}
        elif operation == 'read':
            file_content = read_file(path)
            response = {"operation": "read", "content": file_content}
        elif operation == 'delete':
            response = {"message": delete_file(path)}
        elif operation == 'undo':
            response = {"message": undo_operation()}
        elif operation == 'redo':
            response = {"message": redo_operation()}
        else:
            response = {"error": "Invalid operation"}

    except Exception as e:
        response = {"error": str(e)}

    # Render result page with the response
    return render_template('result.html', result=response)




# File Operations
def create_file(path):
    if os.path.exists(path):
        return {"error": "File already exists"}
    open(path, 'w').close()
    history_stack.append(('delete', path, None))
    return {"message": f"File '{path}' created successfully"}

def write_file(path, data):
    if not os.path.exists(path):
        return {"error": "File does not exist"}
    with open(path, 'w') as file:
        previous_content = file.read() if os.path.getsize(path) > 0 else None
        file.write(data)
    history_stack.append(('write', path, previous_content))
    return {"message": f"Data written to '{path}'"}

def read_file(path):
    try:
        with open(path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        raise Exception("File does not exist")
    except Exception as e:
        raise Exception(f"Error reading file: {e}")


def delete_file(path):
    if not os.path.exists(path):
        return {"error": "File does not exist"}
    with open(path, 'r') as file:
        content = file.read()
    os.remove(path)
    history_stack.append(('create', path, content))
    return {"message": f"File '{path}' deleted successfully"}

# Undo and Redo
def undo_operation():
    if not history_stack:
        return {"error": "Nothing to undo"}
    operation, path, data = history_stack.pop()
    if operation == 'delete':
        open(path, 'w').close()
        redo_stack.append(('delete', path, None))
    elif operation == 'write':
        with open(path, 'w') as file:
            file.write(data if data else '')
        redo_stack.append(('write', path, None))
    elif operation == 'create':
        os.remove(path)
        redo_stack.append(('create', path, data))
    return {"message": f"Undo '{operation}' operation on '{path}'"}

def redo_operation():
    if not redo_stack:
        return {"error": "Nothing to redo"}
    operation, path, data = redo_stack.pop()
    if operation == 'delete':
        os.remove(path)
    elif operation == 'write':
        with open(path, 'w') as file:
            file.write(data if data else '')
    elif operation == 'create':
        open(path, 'w').close()
    history_stack.append((operation, path, data))
    return {"message": f"Redo '{operation}' operation on '{path}'"}


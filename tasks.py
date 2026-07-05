from flask import jsonify, request, Blueprint
from database import get_db_connection
from auth import token_required

tasks = Blueprint("tasks", __name__)

@tasks.route("/todos", methods=["POST"])
@token_required
def create_todo(user_id):
    try:
        task = request.get_json()

        if not task:
            return jsonify({"error": "Please enter a valid information"})
        
        title = task.get("title")
        description = task.get("description")

        if not title:
            return jsonify({"error": "Please give a Title to your task"}), 400
        if not description:
            return jsonify({"error": "Please give a description to your task"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (user_id, title, description) VALUES (?, ?, ?)", (user_id, title, description))
        conn.commit()
        job_id = cursor.lastrowid
        conn.close()
        
        job = {
            "id": job_id,
            "title": title,
            "description": description
        }
        return jsonify({"message": "Task added successfully",
                        "job": job}), 201
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@tasks.route("/todos", methods=["GET"])
@token_required
def print_tasks(user_id):
    try:
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)
        completed = request.args.get("completed")
        offset = (page - 1) * limit
        conn = get_db_connection()
        state = 1 if completed == "true" else 0

        if completed is None:
            total = conn.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (user_id,)).fetchone()[0]
            data = conn.execute("SELECT * FROM tasks WHERE user_id = ? LIMIT ? OFFSET ?", (user_id, limit, offset)).fetchall()
        else:
            total = conn.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND completed = ?", (user_id, state)).fetchone()[0]
            data = conn.execute("SELECT * FROM tasks WHERE user_id = ? AND completed = ? LIMIT ? OFFSET ?", (user_id, state, limit, offset)).fetchall()
        
        conn.close()

        return jsonify({"message": "Here are the registered tasks",
                        "page": page,
                        "limit": limit,
                        "total": total, 
                        "the_tasks": [dict(job) for job in data]}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@tasks.route("/todos/<int:task_id>", methods=["GET"])
@token_required
def get_task(user_id, task_id):
    try:
        conn = get_db_connection()
        job = conn.execute("SELECT * FROM tasks WHERE user_id = ? AND id = ?", (user_id, task_id)).fetchone()

        if not job:
            conn.close()
            return jsonify({"error": "There is not task with such id, please check again"}), 404
        conn.close()

        return jsonify({"message": f"Here is the task #{task_id}",
                    "task": dict(job)}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@tasks.route("/todos/<int:task_id>", methods=["PUT"])
@token_required
def update_task(user_id, task_id):
    try:
        task = request.get_json()

        if not task:
            return jsonify({"error": "Please enter a valid information to update the task"})

        conn = get_db_connection()

        title = task.get("title")
        description = task.get("description")
        completed = task.get("completed")

        does_exist = conn.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id)).fetchone()

        if not does_exist:
            conn.close()
            return jsonify({"error": "Task not found"}), 404

        if title:   
            conn.execute("UPDATE tasks SET title = ? WHERE id = ? AND user_id = ?", (title, task_id, user_id))
        if description:           
            conn.execute("UPDATE tasks SET description = ? WHERE id = ? AND user_id = ?", (description, task_id, user_id))
        if completed is not None: 
            conn.execute("UPDATE tasks SET completed = ? WHERE id = ? AND user_id = ?", (completed, task_id, user_id))
        
        conn.commit()
        conn.close()
        return jsonify({"message": "Task updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@tasks.route("/todos/<int:task_id>", methods=["DELETE"])
@token_required
def delete_task(user_id, task_id):
    try:
        conn = get_db_connection()
        task = conn.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id)).fetchone()

        if not task:
            conn.close()
            return jsonify({"error": "Task not found"}), 404
        
        conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
        conn.commit()
        conn.close()
        
        return "", 204
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
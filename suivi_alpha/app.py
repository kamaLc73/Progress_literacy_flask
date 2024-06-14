from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, json, hashlib
from datetime import datetime
import sqlite3
from statistique import statistique 

app = Flask(__name__)
app.secret_key = 'secret'

###############################################

@app.route("/", methods=['GET'])
def home():
    if 'user_id' in session:
        user_id = session['user_id']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM user WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        conn.close()

        if user:
            if user[3] == "user":
                return render_template('QuizChoice.html', username=user[1])
            else:
                return redirect(url_for('mainAdmin'))
    return render_template("login.html")

###############################################

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            hashed_password_from_db = user[2]
            hashed_password_input = hashlib.sha256(password.encode()).hexdigest()
            
            if hashed_password_from_db == hashed_password_input:
                session['user_id'] = user[0]
                if user[3] == "user":
                    conn.close()
                    return render_template("QuizChoice.html", username=username)
                else:
                    conn.close()
                    return redirect(url_for('mainAdmin'))
            else:
                error = "Nom d'utilisateur ou mot de passe invalide. Veuillez réessayer."
                return render_template("login.html", error=error)
        else:
            error = "Nom d'utilisateur ou mot de passe invalide. Veuillez réessayer."
            return render_template("login.html", error=error)
    else:
        return redirect(url_for('home'))

###############################################

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        user_type = request.form.get("user_type")
        
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        age = request.form.get("age")
        sexe = request.form.get("sexe")
        milieu = request.form.get("milieu")
        classe_sociale = request.form.get("classe_sociale")
        niveau_initial = request.form.get("niveau_initial")
        methodeApprentissage = request.form.get("methodeApprentissage")

        if password != confirmation:
            error = "Les mots de passe ne correspondent pas. Veuillez réessayer."
            return render_template("register.html", error=error)
        
        if user_type not in ['user', 'admin']:
            error = "Sélectionnez un type d'utilisateur. Veuillez réessayer."
            return render_template("register.html", error=error)
        
        if user_type == 'user':
            if sexe not in ['M', 'F']:
                error = "Sélectionnez un sexe. Veuillez réessayer."
                return render_template("register.html", error=error) 

            if milieu not in ['urbain', 'rural', 'suburbain']:
                error = "Sélectionnez un milieu. Veuillez réessayer."
                return render_template("register.html", error=error) 

            if classe_sociale not in ['c1', 'c2', 'c3']:
                error = "Sélectionnez une classe sociale. Veuillez réessayer."
                return render_template("register.html", error=error) 

            if niveau_initial not in ['n1', 'n2', 'n3', 'n4', 'n5']:
                error = "Sélectionnez un niveau initial. Veuillez réessayer."
                return render_template("register.html", error=error) 

            if methodeApprentissage not in ['m1', 'm2', 'm3', 'm4', 'm5']:
                error = "Sélectionnez une méthode d'apprentissage. Veuillez réessayer."
                return render_template("register.html", error=error) 
                   
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO user (username, password, type) 
                VALUES (?, ?, ?)""",
                (username, hashed_password, user_type)
            )
            conn.commit()  

            cursor.execute('SELECT id FROM user WHERE username = ?', (username,))
            user_id = cursor.fetchone()[0]
            session['user_id'] = user_id

            if user_type == "user":
                cursor.execute("""
                    INSERT INTO apprenant (nom, prenom, age, classe_sociale, milieu, niveau_initial, sexe, methodeApprentissage, id_user) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (nom, prenom, age, classe_sociale, milieu, niveau_initial, sexe, methodeApprentissage, user_id)
                )
                conn.commit()
                conn.close()
                return render_template('QuizChoice.html', username=username)
            else:
                conn.close()
                return redirect(url_for('mainAdmin'))
            
        except sqlite3.IntegrityError as e:
            print("Error:", e)  
            error = "Le nom d'utilisateur existe déjà. Veuillez réessayer avec un nom d'utilisateur différent."
            return render_template("register.html", error=error)
    else:
        if 'user_id' in session:
            return redirect(url_for('home'))
        else: 
            return render_template("register.html")

###############################################

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

###############################################

@app.route("/quizChoice", methods=['POST', 'GET'])
def quizChoice():
    if request.method == 'POST':
        username = request.form.get("username")
        quiz_type = request.form.get("quiztype")
        with open("static/questions.json", "r", encoding='utf-8') as json_file:
            questions_data = json.load(json_file)
            questions = questions_data["questions"].get(quiz_type, [])

        return render_template("quiz.html", username=username, quiz_type=quiz_type, questions=questions)
    else:
        return redirect(url_for('home'))
    
###############################################

@app.route("/resultatQuiz", methods=['POST', 'GET'])
def resultatQuiz():
    if request.method == 'POST':
        try:
            username = request.form.get("username")
            quiz_type = request.form.get("quiz_type")
            duree = request.form.get("StartQuizTime")
            score = 0

            with open("static/questions.json", "r", encoding='utf-8') as json_file:
                questions_data = json.load(json_file)
                correct_answers = questions_data.get("answers", {}).get(quiz_type, [])

            for i in range(1, 21):
                user_answer = request.form.get(f"answer_{i}")
                if user_answer in correct_answers:
                    score += 1

            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO quiz (type, datetime, duree, score, id_user) VALUES (?, ?, ?, ?, ?)",
                (quiz_type, current_datetime, duree, score, session.get("user_id"))
            )
            conn.commit()
            conn.close()

            return redirect(url_for('resultatQuiz'))

        except Exception as e:
            print("Une erreur s'est produite:", e)
            return "Une erreur s'est produite lors du traitement de votre demande."

    else:
        if 'user_id' in session:
            try:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT type, score, datetime, duree FROM quiz WHERE id_user = ? ORDER BY id DESC LIMIT 1",
                    (session.get("user_id"),)
                )
                quiz_data = cursor.fetchone()

                cursor.execute(
                    "SELECT username FROM user WHERE id = ?",
                    (session.get("user_id"),)
                )
                username_result = cursor.fetchone()

                conn.close()

                if quiz_data:
                    quiz_type, score, quiz_date, duree = quiz_data
                    username = username_result[0] if username_result else "Anonymous"
                    return render_template(
                        'quizResult.html', 
                        username=username, 
                        quiz_type=quiz_type, 
                        score=score, 
                        date=quiz_date, 
                        duree=duree
                    )
                else:
                    return "No quiz data available."
            except Exception as e:
                print("Une erreur s'est produite:", e)
                return "Une erreur s'est produite lors du traitement de votre demande."
        else:
            return redirect(url_for('home'))

###############################################

@app.route("/voirResults", methods=["GET"])
def voirResults():
    if request.method == 'GET' and 'user_id' in session:
        user_id = session['user_id']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT username FROM user WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if user:
            username = user[0]
            
            cursor.execute("SELECT type, score, duree, datetime FROM quiz WHERE id_user = ? ORDER BY datetime DESC", (user_id,))
            quizzes = cursor.fetchall()
            
            conn.close()
            
            return render_template("voirResults.html", username=username, quizzes=quizzes)
        else:
            conn.close()
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

###############################################

@app.route("/mainAdmin", methods=["GET"])
def mainAdmin():
    if request.method == "GET" and 'user_id' in session:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT a.id, nom, prenom, age, classe_sociale, milieu,
                   niveau_initial, sexe, methodeApprentissage, u.username,
                   COUNT(q.id) AS quiz_count, u.id
            FROM apprenant a
            JOIN user u ON a.id_user = u.id
            LEFT JOIN quiz q ON a.id_user = q.id_user
            GROUP BY a.id, nom, prenom, age, classe_sociale, milieu,
                     niveau_initial, sexe, methodeApprentissage, u.username
        ''')
        apprenant = cursor.fetchall()

        cursor.execute("SELECT username FROM user WHERE id = ?", (session['user_id'],))
        username = cursor.fetchone()

        conn.close()

        return render_template("MainAdmin.html", apprenant=apprenant, username=username[0])
    else:
        return redirect(url_for('home'))
###############################################

@app.route("/userResultat", methods=["GET"])
def userResultat():
    if 'user_id' in session:
        user_id = request.args.get("id")  # Use request.args for GET parameters
        
        if not user_id:
            return redirect(url_for('home'))
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT username FROM user WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        cursor.execute("SELECT username FROM user WHERE id = ?", (session['user_id'],))
        admin = cursor.fetchone()
        
        if user:
            username = user[0]
            adname = admin[0]
             
            cursor.execute("SELECT type, score, duree, datetime FROM quiz WHERE id_user = ? ORDER BY datetime DESC", (user_id,))
            quizzes = cursor.fetchall()
            
            conn.close()
            
            return render_template("voirResults.html", admin=adname, username=username, quizzes=quizzes)
        else:
            conn.close()
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

###############################################

@app.route("/voirProgression", methods=["GET"])
def voirProgression():
    if request.method == "GET" and 'user_id' in session:
        username = request.args.get("username") 
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM user WHERE id = ?", (session['user_id'],))
        admin = cursor.fetchone()[0]  
        s = statistique()
        s.statistiquePr(username=username)
        return render_template("voirProgression.html", admin=admin, username=username)
    else:
        return redirect(url_for('home'))
    
###############################################

@app.route("/statistiquesAp", methods=["GET"])
def statistiquesAp():
    if 'user_id' in session and request.method == "GET":
        critere = request.args.get("critere", "age")  
        stats = statistique()
        stats.statistiquesAp(x=critere)
        return render_template("statistiquesAp.html")
    else:
        return redirect(url_for('home'))


###############################################

@app.route("/statistiquesQu", methods=["GET"])
def statistiquesQu():
    if 'user_id' in session and request.method == "GET":
        critere = request.args.get("critere", "age")  
        stats = statistique()
        stats.statistiquesQu(x=critere)
        return render_template("statistiquesQu.html")
    else:
        return redirect(url_for('home'))

###############################################

if __name__ == "__main__":
    app.run(debug=True)
    
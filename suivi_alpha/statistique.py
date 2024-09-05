import sqlite3
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import os

matplotlib.use('Agg')

class statistique():
    def __init__(self):
        stats_dir = os.path.join('static/img', 'stats')
        if not os.path.exists(stats_dir):
            os.makedirs(stats_dir)

    def statistiquesAp(self, x):
        conn = sqlite3.connect('static/database.db')
        apprenant = pd.read_sql("SELECT * FROM apprenant", conn)
        conn.close()
        plt.figure(figsize=(10, 6))
        sns.histplot(apprenant, x=x, discrete=True)
        plt.xlabel(x)
        plt.ylabel('Nombre d\'apprenants')
        plt.title(f'Distribution des apprenants par {x}')
        plot_path = os.path.join('static/img/stats', 'apprenant.png')
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()
    
    def statistiquesQu(self, x):
        conn = sqlite3.connect('static/database.db')
        quiz = pd.read_sql("SELECT * FROM quiz", conn)
        apprenant = pd.read_sql("SELECT * FROM apprenant", conn)
        conn.close()
        data = pd.merge(quiz, apprenant, how="inner", on="id_user")
        data.drop(['id_x','id_y','nom','prenom'], axis=1, inplace=True)
        data = data.set_index("id_user")
        data.groupby(x).describe()["score"]
        mean_scores_by_ma = data.groupby(x)['score'].mean().reset_index()
        plt.figure(figsize=(12, 6))
        sns.barplot(data=mean_scores_by_ma, x=x, y='score', hue=x, palette='viridis', legend=False)
        plt.xlabel(x)
        plt.ylabel('Moyenne des scores')
        plt.title(f'Moyenne des scores des apprenants par {x}')
        plot_path = os.path.join('static/img/stats', 'quiz.png')
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()

    def statistiquePr(self, username):
        conn = sqlite3.connect('static/database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
        user_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT * FROM quiz WHERE id_user = ? ORDER BY datetime", (user_id,))
        quiz_data = cursor.fetchall()
        
        conn.close()

        columns = [column[0] for column in cursor.description]
        quiz_df = pd.DataFrame(quiz_data, columns=columns)
        quiz_df['nb'] = range(1, len(quiz_df) + 1)

        plt.figure(figsize=(10, 6))
        sns.lineplot(x="nb", y="score", hue="type", markers=True, dashes=True, data=quiz_df)
        plt.xlabel('Nombre de quiz')  
        plt.ylabel('Score')           
        plt.title('Score des Quizs') 
        plt.grid(True)  

        plot_path = os.path.join('static/img/stats', 'plot.png')
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()     
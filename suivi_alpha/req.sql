/*==============================================================*/
/* Table : "USER"                                               */
/*==============================================================*/
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(25) NOT NULL UNIQUE,
    password VARCHAR(25) NOT NULL,
    type VARCHAR(10) NOT NULL
);

/*==============================================================*/
/* Table : APPRENANT                                            */
/*==============================================================*/
CREATE TABLE apprenant (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    age INTEGER DEFAULT NULL,
    classe_sociale TEXT DEFAULT NULL,
    milieu TEXT DEFAULT NULL,
    niveau_initial TEXT DEFAULT NULL,
    sexe TEXT DEFAULT NULL,
    methodeApprentissage TEXT DEFAULT NULL,
    id_user INTEGER DEFAULT NULL,
    FOREIGN KEY (id_user) REFERENCES user(id)
);

/*==============================================================*/
/* Table : QUIZ                                                 */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS quiz (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    datetime DATETIME NOT NULL,
    duree INTEGER,
    score INTEGER,
    id_user INTEGER,
    FOREIGN KEY (id_user) REFERENCES user(id)
);

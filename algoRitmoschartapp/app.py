from flask import Flask, request, redirect, url_for, render_template
import os
import psycopg2
import pandas as pd

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'csv')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    artist = 'Eli Soares'

    tot_deezer, tot_spotify = get_total_artista_rec(artist)

    con = conecta_db()
    cur = con.cursor()

    sql_cmd_s = "(select COUNT(ARTISTA_REC) as total, ARTISTA_REC, PLATAFORMA from tb_execucoes WHERE ARTISTA_SEED = '{}' AND PLATAFORMA = 'SPOTIFY' GROUP BY ARTISTA_REC, PLATAFORMA ORDER BY total DESC LIMIT 10)".format(artist)
    sql_cmd_d = "(select COUNT(ARTISTA_REC) as total, ARTISTA_REC, PLATAFORMA from tb_execucoes WHERE ARTISTA_SEED = '{}' AND PLATAFORMA = 'DEEZER' GROUP BY ARTISTA_REC, PLATAFORMA ORDER BY total DESC LIMIT 10)".format(artist)
    sql_cmd = "{} UNION {} ORDER BY total DESC;".format(sql_cmd_s, sql_cmd_d)

    cur.execute(sql_cmd)
    rows = cur.fetchall()

    df = pd.DataFrame(rows, columns=['QTD', 'ARTISTA_REC', 'PLATAFORMA'])
    filtro_s = (df['PLATAFORMA'] == 'SPOTIFY')
    filtro_d = (df['PLATAFORMA'] == 'DEEZER')

    df_s = df[filtro_s]
    df_s['QTD'] = df_s['QTD'] / tot_spotify
    df_s.to_csv('{}/barplot_spotify_top10.csv'.format(app.config['UPLOAD_FOLDER']), index=False)

    df_d = df[filtro_d]
    df_d['QTD'] = df_d['QTD'] / tot_deezer
    df_d.to_csv('{}/barplot_deezer_top10.csv'.format(app.config['UPLOAD_FOLDER']), index=False)

    return render_template('index.html', s_artist = "elisoares")

@app.route('/<artist>/<s_artist>')
def change_artist(artist, s_artist):
    tot_deezer, tot_spotify = get_total_artista_rec(artist)

    con = conecta_db()
    cur = con.cursor()

    sql_cmd_s = "(select COUNT(ARTISTA_REC) as total, ARTISTA_REC, PLATAFORMA from tb_execucoes WHERE ARTISTA_SEED = '{}' AND PLATAFORMA = 'SPOTIFY' GROUP BY ARTISTA_REC, PLATAFORMA ORDER BY total DESC LIMIT 10)".format(artist)
    sql_cmd_d = "(select COUNT(ARTISTA_REC) as total, ARTISTA_REC, PLATAFORMA from tb_execucoes WHERE ARTISTA_SEED = '{}' AND PLATAFORMA = 'DEEZER' GROUP BY ARTISTA_REC, PLATAFORMA ORDER BY total DESC LIMIT 10)".format(artist)
    sql_cmd = "{} UNION {} ORDER BY total DESC;".format(sql_cmd_s, sql_cmd_d)

    cur.execute(sql_cmd)
    rows = cur.fetchall()

    df = pd.DataFrame(rows, columns=['QTD', 'ARTISTA_REC', 'PLATAFORMA'])
    filtro_s = (df['PLATAFORMA'] == 'SPOTIFY')
    filtro_d = (df['PLATAFORMA'] == 'DEEZER')

    df_s = df[filtro_s]
    df_s['QTD'] = df_s['QTD'] / tot_spotify
    df_s.to_csv('{}/barplot_spotify_top10.csv'.format(app.config['UPLOAD_FOLDER']), index=False)

    df_d = df[filtro_d]
    df_d['QTD'] = df_d['QTD'] / tot_deezer
    df_d.to_csv('{}/barplot_deezer_top10.csv'.format(app.config['UPLOAD_FOLDER']), index=False)

    return render_template('index.html', s_artist = s_artist)

@app.route('/handle_form/', methods=['POST'])
def handle_form():
    s_artist = request.form['s_artists']

    if s_artist == "elisoares":
        return change_artist("Eli Soares", s_artist)
    elif s_artist == "alinebarros":
        return change_artist("Aline Barros", s_artist)
    elif s_artist == "calcanhotto":
        return change_artist("Adriana Calcanhotto", s_artist)
    elif s_artist == "gilbertogil":
        return change_artist("Gilberto Gil", s_artist)
    elif s_artist == "drikbarbosa":
        return change_artist("Drik Barbosa", s_artist)
    elif s_artist == "ricodalasam":
        return change_artist("Rico Dalasam", s_artist)
    elif s_artist == "mcdricka":
        return change_artist("MC Dricka", s_artist)
    elif s_artist == "mcpozedorodo":
        return change_artist("MC Poze do Rodo", s_artist)
    elif s_artist == "baroesdapisadinha":
        return change_artist("Os Barões da Pisadinha", s_artist)
    elif s_artist == "mariliamendonca":
        return change_artist("Marília Mendonça", s_artist)
    elif s_artist == "henriquejuliano":
        return change_artist("Henrique & Juliano", s_artist)
    elif s_artist == "jorgemateus":
        return change_artist("Jorge & Mateus", s_artist)
    elif s_artist == "gusttavolima":
        return change_artist("Gusttavo Lima", s_artist)
    else:
        return redirect(url_for('home'))

def conecta_db():
  con = psycopg2.connect(host='HOST',
                         database='DATABASE',
                         user='USER',
                         password='PASSWORD')
  return con


def get_total_artista_rec(artist):
    tot_deezer = 0
    tot_spotify = 0

    con = conecta_db()
    cur = con.cursor()

    sql_cmd = "select COUNT(ARTISTA_REC) as total, PLATAFORMA from tb_execucoes WHERE ARTISTA_SEED = '{}' GROUP BY PLATAFORMA".format(
        artist)

    cur.execute(sql_cmd)
    rows = cur.fetchall()

    for row in rows:
        if row[1] == 'DEEZER':
            tot_deezer = row[0]
        elif row[1] == 'SPOTIFY':
            tot_spotify = row[0]

    return tot_deezer, tot_spotify

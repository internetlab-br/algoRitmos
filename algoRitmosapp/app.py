#!/usr/bin/python3.10
from flask import Flask, request, render_template
import os
import spotipy
import requests
import psycopg2
import distance
from datetime import datetime
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)

@app.route('/')
def home():
    return elisoares_spotify()

@app.route('/elisoares_spotify')
def elisoares_spotify():
    artista = 'Eli Soares'
    plataforma = 'Spotify'

    CLIENT_ID = "CLIENT_ID"
    CLIENT_SECRET = "CLIENT_SECRET"

    os.environ['SPOTIPY_CLIENT_ID'] = CLIENT_ID
    os.environ['SPOTIPY_CLIENT_SECRET'] = CLIENT_SECRET

    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    lista_artistas = []
    lista_artistas_pic = []
    lista_musicas = []
    lista_top10 = []
    lista_links = []
    lista_links_label = []
    lista_sims = []
    lista_link_artista = []
    lista_link_track = []

    url_artist = "https://open.spotify.com/artist/"
    url_track = "https://open.spotify.com/track/"

    for i in range(0, 1):
        artist_id = "5zblJYkCzvB51Jh29FB07V"
        results = sp.recommendations(seed_artists=[artist_id], limit=10)

        id_sequencia = 1
        for track in results['tracks']:
            artist_track_id = track['artists'][0]['id']
            artist_data = sp.artist(artist_track_id)

            lista_link_track.append(url_track + str(track['id']))
            lista_link_artista.append(url_artist + str(artist_track_id))
            lista_artistas.append(track['artists'][0]['name'])
            lista_artistas_pic.append(artist_data['images'][2]['url'])
            lista_musicas.append(track['name'])
            id_sequencia = id_sequencia + 1

    data_hora = datetime.now()

    for i in range(0, len(lista_artistas)):
        con = conecta_db()
        cur = con.cursor()

        artista_rec = lista_artistas[i].replace(",", " ")
        artista_rec = artista_rec.replace("'", " ")

        musica_rec = lista_musicas[i].replace(",", " ")
        musica_rec = musica_rec.replace("'", " ")

        try:
            sql_cmd = "INSERT INTO tb_execucoes (DATA_HORA,ARTISTA_SEED,ARTISTA_REC,MUSICA_REC,PLATAFORMA) VALUES('{}', '{}', '{}', '{}', '{}')".format(data_hora, artista, artista_rec, musica_rec, plataforma)
            cur.execute(sql_cmd)
            con.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            con.rollback()
            cur.close()
            return 1
        cur.close()

    con = conecta_db()
    cur = con.cursor()
    sql_cmd = "select COUNT(ARTISTA_REC) as total, ARTISTA_REC from tb_execucoes WHERE ARTISTA_SEED = '{}' GROUP BY ARTISTA_REC ORDER BY total DESC LIMIT 10".format(artista)
    cur.execute(sql_cmd)
    rows = cur.fetchall()
    result_top10 = []

    for row in rows:
        result_top10.append(row[1])
    con.close()

    for art in lista_artistas:
        if art in result_top10:
            lista_top10.append("SIM ({})".format(result_top10.index(art) + 1))
        else:
            lista_top10.append("NÃO")

        url = 'https://pt.wikipedia.org/w/api.php'
        params = {
                    'action':'query',
                    'format':'json',
                    'list':'search',
                    'utf8':1,
                    'srsearch':art
                }

        data = requests.get(url, params=params).json()

        bigger_sim = 0
        link_result = ""
        link_label = ""
        sim_result = 0

        for item in data['query']['search']:
            sim = 1 - distance.nlevenshtein(art, item['title'])

            if sim > bigger_sim:
                bigger_sim = sim
                link_result = 'https://pt.wikipedia.org/wiki/{}'.format(item['title'].replace(" ","_"))
                link_label = item['title'].replace(" ","_")
                sim_result = round(sim,2)


        if sim_result > 0.9:
            lista_links.append(link_result)
            lista_links_label.append(link_label)
            lista_sims.append(round(sim_result * 100, 2))
        else:
            url_wiki_new = "https://pt.wikipedia.org/w/index.php?title={}&action=edit&redlink=1".format(art.replace(" ","_"))
            lista_links.append(url_wiki_new)
            lista_links_label.append("Criar Página para " + art.replace(" ","_"))
            lista_sims.append("-")

    return render_template('index.html', lista_artistas = lista_artistas, lista_artistas_pic = lista_artistas_pic, lista_musicas = lista_musicas, lista_link_track = lista_link_track, lista_links_label = lista_links_label, lista_link_artista = lista_link_artista, lista_top10 = lista_top10, lista_links = lista_links, lista_sims = lista_sims, artista = artista, s_artist = "elisoares", s_platform = "spotify")


@app.route('/artista_spotify/<artista>/<s_artist>/<artista_id>')
def artista_spotify(artista, s_artist, artista_id):
    plataforma = 'SPOTIFY'

    CLIENT_ID = "CLIENT_ID"
    CLIENT_SECRET = "CLIENT_SECRET"

    os.environ['SPOTIPY_CLIENT_ID'] = CLIENT_ID
    os.environ['SPOTIPY_CLIENT_SECRET'] = CLIENT_SECRET

    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    lista_artistas = []
    lista_artistas_pic = []
    lista_musicas = []
    lista_top10 = []
    lista_links = []
    lista_links_label = []
    lista_sims = []
    lista_link_artista = []
    lista_link_track = []

    url_artist = "https://open.spotify.com/artist/"
    url_track = "https://open.spotify.com/track/"

    results = sp.recommendations(seed_artists=[artista_id], limit=10)

    id_sequencia = 1
    for track in results['tracks']:
        artist_track_id = track['artists'][0]['id']
        artist_data = sp.artist(artist_track_id)

        lista_link_track.append(url_track + str(track['id']))
        lista_link_artista.append(url_artist + str(artist_track_id))
        lista_artistas.append(track['artists'][0]['name'])
        lista_artistas_pic.append(artist_data['images'][0]['url'])
        lista_musicas.append(track['name'])
        id_sequencia = id_sequencia + 1

    data_hora = datetime.now()

    for i in range(0, len(lista_artistas)):
        con = conecta_db()
        cur = con.cursor()
        artista_rec = lista_artistas[i].replace(",", " ")
        artista_rec = artista_rec.replace("'", " ")

        musica_rec = lista_musicas[i].replace(",", " ")
        musica_rec = musica_rec.replace("'", " ")

        try:
            sql_cmd = "INSERT INTO tb_execucoes (DATA_HORA,ARTISTA_SEED,ARTISTA_REC,MUSICA_REC,PLATAFORMA) VALUES('{}', '{}', '{}', '{}', '{}')".format(data_hora, artista, artista_rec, musica_rec, plataforma)
            cur.execute(sql_cmd)
            con.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            con.rollback()
            cur.close()
            return 1
        cur.close()

    con = conecta_db()
    cur = con.cursor()
    sql_cmd = "select COUNT(ARTISTA_REC) as total, ARTISTA_REC from tb_execucoes WHERE ARTISTA_SEED = '{}' AND PLATAFORMA = '{}' GROUP BY ARTISTA_REC ORDER BY total DESC LIMIT 10".format(artista, plataforma)
    cur.execute(sql_cmd)
    rows = cur.fetchall()
    result_top10 = []

    for row in rows:
        result_top10.append(row[1])
    con.close()

    for art in lista_artistas:
        if art in result_top10:
            lista_top10.append("SIM ({})".format(result_top10.index(art) + 1))
        else:
            lista_top10.append("NÃO")

        url = 'https://pt.wikipedia.org/w/api.php'
        params = {
                    'action':'query',
                    'format':'json',
                    'list':'search',
                    'utf8':1,
                    'srsearch':art
                }

        data = requests.get(url, params=params).json()

        bigger_sim = 0
        link_result = ""
        link_label = ""
        sim_result = 0

        for item in data['query']['search']:
            sim = 1 - distance.nlevenshtein(art, item['title'])

            if sim > bigger_sim:
                bigger_sim = sim
                link_result = 'https://pt.wikipedia.org/wiki/{}'.format(item['title'].replace(" ","_"))
                link_label = item['title'].replace(" ","_")
                sim_result = round(sim,2)


        if sim_result > 0.9:
            lista_links.append(link_result)
            lista_links_label.append(link_label)
            lista_sims.append(round(sim_result * 100, 2))
        else:
            url_wiki_new = "https://pt.wikipedia.org/w/index.php?title={}&action=edit&redlink=1".format(art.replace(" ","_"))
            lista_links.append(url_wiki_new)
            lista_links_label.append("Criar Página para " + art.replace(" ","_"))
            lista_sims.append("-")

    return render_template('index.html', lista_artistas = lista_artistas, lista_artistas_pic = lista_artistas_pic, lista_musicas = lista_musicas, lista_link_track = lista_link_track, lista_links_label = lista_links_label, lista_link_artista = lista_link_artista, lista_top10 = lista_top10, lista_links = lista_links, lista_sims = lista_sims, artista = artista, s_artist = s_artist, s_platform = "spotify")


@app.route('/artista_deezer/<artista>/<s_artist>/<artista_id>')
def artista_deezer(artista, s_artist, artista_id):
    plataforma = "DEEZER"

    r = requests.get('https://api.deezer.com/artist/{}/radio'.format(artista_id))

    lista_artistas = []
    lista_artistas_pic = []
    lista_musicas = []
    lista_top10 = []
    lista_links = []
    lista_links_label = []
    lista_sims = []
    lista_link_artista = []
    lista_link_track = []

    url_artist = "https://www.deezer.com/br/artist/"
    url_track = "https://www.deezer.com/br/track/"

    if r.status_code == 200:
        dados_json = r.json()

        for c, track in enumerate(dados_json['data']):
            if c < 10:
                lista_link_track.append(url_track + str(track['id']))
                lista_link_artista.append(url_artist + str(track['artist']['id']))
                lista_artistas_pic.append(track['artist']['picture_small'])
                lista_artistas.append(track['artist']['name'])
                lista_musicas.append(track['title'])

    data_hora = datetime.now()

    for i in range(0, len(lista_artistas)):
        con = conecta_db()
        cur = con.cursor()
        try:
            sql_cmd = "INSERT INTO tb_execucoes (DATA_HORA,ARTISTA_SEED,ARTISTA_REC,MUSICA_REC,PLATAFORMA) VALUES('{}', '{}', '{}', '{}', '{}')".format(data_hora, artista, lista_artistas[i].replace(",", " "), lista_musicas[i], plataforma)
            cur.execute(sql_cmd)
            con.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            con.rollback()
            cur.close()
            return 1
        cur.close()

    con = conecta_db()
    cur = con.cursor()
    sql_cmd = "select COUNT(ARTISTA_REC) as total, ARTISTA_REC from tb_execucoes WHERE ARTISTA_SEED = '{}' AND PLATAFORMA = '{}' GROUP BY ARTISTA_REC ORDER BY total DESC LIMIT 10".format(artista, plataforma)
    cur.execute(sql_cmd)
    rows = cur.fetchall()
    result_top10 = []

    for row in rows:
        result_top10.append(row[1])
    con.close()

    for art in lista_artistas:
        if art in result_top10:
            lista_top10.append("SIM ({})".format(result_top10.index(art) + 1))
        else:
            lista_top10.append("NÃO")

        url = 'https://pt.wikipedia.org/w/api.php'
        params = {
                    'action':'query',
                    'format':'json',
                    'list':'search',
                    'utf8':1,
                    'srsearch':art
                }

        data = requests.get(url, params=params).json()

        bigger_sim = 0
        link_result = ""
        link_label = ""
        sim_result = 0

        for item in data['query']['search']:
            sim = 1 - distance.nlevenshtein(art, item['title'])

            if sim > bigger_sim:
                bigger_sim = sim
                link_result = 'https://pt.wikipedia.org/wiki/{}'.format(item['title'].replace(" ","_"))
                link_label = item['title'].replace(" ","_")
                sim_result = round(sim,2)

        if sim_result > 0.9:
            lista_links.append(link_result)
            lista_links_label.append(link_label)
            lista_sims.append(round(sim_result * 100, 2))
        else:
            url_wiki_new = "https://pt.wikipedia.org/w/index.php?title={}&action=edit&redlink=1".format(art.replace(" ","_"))
            lista_links.append(url_wiki_new)
            lista_links_label.append("Criar Página para " + art.replace(" ","_"))
            lista_sims.append("-")

    return render_template('index.html', lista_artistas = lista_artistas, lista_artistas_pic = lista_artistas_pic, lista_link_track = lista_link_track, lista_link_artista = lista_link_artista, lista_musicas = lista_musicas, lista_top10 = lista_top10, lista_links = lista_links, lista_links_label = lista_links_label, lista_sims = lista_sims, artista = artista, s_artist = s_artist, s_platform = "deezer")


#*****************************
#******MAIN CALL FUNCTION*****
#*****************************

@app.route('/handle_form/', methods=['POST'])
def handle_form():
    s_artist = request.form['s_artists']
    s_platform = request.form['s_platforms']

    if s_artist == "elisoares" and s_platform == "spotify":
        return artista_spotify("Eli Soares", s_artist, "5zblJYkCzvB51Jh29FB07V")
    elif s_artist == "elisoares" and s_platform == "deezer":
        return artista_deezer("Eli Soares", s_artist, "5503854")
    elif s_artist == "alinebarros" and s_platform == "spotify":
        return artista_spotify("Aline Barros", s_artist, "5VBwbhqmLEaiF6fcRC682W")
    elif s_artist == "alinebarros" and s_platform == "deezer":
        return artista_deezer("Aline Barros", s_artist, "14000")
    elif s_artist == "calcanhotto" and s_platform == "spotify":
        return artista_spotify("Adriana Calcanhotto", s_artist, "72f733zGuCPEzCSLs9wOVi")
    elif s_artist == "calcanhotto" and s_platform == "deezer":
        return artista_deezer("Adriana Calcanhotto", s_artist, "4333")
    elif s_artist == "gilbertogil" and s_platform == "spotify":
        return artista_spotify("Gilberto Gil", s_artist, "7oEkUINVIj1Nr3Wnj8tzqr")
    elif s_artist == "gilbertogil" and s_platform == "deezer":
        return artista_deezer("Gilberto Gil", s_artist, "2077")
    elif s_artist == "drikbarbosa" and s_platform == "spotify":
        return artista_spotify("Drik Barbosa", s_artist, "1VJZvjGu80pBwk0qeJz8ZR")
    elif s_artist == "drikbarbosa" and s_platform == "deezer":
        return artista_deezer("Drik Barbosa", s_artist, "5819296")
    elif s_artist == "ricodalasam" and s_platform == "spotify":
        return artista_spotify("Rico Dalasam", s_artist, "5nbaj9RaJdFNlS5ZxoqN97")
    elif s_artist == "ricodalasam" and s_platform == "deezer":
        return artista_deezer("Rico Dalasam", s_artist, "6858071")
    elif s_artist == "mcdricka" and s_platform == "spotify":
        return artista_spotify("MC Dricka", s_artist, "4d175LvxCzxt5vHbJyv49q")
    elif s_artist == "mcdricka" and s_platform == "deezer":
        return artista_deezer("MC Dricka", s_artist, "12610223")
    elif s_artist == "mcpozedorodo" and s_platform == "spotify":
        return artista_spotify("MC Poze do Rodo", s_artist, "28ie4NNTa2VW2QV4Zray8M")
    elif s_artist == "mcpozedorodo" and s_platform == "deezer":
        return artista_deezer("MC Poze do Rodo", s_artist, "63912472")
    elif s_artist == "baroesdapisadinha" and s_platform == "spotify":
        return artista_spotify("Os Barões da Pisadinha", s_artist, "5Lv2GUVwqmQBPwrTrxucE5")
    elif s_artist == "baroesdapisadinha" and s_platform == "deezer":
        return artista_deezer("Os Barões da Pisadinha", s_artist, "61474832")
    elif s_artist == "mariliamendonca" and s_platform == "spotify":
        return artista_spotify("Marília Mendonça", s_artist, "1yR65psqiazQpeM79CcGh8")
    elif s_artist == "mariliamendonca" and s_platform == "deezer":
        return artista_deezer("Marília Mendonça", s_artist, "7068771")
    elif s_artist == "henriquejuliano" and s_platform == "spotify":
        return artista_spotify("Henrique & Juliano", s_artist, "3p7PcrEHaaKLJnPUGOtRlT")
    elif s_artist == "henriquejuliano" and s_platform == "deezer":
        return artista_deezer("Henrique & Juliano", s_artist, "4876653")
    elif s_artist == "jorgemateus" and s_platform == "spotify":
        return artista_spotify("Jorge & Mateus", s_artist, "1elUiq4X7pxej6FRlrEzjM")
    elif s_artist == "jorgemateus" and s_platform == "deezer":
        return artista_deezer("Jorge & Mateus", s_artist, "3881631")
    elif s_artist == "gusttavolima" and s_platform == "spotify":
        return artista_spotify("Gusttavo Lima", s_artist, "7MiDcPa6UiV3In7lIM71IN")
    elif s_artist == "gusttavolima" and s_platform == "deezer":
        return artista_deezer("Gusttavo Lima", s_artist, "1541592")
    else:
        return s_artist + " e " + s_platform

def conecta_db():
  con = psycopg2.connect(host='HOST',
                         database='DATABASE',
                         user='USER',
                         password='PASSWORD')
  return con

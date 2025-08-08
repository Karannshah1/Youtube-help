from flask import Flask, request, jsonify, render_template, redirect, url_for
import yt_dlp

app = Flask(__name__,template_folder="../templates")

YTDL_OPTS = {
    'quiet': True,
    'skip_download': True,
}

@app.route('/', methods=['GET'])
def home():
    return render_template('search.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('search.html', error="Please enter a search query")

    max_results = 10
    ytdl_query = f"ytsearch{max_results}:{query}"

    with yt_dlp.YoutubeDL(YTDL_OPTS) as ytdl:
        info = ytdl.extract_info(ytdl_query, download=False)

    entries = info.get('entries', [])
    results = []
    for e in entries:
        if not e:
            continue

        if e.get('_type') == 'playlist' or e.get('extractor') == 'youtube:playlist':
            embed_link = f"https://www.youtube-nocookie.com/embed/videoseries?list={e['id']}"
            entry_type = 'playlist'
            id_ = e['id']
        else:
            embed_link = f"https://www.youtube-nocookie.com/embed/{e['id']}"
            entry_type = 'video'
            id_ = e['id']

        results.append({
            'title': e.get('title'),
            'channel': e.get('uploader') or e.get('channel'),
            'thumbnail': e.get('thumbnail'),
            'duration': e.get('duration_string') if 'duration_string' in e else None,
            'type': entry_type,
            'embed_link': embed_link,
            'id': id_,
        })

    return render_template('results.html', query=query, results=results)

@app.route('/watch/<entry_type>/<id_>')
def watch(entry_type, id_):
    # Construct embed link
    if entry_type == 'playlist':
        embed_link = f"https://www.youtube-nocookie.com/embed/videoseries?list={id_}"
    else:
        embed_link = f"https://www.youtube-nocookie.com/embed/{id_}"

    return render_template('watch.html', embed_link=embed_link)


if __name__ == '__main__':
    app.run(debug=True)

from flask import (Flask, request, redirect, Response, url_for, jsonify, render_template)

from search import VideoSearch


searcher = VideoSearch()

app = Flask(__name__)


def second2str(sec):
    hours = sec / 60
    seconds = sec % 60
    return "{}:{:0>2d}".format(hours, seconds)


@app.route('/')
def home():
    q = request.args.get('q', None)
    p = 0
    # noinspection PyBroadException
    try:
        p = int(request.args.get('p', 0))
    except:
        pass
    if q:
        import time
        time_start = time.time()
        searcher.searchByQuery(q)
        number = searcher.num_search_result

        max_page = number // 15
        if p > max_page:
            p = max_page
        if p < 0:
            p = 0
        px = p-3
        if px < 0:
            px = 0
        py = px + 7
        if py > max_page:
            py = max_page

        time_cost = time.time() - time_start
        rank_list = searcher.getResultByInterval(p*15, (p+1)*15)

        return render_template('rank.html', time=time_cost, number=number, ranklist=rank_list, p=p, px=px, py=py,
                               second2str=second2str)
    else:
        return render_template('home.html')


if __name__ == '__main__':
    app.run()

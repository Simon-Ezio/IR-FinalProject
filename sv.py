from flask import (Flask, request, redirect, Response, url_for, jsonify, render_template)

app = Flask(__name__)


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
        time = 0.37
        number = 5170000
        rank_list = (
            dict(
                title='title one: blablabla',
                url='#',
                url_display='https://www.a/fake/url/.../is/here',
                desc=(((85, '01:25'), 'this is desc, this should be long'),) * 4
            ),
            dict(
                title='title two: a fake title',
                url='#',
                url_display='https://www.a/fake/url/.../is/here',
                desc=(((85, '01:25'), 'this is also desc, but short'),) * 2
            ),
        )
        rank_list = rank_list * 8
        max_page = number // 15
        if p >= max_page:
            p = max_page - 1
        if p < 0:
            p = 0
        px = p-3
        if px < 0:
            px = 0
        py = px + 7
        if py > max_page:
            py = max_page-1

        return render_template('rank.html', time=time, number=number, ranklist=rank_list, p=p, px=px, py=py)
    else:
        return render_template('home.html')


if __name__ == '__main__':
    app.run()

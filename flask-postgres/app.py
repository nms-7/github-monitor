from flask import Flask, render_template, request, redirect, url_for, jsonify
from secrets import POSTGRES
from pr_model import PRModel, PRSchema, rdb, ma
import requests
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
rdb.init_app(app)
ma.init_app(app)

pr_schema = PRSchema()
prs_schema = PRSchema(many=True)

@app.route('/')
def main():
    return 'Hello World!'

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/process', methods = ['POST'])
def process():
    username = request.form['username']
    repo = request.form['repo']
    pull_requests = requests.get("http://0.0.0.0:5000" + url_for('repo_pull_requests',user=username,repo=repo)).json()['pullrequests']
    num_pr = len(pull_requests)
    if num_pr == 0:
        return jsonify({'error': 'username / repo non-existent or contains no pull requests'})
    else:
        ### PR Metrics

        #avg time to close
        #ttc = sum([(pr['closed_at'] - pr['created_at']) for pr in pull_requests])/len(pull_requests)

        merge_rate = sum([pr['merged'] for pr in pull_requests])/num_pr

        metrics = requests.get("http://0.0.0.0:5000" + url_for('repo_metrics',user=username,repo=repo)).json()
        metrics['num_pr'] = num_pr
        metrics['merge_rate'] = merge_rate

        mean_open_time = requests.get("http://0.0.0.0:5000" + url_for('repo_pr_time',user=username,repo=repo)).json()
        print(mean_open_time)
        metrics.update(mean_open_time)


        return jsonify(metrics)

"""

API Calls

"""
@app.route('/pullrequest/examples')
def example_pull_requests():
    prs = PRModel.all_prs()
    return {"pullrequests": prs_schema.dump(prs[:3])}

"""Pull Request by PR ID"""
@app.route('/pullrequest/id/<id>')
def single_pull_request(id):
    prs = PRModel.get_pr_by_id(id)
    return {"pullrequests": prs_schema.dump(prs)}
# test id: 645165

"""Pull Requests by Repo"""
@app.route('/pullrequest/repo/<user>/<repo>')
def repo_pull_requests(user, repo):
    prs = PRModel.get_pr_by_repo("/".join((user,repo)))
    return json.dumps({"pullrequests": prs_schema.dump(prs)})

"""PR Metrics by Repo"""
@app.route('/metrics/repo/<user>/<repo>')
def repo_metrics(user, repo):
    metrics = PRModel.get_repo_metrics("/".join((user,repo)))
    return json.dumps(pr_schema.dump(metrics))

"""PR Open Time by Repo"""
@app.route('/pr_time/repo/<user>/<repo>')
def repo_pr_time(user, repo):
    pr_time = PRModel.get_repo_pr_time("/".join((user,repo)))[0]
    #print(pr_time)
    return {
        'days' : pr_time.days,
        'hours': pr_time.seconds // 3600,
        'minutes': (pr_time.seconds % 3600) / 60,
      }

if __name__ == "__main__":
    app.config['DEBUG'] = True
    app.run(host="0.0.0.0", port=5000)

import logging
import re

from flask import Flask
from flask import render_template, redirect, url_for
from flask import request
from flask import Markup

import markdown

from models import Post, Entity

app = Flask(__name__.split('.')[0])

def noTag(text, tag):
    pattern = r"(<\s*%s\s*.*?>)|(<\s*/%s\s*>)" % (tag, tag)
    pat = re.compile(pattern, re.IGNORECASE | re.DOTALL)
    tagless = pat.sub('', text)
    return tagless
  
def md2html(content):
    md = markdown.Markdown(extensions=['toc', 'def_list'])
    html_content = Markup(md.convert(content))
    toc = Markup(md.toc)
    return html_content, toc

def post(title=None, category=None):
    if title:
        post = Post.query(Post.title==title).get()
    else:
        post = Post.get_1lastest(category=category)

    pre_post = post.get_pre(category=category)
    next_post = post.get_next(category=category)
    content, toc = md2html(post.content)
    
    txt = noTag(noTag(toc, 'div'), 'ul')
    toc = toc if txt.strip() else ''
    return render_template('post.html',
                           post=post,
                           category=category,
                           pre_post=pre_post,
                           next_post=next_post,
                           toc=toc,
                           content=content)

@app.route('/')
@app.route('/page/')
@app.route('/page/<title>')
def index(title=None):
    return post(title)

@app.route('/<noun>/')
def entity(noun=None):
    entity = Entity.query(Entity.name==noun).get()
    post = Post.query(Post.title==noun).get()
    if not post:
        return redirect(url_for("idonotknow", noun=noun))
    
    posts = Post.query().filter(Post.category.IN([noun]))
    content, toc = md2html(post.content)
    
    txt = noTag(noTag(toc, 'div'), 'ul')
    toc = toc if txt.strip() else ''

    return render_template('entity.html',
                           entity=entity,
                           post=post,
                           posts=posts,
                           toc=toc,
                           content=content)

@app.route('/<noun>/<verb>')
def verb(noun=None, verb=None):
    return post(verb, category=noun)

@app.route('/idonotknow/<noun>')
def idonotknow(noun):
    posts = Post.query().filter(Post.category.IN([noun])).order(-Post.date)
    tagged_posts = Post.get_tagged_post(noun)
    return render_template('idonotknow.html',
                           noun=noun,
                           posts=posts,
                           tagged_posts=tagged_posts)

@app.route('/archives')
def archives():
    entities = Entity.query().order(Entity.name)
    return render_template('archives.html',
                           entities=entities)

@app.route('/history')
def hisotry():
    posts = Post.query().order(-Post.date)
    return render_template('archives-history.html',
                           posts=posts)

@app.route('/network')
def network():
    entities = Entity.query().order(Entity.name)
    result = list()
    for e in entities:
        result.extend(e.get_json())
    return render_template('network.html',
                           result=result)
    
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

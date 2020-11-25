from flask import g, request

from . import bp_admin_api
from ...api_utils import *
from ...models import Article


@bp_admin_api.route('/article/create/', methods=['POST'])
def create_article():
    """创建文章"""
    title, contents, cover_url, extra_add_count = map(g.json.get, ['title', 'contents', 'cover_url', 'extra_add_count'])
    claim_args(1203, title, contents, cover_url, extra_add_count)
    claim_args_int(1204, extra_add_count)
    claim_args_str(1204, title, contents, cover_url)
    Article.new(title, contents, cover_url, extra_add_count)
    return api_success_response({})


@bp_admin_api.route('/article/status/update/', methods=['POST'])
def update_article_status():
    """启用/停用文章"""
    article_id, show = map(g.json.get, ['article_id', 'show'])
    claim_args(1203, article_id, show)
    claim_args_int(1204, article_id, show)
    article = Article.get_by_id(article_id, code=1104)
    article.update_show(show)
    return api_success_response({})


@bp_admin_api.route('/article/delete/', methods=['POST'])
def delete_article():
    """删除文章"""
    article_id = g.json.get('article_id')
    claim_args_int(1204, article_id)
    article = Article.get_by_id(article_id, code=1104)
    article.update_delete(is_delete=1)
    return api_success_response({})


@bp_admin_api.route('/article/edit/', methods=['POST'])
def edit_article():
    """编辑文章"""
    article_id, title, contents, cover_url, extra_add_count = map(g.json.get, ['article_id', 'title', 'contents', 'cover_url', 'extra_add_count'])
    claim_args(1203, article_id, title, contents, cover_url, extra_add_count)
    claim_args_int(1204, article_id, extra_add_count)
    claim_args_str(1204, title, contents, cover_url)
    article = Article.get_by_id(article_id, code=1104)
    article.update_info(title, contents, cover_url, extra_add_count)
    return api_success_response({})


@bp_admin_api.route('/article/list/', methods=['GET'])
def get_article_list():
    """查询文章list"""
    query = Article.select().where(Article.is_delete == 0)
    data = {
        "articles": [article.to_dict() for article in query]
    }
    return api_success_response(data)


@bp_admin_api.route('/article/detail/<int:article_id>/', methods=['GET'])
def get_article_detail(article_id):
    """查询单个文章详情"""
    article = Article.get_by_id(int(article_id), code=1104)
    data = {
        "article": article.to_dict()
    }
    return api_success_response(data)


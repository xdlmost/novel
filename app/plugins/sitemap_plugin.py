from flask import Blueprint ,request,render_template , abort
import os
import json
from config.local import URL_BASE
plugin = Blueprint('sitemap', __name__)
DATA_PATH='app/static/data'

@plugin.route('/sitemap.xml', methods=['GET'])
def sitemap():
    header='<?xml version="1.0" encoding="UTF-8" ?> <urlset >'
    footer='</urlset>'
    ret=header
    
    # index 

    ret+='<url><loc>%s/</loc></url>'%(URL_BASE)
    ret+='<url><loc>%s/xuanhuan/</loc></url>'%(URL_BASE)
    ret+='<url><loc>%s/xianxia/</loc></url>'%(URL_BASE)
    ret+='<url><loc>%s/dushi/</loc></url>'%(URL_BASE)
    ret+='<url><loc>%s/yanqing/</loc></url>'%(URL_BASE)
    ret+='<url><loc>%s/lishi/</loc></url>'%(URL_BASE)
    ret+='<url><loc>%s/wangyou/</loc></url>'%(URL_BASE)
    ret+='<url><loc>%s/kehuan/</loc></url>'%(URL_BASE)
    ret+='<url><loc>%s/kongbu/</loc></url>'%(URL_BASE)

    
    # content 
    from app import db
    from app.dao.models import NovelInfo,NovelContent
    aa=db.session.query(NovelInfo.id).all()
    for ni in aa:
        ret+= '<url><loc>%s</loc></url>'%(URL_BASE+'/'+ni.id+'/')
    ret+=footer
    return ret,200, {'Content-Type': 'text/xml; charset=utf-8'}

@plugin.route('/sitemap<string:numberStr>.xml', methods=['GET'])
def sitemapn(numberStr):
    NUM=40000
    number=int(numberStr)
    from app import db
    from app.dao.models import NovelInfo,NovelContent
    aa=db.session.query(NovelContent.novelid,NovelContent.id).offset(number*NUM).limit(NUM).all()
    header='<?xml version="1.0" encoding="UTF-8" ?> <urlset>'
    footer='</urlset>'
    ret=header
    for ni in aa:
        ret+= '<url><loc>%s</loc></url>'%(URL_BASE+'/'+ni.novelid+'/'+ni.id)
    ret+=footer
    return ret,200, {'Content-Type': 'text/xml; charset=utf-8'}
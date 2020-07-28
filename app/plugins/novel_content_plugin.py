from flask import Blueprint ,request,render_template , abort
import os
import json
from config.local import URL_BASE,DATA_DIR

plugin = Blueprint('novel_content', __name__)
DATA_PATH=DATA_DIR


@plugin.route('/<string:novelid>/<string:charpterid>', methods=['GET'])
def novel_content(novelid,charpterid):
    from app import db
    from app.dao.models import NovelInfo,NovelContent
    session=db.session

    thisNovelContent=session.query(NovelContent).filter(NovelContent.id==charpterid,NovelContent.novelid==novelid).first()
    if thisNovelContent is None:
        abort(404)
        
    
    charpter_path=os.path.join(DATA_PATH,novelid,charpterid)
    if not os.path.isfile(charpter_path):
        abort(404)
    
    thisNovelInfo=session.query(NovelInfo).filter(NovelInfo.id==novelid).one()

    content=''
    with open (charpter_path,"r",encoding="utf-8") as f:
        content=f.readlines()
    
    pindex=thisNovelContent.index-1
    pNovelContent=session.query(NovelContent).filter(NovelContent.index==pindex,NovelContent.novelid==novelid).first()

    return render_template('novel_content.html',data={
        'content':content,
        'author':thisNovelInfo.author,
        'bookid':novelid,
        'bookname':thisNovelInfo.title,
        'charptername':thisNovelContent.title,
        'pid':thisNovelContent.pid ,
        'nid':thisNovelContent.nid },url_base=URL_BASE)
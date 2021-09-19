﻿# -*- coding: utf-8 -*-
try:
    import urllib2
    import urllib
    import HTMLParser as htmlparser
    py3 = False
except ImportError:
    py3 = True
    import html
    import html.parser as htmlparser
    import urllib.request as urllib2
    import urllib.parse as urllib
    basestring = str

import re
import socket
import datetime
import time
import sys
import os
import json
import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import xbmcvfs
import base64

try: from sqlite3 import dbapi2 as database
except: from pysqlite2 import dbapi2 as database
from resources.lib import requests

__settings__ = xbmcaddon.Addon('plugin.video.romanianpack')
__language__ = __settings__.getLocalizedString
__scriptname__ = __settings__.getAddonInfo('name')
ROOT = __settings__.getAddonInfo('path')
USERAGENT = "Mozilla/5.0 (Windows NT 6.1; rv:5.0) Gecko/20100101 Firefox/5.0"
__addonpath__ = __settings__.getAddonInfo('path')
icon = os.path.join(__addonpath__, 'icon.png')
__version__ = __settings__.getAddonInfo('version')
__plugin__ = __scriptname__ + " v." + __version__
if py3: dataPath = xbmcvfs.translatePath(__settings__.getAddonInfo("profile"))
else: dataPath = xbmc.translatePath(__settings__.getAddonInfo("profile")).decode("utf-8")
addonCache = os.path.join(dataPath,'cache.db')
try: 
    media = sys.modules["__main__"].__media__
except: media = os.path.join(ROOT, 'resources', 'media')
search_icon = os.path.join(media,'search.png')
fav_icon = os.path.join(media,'favorite.png')
torr_icon = os.path.join(media,'torrents.png')
torrclient_icon = os.path.join(media,'torrclient.png')
cat_icon = os.path.join(media,'categorii.png')
recents_icon = os.path.join(media,'recente.png')
seen_icon = os.path.join(media,'vazute.png')
next_icon = os.path.join(media,'next.png')


def md5(string):
    try:
        from hashlib import md5
    except ImportError:
        from md5 import md5
    hasher = hashlib.md5()
    try:
        hasher.update(string)
    except:
        hasher.update(string.encode('utf-8', 'ignore'))
    return hasher.hexdigest()


def log(msg):
    loginfo = xbmc.LOGINFO if py3 else xbmc.LOGNOTICE
    try:
        xbmc.log("### [%s]: %s" % (__plugin__,msg,), level=loginfo )
    except UnicodeEncodeError:
        xbmc.log("### [%s]: %s" % (__plugin__,msg.encode("utf-8", "ignore"),), level=loginfo )
    except:
        xbmc.log("### [%s]: %s" % (__plugin__,'ERROR LOG',), level=loginfo )

def join_list(l, char=', ', replace=''):
    string=''
    for i in l:
        string+=i.replace(replace,'')+char
    return string.rstrip(' ,')

def getSettingAsBool(setting):
    return __settings__.getSetting(setting).lower() == "true"

def showMessage(heading, message, times=5000, forced=True):
    if forced or not getSettingAsBool('disable_notifications'):
        xbmc.executebuiltin('Notification(%s, %s, %s, %s)' % (
            heading.replace('"', "'"), message.replace('"', "'"), times, icon))

def fetchData(url, referer=None, data={}, redirect=None, rtype=None, headers={}, cookies={}, timeout=None, api=None):
    from resources.lib.requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    timeout = timeout if timeout else int(__settings__.getSetting('timeout'))
    headers = headers
    if referer != None:
        headers['Referer'] = referer
    headers['User-Agent'] = USERAGENT
    if api: headers = {'User-Agent' : USERAGENT}
    try:
        if data: get = requests.post(url, headers=headers, data=data, verify=False, timeout=timeout)
        else: get = requests.get(url, headers=headers, verify=False, timeout=timeout, cookies=cookies)
        if redirect: result = get.url
        else: 
            if rtype: 
                if rtype == 'json': result = get.json()
                else:
                    if py3: result = get.text
                    else:
                        try: result = get.text.decode('utf-8')
                        except: result = get.text.decode('latin-1')
            else:
                try: result = get.content.decode('utf-8')
                except: result = get.content.decode('latin-1')
        return (result)
    except BaseException as e:
        log("fetchData(%s) exception: %s" % (url,e))
        return

def replaceHTMLCodes(txt):
    txt = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", txt)
    txt = txt.replace("&quot;", "\"")
    txt = txt.replace("&amp;", "&")
    try: txt = html.unescape(txt)
    except: txt = htmlparser.HTMLParser().unescape(txt)
    txt = txt.strip()
    return txt
        
def striphtml(data):
        p = re.compile('<.*?>', re.DOTALL)
        cleanp = re.sub(p, '', data)
        return cleanp

def unquote(string, ret=None):
    try:
        return urllib.unquote_plus(string)
    except:
        if ret:
            return ret
        else:
            return string
        
def unquot(string, ret=None):
    try:
        return urllib.unquote(string)
    except:
        if ret:
            return ret
        else:
            return string
        
def quote(string, ret=None):
    string = ensure_str(string)
    try:
        return urllib.quote_plus(string)
    except:
        if ret:
            return ret
        else:
            return string
        
def quot(string, ret=None):
    string = ensure_str(string)
    try:
        return urllib.quote(string)
    except:
        if ret:
            return ret
        else:
            return string

def unescape(string):
    htmlCodes = (
        ('&', '&amp;'),
        ('<', '&lt;'),
        ('>', '&gt;'),
        ('"', '&quot;'),
        ("'", '&#39;'),
    )
    for (symbol, code) in htmlCodes:
        string = re.sub(code, symbol, string)
    try: return string.encode('utf-8')
    except: return string

def create_tables():
    try:
        if xbmcvfs.exists(dataPath) == 0: xbmcvfs.mkdir(dataPath)
    except BaseException as e: log(u"localdb.create_tables makedir ##Error: %s" % str(e))
    try:
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS watched (id INTEGER PRIMARY KEY AUTOINCREMENT, ""title TEXT, ""label TEXT, ""overlay TEXT, ""date TEXT, ""UNIQUE(title)"");")
        dbcur.execute("CREATE TABLE IF NOT EXISTS resume (id INTEGER PRIMARY KEY AUTOINCREMENT, ""url TEXT, ""title TEXT, ""fileindex TEXT, ""elapsed TEXT, ""total TEXT, ""date TEXT, ""UNIQUE(url)"");")
        dbcur.execute("CREATE TABLE IF NOT EXISTS favorites (id INTEGER PRIMARY KEY AUTOINCREMENT, ""url TEXT, ""title TEXT, ""info TEXT, ""date TEXT, ""UNIQUE(url)"");")
        dbcur.execute("CREATE TABLE IF NOT EXISTS search (id INTEGER PRIMARY KEY AUTOINCREMENT, ""search TEXT, ""date TEXT"");")
        dbcur.execute("CREATE TABLE IF NOT EXISTS onetime (""fixdb TEXT"");")
        dbcon.commit()
    except BaseException as e: log(u"localdb.create_tables ##Error: %s" % str(e))

def fix_db():
    try:
        log('fix old db take 3')
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS watched_copy (id INTEGER PRIMARY KEY AUTOINCREMENT, ""title TEXT, ""label TEXT, ""overlay TEXT, ""date TEXT, ""UNIQUE(title)"");")
        dbcur.execute('INSERT INTO watched_copy(title, label, overlay) select title, label, overlay from watched')
        dbcur.execute('DROP TABLE watched')
        dbcur.execute('ALTER TABLE watched_copy rename to watched')
        dbcur.execute("CREATE TABLE IF NOT EXISTS favorites_copy (id INTEGER PRIMARY KEY AUTOINCREMENT, ""url TEXT, ""title TEXT, ""info TEXT, ""date TEXT, ""UNIQUE(url)"");")
        dbcur.execute('INSERT INTO favorites_copy(url, title, info) select url, title, info from favorites')
        dbcur.execute('DROP TABLE favorites')
        dbcur.execute('ALTER TABLE favorites_copy rename to favorites')
        dbcur.execute("CREATE TABLE IF NOT EXISTS search_copy (id INTEGER PRIMARY KEY AUTOINCREMENT, ""search TEXT, ""date TEXT"");")
        dbcur.execute('INSERT INTO search_copy(search) select search from search')
        dbcur.execute('DROP TABLE search')
        dbcur.execute('ALTER TABLE search_copy rename to search')
        dbcur.execute("INSERT INTO onetime(fixdb) VALUES ('3');")
        try: dbcur.execute("VACUUM")
        except: pass
        dbcon.commit()
    except BaseException as e: log(u"localdb.fix_db ##Error: %s" % str(e))
    
def check_one_db():
    try:
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT fixdb FROM onetime")
        found = dbcur.fetchall()
        fix = True
        for i in found:
            if i[0] == '3':
                fix = False
                break
        if fix: fix_db()
    except BaseException as e: log(u"localdb.check_one_db ##Error: %s" % str(e))
    
def get_watched(title):
    try:
        dbcon = database.connect(addonCache)
        dbcon.text_factory = str
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT overlay FROM watched WHERE title = ?", (title, ))
        found = dbcur.fetchone()
        return True if found else False
    except BaseException as e: log(u"localdb.get_watched ##Error: %s" % str(e))
    
def list_watched(page=1):
    try:
        found = []
        try:
            xrange
        except NameError:
            xrange = range
        dbcon = database.connect(addonCache)
        cursor = dbcon.cursor()
        cursor.execute("SELECT count(*) FROM watched")
        count = cursor.fetchone()[0]
        batch_size = 50
        offsetnumber = (page-1) * batch_size
        offset = xrange(offsetnumber, count, batch_size)
        offset = offset[0] if offset else 0
        cursor.execute("SELECT * FROM watched ORDER by id DESC LIMIT ? OFFSET ?", (batch_size, offset))
        for row in cursor:
            found.append((row))
        return found
    except BaseException as e: log(u"localdb.list_watched ##Error: %s" % str(e))

def list_partial_watched(page=1):
    try:
        found = []
        try:
            xrange
        except NameError:
            xrange = range
        dbcon = database.connect(addonCache)
        cursor = dbcon.cursor()
        cursor.execute("SELECT count(*) FROM resume")
        count = cursor.fetchone()[0]
        batch_size = 50
        offsetnumber = (page-1) * batch_size
        offset = xrange(offsetnumber, count, batch_size)[0]
        offset = offset[0] if offset else 0
        cursor.execute("SELECT id,title,url,elapsed,date,total FROM resume ORDER by id DESC LIMIT ? OFFSET ?",  (batch_size, offset))
        for row in cursor:
            found.append((row))
        return found
    except BaseException as e: log(u"localdb.list_partial_watched ##Error: %s" % str(e))


def save_watched(title, info, norefresh=None, elapsed=None, total=None):
    try:
        title = unquote(title)
        overlay = '7'
        date = get_time()
        dbcon = database.connect(addonCache)
        dbcon.text_factory = str
        dbcur = dbcon.cursor()
        dbcur.execute("DELETE FROM resume WHERE title = ?", (title, ))
        dbcur.execute("DELETE FROM watched WHERE title = ?", (title, ))
        if elapsed:
            dbcur.execute("INSERT INTO resume (title,url,elapsed,total,date) Values (?, ?, ?, ?, ?)", (title, str(info), elapsed, total, date))
        else:
            dbcur.execute("INSERT INTO watched (title,label,overlay,date) Values (?, ?, ?, ?)", (title, str(info), overlay, date))
        try: dbcur.execute("VACUUM")
        except: pass
        dbcon.commit()
        #if not norefresh:
            #xbmc.executebuiltin("Container.Refresh")
    except BaseException as e: log(u"localdb.save_watched ##Error: %s" % str(e))

def update_watched(title, label, overlay):
    try:
        dbcon = database.connect(addonCache)
        dbcon.text_factory = str
        dbcon.execute("UPDATE watched SET overlay = ? WHERE title = ?", (overlay, title))
        dbcon.commit()
    except BaseException as e: log(u"localdb.update_watched ##Error: %s" % str(e))

def delete_watched(url=None):
    try:
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        if url: dbcur.execute("DELETE FROM watched WHERE title = ?", (url, ))
        else: dbcur.execute("DELETE FROM watched")
        if url:
            try:
                dbcur.execute("DELETE FROM resume WHERE title = ?", (url, ))
            except: pass
        try: dbcur.execute("VACUUM")
        except: pass
        dbcon.commit()
        xbmc.executebuiltin("Container.Refresh")
    except BaseException as e: log(u"localdb.delete_watched ##Error: %s" % str(e))
    
def save_fav(title, url, info, norefresh=None):
    try:
        dbcon = database.connect(addonCache)
        dbcon.text_factory = lambda x: unicode(x, "utf-8", "ignore")
        dbcur = dbcon.cursor()
        dbcur.execute("DELETE FROM favorites WHERE url = ?", (url, ))
        dbcur.execute("INSERT INTO favorites (url,title,info) Values (?, ?, ?)", (url, title, str(info)))
        try: dbcur.execute("VACUUM")
        except: pass
        dbcon.commit()
        showMessage('MRSP','Salvat în Favorite')
        #if not norefresh:
            #xbmc.executebuiltin("Container.Refresh")
    except BaseException as e: log("localdb.save_fav ##Error: %s" % str(e))

def get_fav(url=None,page=1):
    try:
        dbcon = database.connect(addonCache)
        dbcon.text_factory = str
        dbcur = dbcon.cursor()
        if url:
            dbcur.execute("SELECT title FROM favorites WHERE url = ?", (url, ))
            found = dbcur.fetchall()
        else:
            try:
                xrange
            except NameError:
                xrange = range
            found = []
            dbcur.execute("SELECT count(*) FROM favorites")
            count = dbcur.fetchone()[0]
            batch_size = 50
            offsetnumber = (page-1) * batch_size
            offset = xrange(offsetnumber, count, batch_size)[0]
            dbcur.execute("SELECT * FROM favorites ORDER by id DESC LIMIT ? OFFSET ?", (batch_size, offset))
            for row in dbcur:
                found.append((row))
        return found
    except BaseException as e: 
        log(u"localdb.get_fav ##Error: %s" % str(e))

def del_fav(url, norefresh=None):
    try:
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        dbcur.execute("DELETE FROM favorites WHERE url = ?", (url, ))
        try: dbcur.execute("VACUUM")
        except: pass
        dbcon.commit()
        showMessage('MRSP', 'Șters din favorite')
        if not norefresh:
            xbmc.executebuiltin("Container.Refresh")
    except BaseException as e: log(u"localdb.del_fav ##Error: %s" % str(e))

def save_search(cautare):
    try:
        dbcon = database.connect(addonCache)
        dbcon.text_factory = str
        dbcur = dbcon.cursor()
        dbcur.execute("DELETE FROM search WHERE search = ?", (cautare, ))
        dbcur.execute("INSERT INTO search (search) Values (?)", (cautare,))
        try: dbcur.execute("VACUUM")
        except: pass
        dbcon.commit()
    except BaseException as e: log(u"localdb.save_search ##Error: %s" % str(e))

def del_search(text):
    try:
        dbcon = database.connect(addonCache)
        dbcon.text_factory = lambda x: unicode(x, "utf-8", "ignore")
        dbcur = dbcon.cursor()
        dbcur.execute("DELETE FROM search WHERE search = ?", (text, ))
        try: dbcur.execute("VACUUM")
        except: pass
        dbcon.commit()
        showMessage('MRSP', 'Șters din Căutări')
        xbmc.executebuiltin("Container.Refresh")
    except BaseException as e: log(u"localdb.del_search ##Error: %s" % str(e))
    
def clean_database():
    try:
        tableid = __settings__.getSetting('cleandatabasetable')
        if tableid == '0':
            table = 'favorites'
            tablename = 'Favorite'
        elif tableid == '1':
            table = 'watched'
            tablename == 'Văzute'
        elif tableid == '2':
            table = 'search'
            tablename = 'Căutare'
        limit = __settings__.getSetting('cleandatabaselimit')
        dialog = xbmcgui.Dialog()
        ret = dialog.yesno('MRSP', 'Vrei să cureți intrările din %s' % tablename, 'Și să păstrezi ultimele %s intrări?' % limit, yeslabel='Da', nolabel='Nu' )
        if ret == 1:
            dbcon = database.connect(addonCache)
            dbcon.text_factory = str
            dbcur = dbcon.cursor()
            dbcur.execute("DELETE FROM ? WHERE id NOT IN (SELECT id FROM ? ORDER BY id DESC LIMIT ?)", (table, table, int(limit)))
            try: dbcur.execute("VACUUM")
            except: pass
            dbcon.commit()
            showMessage('MRSP', 'Curățat %s și păstrat %s intrări' % (tablename,limit))
    except BaseException as e: 
        log(u"functions.clean_database ##Error: %s" % str(e))

def get_search():
    try:
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT search FROM search")
        found = dbcur.fetchall()
        return found
    except BaseException as e: log(u"localdb.get_search ##Error: %s" % str(e))

def tmdb_key():
    if py3:
        return base64.urlsafe_b64decode('ODFlNjY4ZTdhMzdhM2Y2NDVhMWUyMDYzNjg3ZWQ3ZmQ=').decode()
    else: return base64.urlsafe_b64decode('ODFlNjY4ZTdhMzdhM2Y2NDVhMWUyMDYzNjg3ZWQ3ZmQ=')

def get_time():
    return int(time.time())

def playTrailer(params):
        get = params.get
        nume = get('nume')
        link = get('link')
        liz = xbmcgui.ListItem(nume)
        liz.setArt({'thumb': get('poster')})
        liz.setInfo(type="Video", infoLabels={'Title':nume, 'Plot': get('plot')})
        import resolveurl as urlresolver
        try:
            hmf = urlresolver.HostedMediaFile(url=link, include_disabled=True, include_universal=False)
            xbmc.Player().play(hmf.resolve(), liz, False)
        except Exception as e: 
            showMessage("MRSP-Eroare", "%s" % e)

def playTrailerImdb(params):
    get = params.get
    nume = get('nume')
    link1 = get('link')
    link = ''
    sel = None
    if not isinstance(link1, basestring):
        dialog = xbmcgui.Dialog()
        if len(link1) > 1: sel = dialog.select("Selecteaza trailer", [str(i) for i in range(len(link1))])
        else: sel = 0
    if sel is not None:
        link1 = ('https://www.imdb.com%s' % link1[sel]) if not link1[sel].startswith('http') else link1[sel]
    match = re.findall('videoUrl":"(.+?)"', fetchData(link1))
    if match: link = match[-1]
    if not link:
        try:
            s = requests.Session()
            headers = {'Host': 'www.imdb.com',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:70.1) Gecko/20100101 Firefox/70.1',
                    'Referer': link1}
            html = s.get(link1, headers=headers).text
            datakey = re.search('playbackDataKey":\["([^"]+)', html).group(1)
            new = s.get('https://www.imdb.com/ve/data/VIDEO_PLAYBACK_DATA?key=%s' % datakey, headers=headers).json()
            link = new[0].get('videoLegacyEncodings')[0].get('url')
        except: link = ''
    try: link = link.decode('unicode_escape')
    except: pass
    liz = xbmcgui.ListItem(nume)
    liz.setArt({'thumb': get('poster')})
    liz.setInfo(type="Video", infoLabels={'Title':nume, 'Plot': get('plot')})
    try:
        xbmc.Player().play(link, liz, False)
    except Exception as e: 
        showMessage("MRSP-Eroare", "%s" % e)

def playTrailerCnmg(params):
    #log(params)
    get = params.get
    nume = unquote(get('nume'))
    url = unquote(get('link'))
    if not url: return
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Referer': url}
    htmlpage = fetchData(url, headers=headers)
    regex = '''<iframe[^>]+src=["\']([http].+?)"'''
    regex2 = '''<source[^>]+src=["\']([http].+?)\''''
    source = re.compile(regex, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(htmlpage)[0]
    getlink = fetchData(source, headers=headers)
    link = re.compile(regex2, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(getlink)[-1]
    item = xbmcgui.ListItem(nume + ' - Trailer', path=link)
    liz = xbmcgui.ListItem(nume)
    liz.setArt({'thumb': unquote(get('poster'))})
    liz.setInfo(type="Video", infoLabels={'Title':nume, 'Plot': unquote(get('plot'))})
    try:
        xbmc.Player().play(link, liz, False)
    except Exception as e: 
        showMessage("MRSP-Eroare", "%s" % e)

def getTrailerImdb(params):
    #log(params)
    get = params.get
    nume = unquote(get('nume'))
    url = unquote(get('link'))
    if not url: return
    headers = {'Accept-Language': 'ro-RO'}
    htmlpage = fetchData(url, headers=headers)
    regex = '''"(/video/imdb.+?)"'''
    try:
        source = re.compile(regex, re.IGNORECASE | re.DOTALL).findall(htmlpage)[0]
        source = "https://www.imdb.com%s" % source
        playTrailerImdb({'nume': nume, 'plot' : unquote(get('plot')), 'poster': unquote(get('poster')), 'link' : source})
    except: pass
        
def get_links(content, referer=None):
    try: from urlparse import urlparse
    except: from urllib.parse import urlparse
    links = []
    for link in content:
        if link is not None:
            if link and type(link) is tuple:
                name = striphtml(link[0])
                link = link[1]
            else: name = ''
            if link.startswith("//"):
                link = 'http:' + link #//ok.ru fix
            try:
                headers = {'User-Agent': USERAGENT}
                if referer: headers['Referer'] = referer
                result = requests.head(link, headers=headers, allow_redirects=False, timeout=4)
                link = result.headers['Location']
            except: pass
            if '2target.net' in link:
                try:
                    eurl = 'https://event.2target.net/links/go'
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'}
                    r = requests.get(link, headers=headers)
                    html = r.text
                    cj = r.cookies
                    csrf = re.findall(r'name="_csrfToken".+?value="([^"]+)', html)[0]
                    adf = re.findall(r'name="ad_form_data".+?value="([^"]+)', html)[0]
                    tokenf = re.findall(r'name="_Token\[fields\]".+?value="([^"]+)', html)[0]
                    tokenu = re.findall(r'name="_Token\[unlocked\]".+?value="([^"]+)', html)[0]
                    data = {'_method': 'POST',
                            '_csrfToken': csrf,
                            'ad_form_data': adf,
                            '_Token[fields]': tokenf,
                            '_Token[unlocked]': tokenu}

                    headers.update({'Referer': link, 'X-Requested-With': 'XMLHttpRequest'})
                    requests.utils.add_dict_to_cookiejar(cj, {'ab': '2'})
                    time.sleep(5)
                    strurl = requests.post(eurl, headers=headers, cookies=cj, data=data).json()['url']
                    name = '%s 2target->%s' % (name, strurl.split('/')[2].replace('www.', '').capitalize())
                    link = strurl
                    #links.append(('2target->%s' % host, strurl))
                except: pass
            elif 'ifp.re' in link:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:57.0) Gecko/20100101 Firefox/57.0'}
                    s = requests.Session()
                    try:
                        result = s.head(link, headers=headers, allow_redirects=False, timeout=10)
                        link2 = result.headers['Location']
                    except:
                        link2 = link
                    if link2.startswith("//"): link2 = 'http:' + link2
                    get_l = s.get(link2, headers=headers).text
                    link3 = re.findall('<iframe.+?src="(//plink.re/em.+?)"', get_l, re.IGNORECASE | re.DOTALL)[0]
                    if link3.startswith("//"): link3 = 'http:' + link3
                    html = s.get(link3, headers=headers).text
                    from resources.lib import jsunpack
                    html = jsunpack.unpack(re.search("eval(.*?)\{\}\)\)", html, re.DOTALL).group(1))
                    b_url = re.search("window.location.replace\((.+?)\)", html, re.DOTALL).group(1)
                    final_link = re.search(re.escape(b_url) + "=['\"](.+?)['\"]", html, re.DOTALL).group(1)
                    if final_link.startswith("//"): final_link = 'http:' + final_link
                    name = '%s ifp.re->%s' % (name, final_link.split('/')[2].replace('www.', '').capitalize())
                    link = final_link
                    #links.append(('ifp.re->%s' % host, final_link))
                except: pass
            elif 'iframe-secured.com' in link:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:57.0) Gecko/20100101 Firefox/57.0'}
                    extract = link[link.rfind("/")+1:]
                    link1 = 'https://iframe-secured.com/embed/iframe.php?u=%s' % extract
                    html = requests.get(link1, headers=headers).text
                    html = jsunpack.unpack(re.search("eval(.*?)\{\}\)\)", html, re.DOTALL).group(1))
                    final_link = re.search('''window.location.replace\(\\\\['"](.+?)\\\\['"]\)''', html, re.DOTALL).group(1)
                    name = '%s iframe->%s' % (name, final_link.split('/')[2].replace('www.', '').capitalize())
                    link = final_link
                    #links.append(('iframe->%s' % host, final_link))
                except: pass
            elif 'hideiframe.com' in link:
                try:
                    link1 = base64.b64decode(re.findall('php\?(.+?)$', link)[0])
                    name = '%s hideiframe->%s' % (name, link1.split('/')[2].replace('www.', '').capitalize())
                    link = link1
                    #links.append(('hideiframe->%s' % host, link1))
                except: pass
            elif 'vidsrc.me' in link:
                try:
                    s = requests.Session()
                    parsed = urlparse(link)
                    domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed)
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:57.0) Gecko/20100101 Firefox/57.0'}
                    html = s.get(link, headers=headers).content
                    first = re.search('iframe\s*src="(.+?)"', html)
                    firstlink = '%s%s' % (domain, first.group(1))
                    html = s.get(firstlink, headers=headers).content
                    second = re.search('query\s*=\s*"(.+?)".+?src\:\s*"(.+?)"', html, re.DOTALL)
                    headers['Referer'] = firstlink
                    third = s.head('%s%s%s' % (domain, second.group(2), second.group(1)), headers=headers)
                    link = third.headers['location']
                except: pass
            if 'vidnode.net/load.php' in link:
                try:
                    s = requests.Session()
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:57.0) Gecko/20100101 Firefox/57.0'}
                    html = s.get(link, headers=headers).content
                    lists = re.search('"(.+?download\?.+?)"', html).group(1)
                    html = s.get(lists, headers=headers).content
                    lists = re.findall('download.+?href="(.+?)"', html, re.DOTALL)
                    for linkes in lists:
                        label = re.search('\(([0-9P\-\sa-z]+)', linkes)
                        if label:
                            links.append((label.group(1), linkes))
                        else:
                            link = linkes
                except: pass
            if 'bazavox' in link or 'vidsource.me' in link or 'gcloud.live' in link:
                try:
                    parsed = urlparse(link)
                    domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed)
                    host = link.split('/')[2].replace('www.', '').capitalize()
                    vid = re.search('(?:v|f)/(.+?)$', link).group(1)
                    r = requests.post('%s/api/source/%s' % (domain, vid)).json()
                    for i in r.get('data'):
                        link = i.get('file')
                        links.append(('%s %s' % (host, i.get('label')), link))
                except: pass
                
            parsed_url1 = urlparse(link)
            if parsed_url1.scheme:
                import resolveurl as urlresolver
                hmf = urlresolver.HostedMediaFile(url=link, include_disabled=True, include_universal=True)
                if hmf.valid_url() == True:
                    host = link.split('/')[2].replace('www.', '').capitalize()
                    if name: host = '%s: %s' % (name, host) #+ ': ' + host
                    links.append((host, link))
    return links

def get_threads(threads, text=None, progress=None):
    if progress:
        current = 0
        dp = xbmcgui.DialogProgress()
        dp.create(__scriptname__, '%s...' % text if text else 'Căutare...')
        total = len(threads)
    [i.start() for i in threads]
    for i in threads:
        if progress:
            if i.isAlive():
                dp.update(1, 'Căutare in:', str(i.getName()))
                current += 1
                percent = int((current * 100) / total)
                dp.update(percent, "", str(i.getName()), "")
                if (dp.iscanceled()): break
        i.join()
    if progress:
        dp.close()

def get_sub(link, referer, direct=None):
    #log(link)
    try: from urlparse import urlparse
    except: from urllib.parse import urlparse
    if direct: 
        sub = link
        host = 'xngsrs'
    else:
        regex_sub_oload = '''(?:captions|track|subtitles)["\s]+src="(.+?)"'''
        regex_sub_vidoza = '''tracks[:\s]+(.+?])'''
        host = link.split('/')[2].replace('www.', '').capitalize()
        sub = None
        s = requests.Session()
        headers = {'Referer': referer, 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:57.0) Gecko/20100101 Firefox/70.1'}
        try:
            response = s.head(link, timeout=int(__settings__.getSetting('timeout')), headers=headers)
            try:
                response = s.head(response.headers['location'], timeout=int(__settings__.getSetting('timeout')), headers=headers)
            except: pass
            cT = response.headers['content-type']
        except: cT = ''
        if re.search('/html', cT, flags=re.I):
                sub_code = s.get(link, headers=headers).content
                try:
                    r = re.search('(eval\(function\(p,a,c,k,e,d\).+?\))\s+<', sub_code)
                    if r:
                        from resources.lib import jsunpack
                        r = jsunpack.unpack(r.group(1))
                        try: sub = re.search('\.?sub="(.+?)"', r).group(1)
                        except: pass
                        try:
                            if not sub:
                                subs = re.findall('(?:\{file:"([^\{]+)"\,label:"(.+?)"){1,}', r)
                                for sublink, label in subs:
                                    if re.search('rom', label, re.IGNORECASE):
                                        sub = sublink
                                        break
                                if not sub: sub = subs[0][0]
                        except: pass
                except: pass
                if not sub:
                    try:
                        sub = re.findall('''captions.+?src:.+?url=(.+?)['"]''', sub_code)[0]
                    except: pass
                try: 
                    if not sub: sub = re.findall(regex_sub_oload, sub_code, re.IGNORECASE | re.DOTALL)[0]
                except: pass
                try:
                    if not sub:
                        test = re.findall(regex_sub_vidoza, sub_code, re.IGNORECASE | re.DOTALL)[0]
                        test = (re.sub(r'([a-zA-Z]+):\s', r'"\1": ', test)).replace(', default:true', '')
                        test = eval(str(test))
                        for subs in test:
                            if subs.get('label') and subs.get('label') == 'Romanian':
                                sub = subs.get('file').replace('\\', '')
                                if sub.startswith('/'):
                                    parsed = urlparse(link)
                                    domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed)
                                    sub = domain + sub
                except: pass
                try: 
                    if not sub:
                        sub = re.findall(regex_sub_oload, sub_code, re.IGNORECASE | re.DOTALL)
                        if sub[0].startswith('/'):
                            parsed = urlparse(link)
                            domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed)
                            sub = domain + sub[0]
                        else: sub = sub[0]
                except: 
                    if not sub:
                        if re.search('c1_file=', link):
                            try: sub = re.findall('c1_file=(.+?)(?:&|$)', link)[0]
                            except: pass
                if not sub:
                    try:
                        sub = re.findall('url=(h.+?)"', sub_code)[0]
                    except: pass
    try:
        if py3: subtitle = xbmcvfs.translatePath('special://temp/')
        else: subtitle = xbmc.translatePath('special://temp/')
        try:
            sub = unquote(sub)
        except: pass
        if sub:
            if sub.startswith('//'): 
                sub = 'http:%s' % sub
            elif sub.startswith('/'):
                parsed = urlparse(link)
                domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed)
                sub = domain + sub
            subtitle = os.path.join(subtitle, '%s.ro.srt' % host)
            data = s.get(sub, headers=headers).content
            try:
                if re.search("WEBVTT\n|WEBVTT FILE\n", data):
                    data = wtttosrt(data)
            except: pass
            s = data.splitlines(True)
            while s and not s[0].strip():
                s.pop(0)
            while s and not s[-1].strip():
                s.pop()
            data  = "".join(s)
            with open(subtitle, 'w') as f: f.write(data)
            return subtitle
        else: return None
    except: return None

def wtttosrt(fileContents):
    replacement = re.sub(r'(\d\d:\d\d:\d\d).(\d\d\d) --> (\d\d:\d\d:\d\d).(\d\d\d)(?:[ \-\w]+:[\w\%\d:]+)*\n', r'\1,\2 --> \3,\4\n', fileContents)
    replacement = re.sub(r'(\d\d:\d\d).(\d\d\d) --> (\d\d:\d\d).(\d\d\d)(?:[ \-\w]+:[\w\%\d:]+)*\n', r'\1,\2 --> \3,\4\n', replacement)
    replacement = re.sub(r'(\d\d).(\d\d\d) --> (\d\d).(\d\d\d)(?:[ \-\w]+:[\w\%\d:]+)*\n', r'\1,\2 --> \3,\4\n', replacement)
    replacement = re.sub(r'WEBVTT\n', '', replacement)
    replacement = re.sub(r'WEBVTT FILE\n', '', replacement)
    replacement = re.sub(r'Kind:[ \-\w]+\n', '', replacement)
    replacement = re.sub(r'Language:[ \-\w]+\n', '', replacement)
    #replacement = re.sub(r'^\d+\n', '', replacement)
    #replacement = re.sub(r'\n\d+\n', '\n', replacement)
    replacement = re.sub(r'<c[.\w\d]*>', '', replacement)
    replacement = re.sub(r'</c>', '', replacement)
    replacement = re.sub(r'<\d\d:\d\d:\d\d.\d\d\d>', '', replacement)
    replacement = re.sub(r'::[\-\w]+\([\-.\w\d]+\)[ ]*{[.,:;\(\) \-\w\d]+\n }\n', '', replacement)
    replacement = re.sub(r'Style:\n##\n', '', replacement)
    return replacement

def randomagent():
    import random
    try:
        xrange
    except NameError:
        xrange = range
    BR_VERS = [
        ['%s.0' % i for i in xrange(18, 50)],
        ['37.0.2062.103', '37.0.2062.120', '37.0.2062.124', '38.0.2125.101', '38.0.2125.104', '38.0.2125.111', '39.0.2171.71', '39.0.2171.95', '39.0.2171.99',
         '40.0.2214.93', '40.0.2214.111',
         '40.0.2214.115', '42.0.2311.90', '42.0.2311.135', '42.0.2311.152', '43.0.2357.81', '43.0.2357.124', '44.0.2403.155', '44.0.2403.157', '45.0.2454.101',
         '45.0.2454.85', '46.0.2490.71',
         '46.0.2490.80', '46.0.2490.86', '47.0.2526.73', '47.0.2526.80', '48.0.2564.116', '49.0.2623.112', '50.0.2661.86', '51.0.2704.103', '52.0.2743.116',
         '53.0.2785.143', '54.0.2840.71'],
        ['11.0'],
        ['5.0', '8.0', '9.0', '10.0', '10.6']]
    WIN_VERS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1', 'Windows NT 6.0', 'Windows NT 5.1', 'Windows NT 5.0']
    FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
    RAND_UAS = ['Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
                'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
                'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko',
                'Mozilla/5.0 (compatible; MSIE {br_ver}; {win_ver}{feature}; Trident/6.0)']
    index = random.randrange(len(RAND_UAS))
    return RAND_UAS[index].format(win_ver=random.choice(WIN_VERS), feature=random.choice(FEATURES), br_ver=random.choice(BR_VERS[index]))

def ensure_str(string, encoding='utf-8'):
    try:
        if isinstance(string, unicode):
            string = string.encode(encoding)
        if not isinstance(string, str):
            string = str(string)
        return string
    except:
        return string

def thread_me(lists, parms, actiune, word=None):
    from .Core import Core
    from resources.lib import streams, torrents
    progress = '1' if __settings__.getSetting('progress') == 'true' else ''
    bigprogress = '1' if __settings__.getSetting('progress_type') == 'Mare' else ''
    recentslimit = str(__settings__.getSetting('recentslimit'))
    names = {}
    from threading import Thread
    try:
        from Queue import Queue, Empty
    except ImportError:
        from queue import Queue, Empty
    num_threads = 5
    queue = Queue()
    rezultat = {}
    iterator, filesList, left_searchers = 0, [], []
    for searcherName in lists:
        if searcherName in streams.streamsites:
            namet = streams.streamnames.get(searcherName).get('nume')
        else:
            namet = torrents.torrnames.get(searcherName).get('nume')
        names[searcherName] = namet
        left_searchers.append(namet)
    searchersList = names
    if progress:
        if bigprogress: progressBar = xbmcgui.DialogProgress()
        else: progressBar = xbmcgui.DialogProgressBG()
        progressBar.create('MRSP - Așteptați', 'Se încarcă')
    class CleanExit:
        pass
    def search_one(i, q):
        while True:
            if progress:
                iterator=100*int(len(searchersList)-len(left_searchers))/len(searchersList)
                progressBar.update(int(iterator), join_list(left_searchers))
                if bigprogress:
                    if progressBar.iscanceled():
                        progressBar.update(0)
                        progressBar.close()
                        return
            try:
                searcherFile = q.get_nowait()
                if searcherFile == CleanExit:
                    return
                searcher=searcherFile
                try:
                    if searcher in torrents.torrentsites: 
                        imp = getattr(torrents, searcher)
                    else:
                        imp = getattr(streams, searcher)
                    if actiune == 'recente' or actiune == 'categorii':
                        menu = imp().menu
                        if menu:
                            for name, url, switch, image in menu:
                                if name.lower() == 'recente' and actiune == 'recente':
                                    #log(sitee)
                                    params = {'site': searcher, 'link': url, 'switch': switch }
                                    rezultat[searcher]=Core().OpenSite(params, '1', recentslimit, new='1')
                                if switch == 'genuri' and actiune == 'categorii':
                                    params = {'site': searcher, 'link': url, 'switch': switch }
                                    rezultat[searcher]=Core().OpenSite(params, '2', None, new='1')
                    elif actiune == 'cautare':
                        try: rezultat[searcher] = imp().cauta(word)
                        except: rezultat[searcher] = ''
                    elif actiune == 'categorie':
                        if py3: parmsitems = parms.items()
                        else: parmsitems = parms.iteritems()
                        for sitekey, catvalue in parmsitems:
                            if searcher == sitekey:
                                rezultat[searcher]=Core().OpenSite(catvalue, '2', None, new='1')
                    try: left_searchers.remove(imp().name)
                    except: pass
                except Exception as e: 
                    log('eroare in thread_me:  ' + str(e))
                    pass
                q.task_done()
            except Empty:
                pass

    workers=[]
    for i in range(num_threads):
        worker = Thread(target=search_one, args=(i, queue))
        worker.setDaemon(True)
        worker.start()
        workers.append(worker)
    try: searchersListitems = searchersList.iteritems()
    except: searchersListitems = searchersList.items()
    for key, value in searchersListitems:
        queue.put(key)
    queue.join()
    for i in range(num_threads):
        queue.put(CleanExit)
    for w in workers:
        w.join()
    if progress:
        progressBar.update(0)
        progressBar.close()
    return rezultat
    
def openTorrent(params):
    get = params.get
    mode = get('Tmode')
    orig_url = get('orig_url')
    url = unquote(get('Turl'),'')
    site = unquote(get('Tsite'))
    info = get('info') or ''
    files = unquote(get('files'),None)
    download = get('download') == 'true'
    if files:
        from torrent2http import FileStatus
        files = eval(files)
    tid = get('Tid')
    surl = url
    s = __settings__.getSetting
    #from resources.lib import monitor
    #monitor.start(params=params)
    if url:
        surl = urllib.quote_plus(unescape(urllib.unquote_plus(surl)))
        if not mode:
            if s('clickactiontype') == '0':
                mode = 'browsetorrent'
            elif s('clickactiontype') == '1':
                mode = 'playdirect'
            elif s('clickactiontype') == '2':
                mode = 'playelementum'
            elif s('clickactiontype') == '3':
                mode = 'addtorrenter'
            elif s('clickactiontype') == '4':
                mode = 'addtransmission'
            elif s('clickactiontype') == '5':
                mode = 'playmrsp'
        if mode == 'browsetorrent':
            surl = '%s?action=openTorrent&url=%s&site=%s&info=%s' % (sys.argv[0], surl, site, quote(str(info)))
        elif mode == 'playdirect':
            surl = 'plugin://plugin.video.torrenter/?action=playSTRM&url=%s&not_download_only=True' % surl
        elif mode == 'playmrsp':
            surl = surl
        elif mode == 'playelementum':
            surl = 'plugin://plugin.video.elementum/playuri?uri=%s' %surl
        elif mode == 'addtransmission':
            #surl = 'plugin://plugin.video.torrenter/?action=downloadFilesList&url=%s' % surl
            surl = surl
        elif mode == 'addtorrenter':
            download = True
        elif mode == 'opentclient':
            surl = '%s?action=uTorrentBrowser' % (sys.argv[0])
        elif mode == 'opentintern':
            surl = '%s?action=internTorrentBrowser' % (sys.argv[0])
        elif mode == 'opentbrowser':
            surl = 'plugin://plugin.video.torrenter/?action=DownloadStatus'
        if not (mode == 'playelementum' or mode == 'playmrsp' or mode == 'addtransmission'):
            if (s('seedtransmission') == 'true' or s('%sseedtransmission' % site) == 'true') and not (s('seedtorrenter') == 'true' or s('%sseedtorrenter' % site) == 'true'):
                surl = '%s&seedtransmission=true' % (surl)
            else:
                if not (s('seedtransmission') == 'true' or s('%sseedtransmission' % site) == 'true') and (s('seedtorrenter') == 'true' or s('%sseedtorrenter' % site) == 'true'):
                    surl = '%s&seedtorrenter=true' % (surl)
        if mode == 'playelementum':
            xbmc.executebuiltin('RunPlugin(%s)' % surl)
        elif mode == 'addtransmission':
            from resources.lib.utorrent.net import Download
            if isRemoteTorr():
                t_dir = s('torrent_dir')
                empty = [None, '']
                if t_dir in empty:
                    if xbmcgui.Dialog().yesno(
                                'Remote Torrent-client',
                                'Nu ai configurat "Path" in Torrent Client',
                                'Vrei sa configurezi acum?'):
                        torrent_dir()
                        return
                else:
                    storage = t_dir
            else:
                storage = s('storage') or xbmcaddon.Addon(id='plugin.video.torrenter').getSetting('storage')
                
            if not (unquote(surl).startswith('http') or unquote(surl).startswith('magnet')):
                with open(unquote(surl), 'rb') as binary_file:
                    binary_file_data = binary_file.read()
                    base64_encoded_data = base64.b64encode(binary_file_data)
                Download().add(base64_encoded_data, storage, None, None)
                showMessage('Download Status', 'Added!')
            else:
                Download().add_url(unquote(surl), storage)
                showMessage('Download Status', 'Added!')
                    
        elif mode == 'playmrsp' or mode == 'addtorrenter':
            try: info = eval(info)
            except: info = eval(unquote(info))
            name = info.get('Title')
            seek_time = info.get('seek_time') or ''
            played_file = info.get('played_file') or ''
            infog = info
            infog.pop('seek_time', None)
            infog.pop('played_file', None)
            listitem = xbmcgui.ListItem(name)
            #log(info)
            listitem.setInfo(type='Video', infoLabels=infog)
            listitem.setArt({'thumb': info.get('Poster'), 'icon': info.get('Poster')})
            from resources.lib.mrspplayer import MRPlayer
            for_link = orig_url or surl
            cast_params = {'site': site, 'torrent': 'true', 'landing': for_link, 'link': for_link, 'switch': 'torrent_links', 'nume': name, 'info': info, 'favorite': 'check', 'watched': 'check'}
            listitem.setInfo('Video', {'Cast': [str(cast_params)]})
            try: 
                listitem.setContentLookup(False)
            except: pass
            MRPlayer().start(unquote(surl), cid=tid, params={'listitem': listitem, 'site': site, 'seek_time': seek_time, 'played_file': played_file},files=files, download=download)
        else:
            xbmc.executebuiltin('Container.Update(%s)' % surl)

def formatsize(size):
    try:
        kodisize = re.findall('[mbgik]+', size, re.IGNORECASE)
        sizes = {'K': 1024, 'M': 1048576, 'G': 1073742000}
        if kodisize:
            for letter in sizes.keys():
                if re.search('[mgk]+', size, re.IGNORECASE).group().lower() == letter.lower():
                    size = size.replace(kodisize[0],'').replace(',', '.')
                    size = float(size) * sizes[letter]
                    size = format(size, '.1f')
                    return size
                    break
    except: return 0

def is_writable(path):
    if not xbmcvfs.exists(path+os.sep):
        xbmcvfs.mkdirs(path)
    try:
        open(os.path.join(file_decode(path), 'temp'), 'w')
    except:
         return False
    else:
         os.remove(os.path.join(file_decode(path), 'temp'))
         return True
     
def file_decode(filename):
    pass
    try:
        filename = filename.decode('utf-8')  # ,'ignore')
    except:
        pass
    return filename

def cutFileNames(l):
    from difflib import Differ

    d = Differ()

    text = sortext(l)
    newl = []
    for li in l: newl.append(cutStr(li[0:len(li) - 1 - len(li.decode('utf-8').split('.')[-1])]))

    text1 = cutStr(text[0][0:len(text[0]) - 1 - len(text[0].decode('utf-8').split('.')[-1])])
    text2 = cutStr(text[1][0:len(text[1]) - 1 - len(text[1].decode('utf-8').split('.')[-1])])
    sep_file = " "
    result = list(d.compare(text1.split(sep_file), text2.split(sep_file)))

    start = ''
    end = ''

    for res in result:
        if str(res).startswith('-') or str(res).startswith('+') or str(res).startswith('.?'):
            break
        start = start + str(res).strip() + sep_file
    result.reverse()
    for res in result:
        if str(res).startswith('-') or str(res).startswith('+') or str(res).startswith('?'):
            break
        end = sep_file + str(res).strip() + end

    l = []
    for fl in newl:
        if cutStr(fl[0:len(start)]) == cutStr(start): fl = fl[len(start):]
        if cutStr(fl[len(fl) - len(end):]) == cutStr(end): fl = fl[0:len(fl) - len(end)]
        try:
            isinstance(int(fl.split(sep_file)[0]), int)
            fl = fl.split(sep_file)[0]
        except:
            pass
        l.append(fl)
    return l
    
def isSubtitle(filename, filename2):
    filename_if = filename[:len(filename) - len(filename.split('.')[-1]) - 1]
    filename_if = filename_if.split('/')[-1].split('\\')[-1]
    filename_if2 = filename2.split('/')[-1].split('\\')[-1][:len(filename_if)]
    # debug('Compare ' + filename_if.lower() + ' and ' + filename_if2.lower() + ' and ' + filename2.lower().split('.')[-1])
    ext = ['aqt', 'gsub', 'jss', 'sub', 'ttxt', 'pjs', 'psb', 'rt', 'smi', 'stl',
            'ssf', 'srt', 'ssa', 'ass', 'usf', 'idx', 'mpsub', 'rum', 'sbt', 'sbv', 'sup', 'w32']
    if filename2.lower().split('.')[-1] in ext and \
                    filename_if.lower() == filename_if2.lower():
        return True
    return False

#def decode(string, ret=None):
    #try:
        #string = string.decode('utf-8')
        #return string
    #except:
        #if ret:
            #return ret
        #else:
            #return string

def get_ids_video(contentList):
    ids_video = []
    allowed_video_ext = ['avi', 'mp4', 'mkv', 'flv', 'mov', 'vob', 'wmv', 'ogm', 'asx', 'mpg', 'mpeg', 'avc', 'vp3',
                         'fli', 'flc', 'm4v', 'iso', '3gp', 'ts']
    allowed_music_ext = ['mp3', 'flac', 'wma', 'ogg', 'm4a', 'aac', 'm4p', 'rm', 'ra']
    for extlist in [allowed_video_ext, allowed_music_ext]:
        for item in contentList:
            title = item[0]
            identifier = item[1]
            try:
                ext = title.split('.')[-1]
                if ext.lower() in extlist:
                    ids_video.append(str(identifier))
            except:
                pass
        if len(ids_video) > 1:
            break
    # print debug('[get_ids_video]:'+str(ids_video))
    return ids_video

def sortext(filelist):
    result = {}
    for name in filelist:
        ext = name.decode('utf-8').split('.')[-1]
        try:
            result[ext] = result[ext] + 1
        except:
            result[ext] = 1
    try: lol = result.iteritems()
    except: lol = result.items()
    lol = sorted(lol, key=lambda x: x[1])
    popext = lol[-1][0]
    result, i = [], 0
    for name in filelist:
        if name.decode('utf-8').split('.')[-1] == popext:
            result.append(name)
            i = i + 1
    result = sweetpair(result)
    return result

def sweetpair(l):
    from difflib import SequenceMatcher

    s = SequenceMatcher()
    ratio = []
    for i in range(0, len(l)): ratio.append(0)
    for i in range(0, len(l)):
        for p in range(0, len(l)):
            s.set_seqs(l[i], l[p])
            ratio[i] = ratio[i] + s.quick_ratio()
    id1, id2 = 0, 0
    for i in range(0, len(l)):
        if ratio[id1] <= ratio[i] and i != id2 or id2 == id1 and ratio[id1] == ratio[i]:
            id2 = id1
            id1 = i
        elif (ratio[id2] <= ratio[i] or id1 == id2) and i != id1:
            id2 = i

    return [l[id1], l[id2]]

def cutStr(s):
    try:
        return s.decode('utf-8').replace('.', ' ').replace('_', ' ').replace('[', ' ').replace(']', ' ').lower().strip()
    except:
        return s.replace('.', ' ').replace('_', ' ').replace('[', ' ').replace(']', ' ').lower().strip()

def cutFolder(contentList, tdir=None):
    dirList, contentListNew = [], []
    if py3:
        first = b'\\'
        second = b'/'
    else:
        first = '\\'
        second = '/'
    if len(contentList) > 1:
        common_folder = contentList[0][0]
        if first in common_folder:
            common_folder = common_folder.split(first)[0]
        elif second in common_folder:
            common_folder = common_folder.split(second)[0]
        common = True
        for item in contentList:
            if common_folder not in item[0]:
                common = False
                break
        for item in contentList:
            dir = None
            if common:
                item[0] = item[0][len(common_folder) + 1:]

            if first in item[0]:
                dir = item[0].split(first)[0]
            elif second in item[0]:
                dir = item[0].split(second)[0]
            elif not tdir:
                contentListNew.append(item)
            if tdir and ensure_str(dir) == ensure_str(tdir):
                tupleContent = list(item)
                tupleContent[0] = item[0][len(dir) + 1:]
                contentListNew.append(list(tupleContent))

            if not tdir and dir and dir not in dirList:
                dirList.append(dir)
        return dirList, contentListNew
    else:
        return dirList, contentList

def localize_path(path):
    import chardet
    if not isinstance(path, unicode):
        try:
            path = path.decode(chardet.detect(path).get('encoding') or 'utf-8')
        except:
            pass
    if not sys.platform.startswith('win'):
        path = encode_msg(path)
    return path

def encode_msg(msg):
    try:
        msg = isinstance(msg, unicode) and msg.encode(
            (sys.getfilesystemencoding() not in ('ascii', 'ANSI_X3.4-1968')) and sys.getfilesystemencoding() or 'utf-8') or msg
    except:
        import traceback
        log(traceback.format_exc())
        msg = ensure_str(msg)
    return msg

def TextBB(string, action=None, color=None):
    if action == 'b':
        string = '[B]' + string + '[/B]'
    return string

def get_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def isRemoteTorr():
    from resources.lib.utorrent.net import Download
    host_ip = get_ip()
    setip = Download().get_torrent_client().get('host')
    localhost = ['127.0.0.1', '0.0.0.0', 'localhost', host_ip]
    if not setip in localhost:
        return True

def torrent_dir():
    from resources.lib.utorrent.net import Download

    socket.setdefaulttimeout(3)
    list = Download().list()
    ret = 0
    if list and len(list) > 0:
        dirs = ["Keyboard"]
        for dl in list:
            if dl['dir'] not in dirs:
                dirs.append(dl['dir'])
            basename = os.path.dirname(dl['dir'])
            if basename not in dirs:
                dirs.append(basename)
            else:
                dirs.remove(basename)
                dirs.insert(1, basename)

        dialog = xbmcgui.Dialog()
        ret = dialog.select('Manual Torrent-client Path Edit', dirs)
    else:
        ret = 0

    if ret == 0:
        KB = xbmc.Keyboard()
        KB.setHeading('Manual Torrent-client Path Edit')
        KB.setDefault(__settings__.getSetting("torrent_dir"))
        KB.doModal()
        if (KB.isConfirmed()):
            __settings__.setSetting("torrent_dir", KB.getText())
    elif ret > 0:
        __settings__.setSetting("torrent_dir", dirs[ret])

def pbar(iterator=0,line1='',line2='', line3=''):
        res = []
        res2 = ''
        res.append(iterator)
        if line1:
            if py3:
                res2 += '%s\n' % line1
            else:
                res.append(line1)
        if line2:
            if py3:
                res2 += '%s\n' % line2
            else:
                res.append(line2)
        if line3:
            if py3:
                res2 += '%s' % line3
            else:
                res.append(line3)
        if py3:
            res.append(res2)
        return res

def check_torrent2http():
    from torrent2http import s
    from resources.lib.mrspplayer import MRPlayer
    result = MRPlayer().start('magnet:blahblah', cid='0', params={'cmdline_proc': '1'},files=None, download=False)
    if result:
        try:
            result = base64.b64decode(result)
            if py3:
                result = result.decode()
            if s.role == 'client' and (not s.mrsprole):
                result = result.replace('0.0.0.0', str(s.remote_host))
            return re.findall('(?=.*--resume-file[\s=](.+?)\s+--)?.+?--bind[\s=]([0-9]+(?:\.[0-9]+){3}:[0-9]+)', str(result))
        except BaseException as e:
            log(e)
            pass
    return None
        

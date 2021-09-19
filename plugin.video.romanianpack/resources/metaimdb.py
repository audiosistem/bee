# -*- coding: utf-8 -*-
from .functions import *

__plugin__ = sys.modules["__main__"].__plugin__
__settings__ = sys.modules["__main__"].__settings__
__scriptname__ = __settings__.getAddonInfo('name')
ROOT = sys.modules["__main__"].__root__

ACTION_PREVIOUS_MENU = 10
"""ESC action"""
ACTION_NAV_BACK = 92
"""Backspace action"""
ACTION_MOVE_LEFT = 1
"""Left arrow key"""
ACTION_MOVE_RIGHT = 2
"""Right arrow key"""
ACTION_MOVE_UP = 3
"""Up arrow key"""
ACTION_MOVE_DOWN = 4
"""Down arrow key"""
ACTION_MOUSE_WHEEL_UP = 104
"""Mouse wheel up"""
ACTION_MOUSE_WHEEL_DOWN = 105
"""Mouse wheel down"""
ACTION_MOUSE_DRAG = 106
"""Mouse drag"""
ACTION_MOUSE_MOVE = 107
"""Mouse move"""
ACTION_MOUSE_LEFT_CLICK = 100
"""Mouse click"""

class window(xbmcgui.WindowDialog):

    def get_n(self, content, nameorig, imdb):
        imdb_aka_container = '''>Also Known As\:(?:</.*?>\s+)?(.+?)\n'''
        #imdb_aka = '''"ipl-inline-list__item">\s+([^<].+?)\s+<''';
        #imdb_aspect_ratio = '''<h5>Aspect Ratio:<\/h5>(?:\s*)<div class="info-content">(.*)<\/div>''';
        #imdb_awards = '''<h5>Awards:<\/h5>(?:\s*)<div class="info-content">(.*)<\/div>''';
        imdb_cast_container = '''cast_list">(.+?)</table'''
        imdb_castandchar = '''primary_photo.+?src=".+?".+?/name/.+?>(.+?)<.+?"character">(.+?)</a''';
        #imdb_certification = '''<h5>Certification:</h5>(?:\s*)<div class=['"]info-content['"]>(.+?)</div>''';
        #imdb_color = '''<h5>Color:<\/h5>(?:\s*)<div class="info-content">(.*)<\/div>''';
        imdb_company_container = '''Production Co:(.+?)</div'''
        imdb_company = '''href="/company/.+?>(.+?)<''';
        imdb_country_container = '''Country:(.+?)</div'''
        imdb_country = '''href=.+?country_of.+?>(.+?)<'''
        imdb_seasons = '''href=.+?episodes\?season.+?>(.+?)<'''
        #imdb_creator = '''<h5>(?:Creator|Creators):</h5>(?:\s*)<div class=['"]info-content['"]>(.+?)</div>''';
        imdb_director_container = '''Director(?:s)?:(.+?)</div'''
        imdb_director = '''href="/name/.+?>(.+?)<''';
        imdb_info_container = '''"title_wrapper">(.+?)</div>\s+</div>'''
        imdb_genre = '''href=.+?genre.+?>(.+?)<''';
        imdb_id = '''((?:tt\d{6,})|(?:itle\?\d{6,}))/reference''';
        imdb_language_container = '''Language:(.+?)</div'''
        imdb_language = '''<a href=.+?language.+?>(.+?)</a>''';
        imdb_location = '''href=['"]/search/title\?locations=.+?['"]>(.+?)</a>''';
        imdb_mpaa = '''<h5><a href=['"]/mpaa['"]>MPAA</a>:</h5>(?:\s*)<div class=['"]info-content['"]>(.+?)</div>''';
        #imdb_name = '''<title>(.+?)</title>''';
        imdb_not_found = '''<h1 class=['"]findHeader['"]>No results found for ''';
        imdb_tagline = '''"summary_text">(.+?)<''';
        #imdb_plot_keywords = '''<h5>Plot Keywords:<\/h5>(?:\s*)<div class=['"]info-content['"]>(.*)<\/div>''';
        imdb_poster = '''<link rel=['"]image_src['"] href=['"](.+?)['"]>''';
        imdb_rating = '''"ratingValue":\s+"(.+?)"''';
        imdb_release_date = '''/releaseinfo.+?>(.+?)<''';
        #imdb_runtime_container = '''Runtime</td>(.+?)</ul'''
        imdb_runtime = '''datetime.+?>(.+?)<''';
        imdb_fanart = '''media_strip_thumb['"].+?src=['"](.+?)['"].*</a>'''
        #imdb_sound_mix = '''<h5>Sound Mix:<\/h5>(?:\s*)<div class=['"]info-content['"]>(.*)<\/div>''';
        imdb_plot = '''Storyline.+?inline canwrap.+?<span>(.+?)</s''';
        imdb_title = '''property=['"]og:title['"] content="(.+?)"''';
        imdb_title_orig = '''originalTitle">(.+?)<''';
        imdb_trailer = '''video_slate".+?href="(.+?)"'''
        imdb_trailer_first = '''trailer".+?"embedUrl": "(.+?)"'''
        #imdb_url = '''http://(?:.*\.|.*)imdb.com/(?:t|T)itle(?:\?|/)(..\d+)''';
        #imdb_user_review = '''<h5>User Reviews:<\/h5>(?:\s*)<div class="info-content">(.+?)<a''';
        imdb_votes = '''"ratingCount":(.+?)\,''';
        imdb_writer_container = '''Writer(?:s)?:(.+?)</div'''
        imdb_writer = '''href="/name/.+?>(.+?)<''';
        imdb_year = '''content=['"](?:.*)\(*(\d{4})\)'''
        imdb_created = '''"datePublished":\s"(.+?)"'''
        imdb_episodes = '''bp_sub_heading">(.+?)<'''
        imdb_more_like_this = '''div class="rec_item"(.+?)</a>'''
        self.trailer = None
        self.plot = ''
        self.cast = ''
        created = ''
        fundal = os.path.join(media,'ContentPanel.png')
        if content:
            getposter = self.get_data(imdb_poster, content)
            if getposter : poster = re.sub(r'@\..+?.(\w{3}$)', r'@.\1', getposter[0])
            else: poster = ''
            getbackdrop = self.get_data(imdb_fanart, content)
            if getbackdrop: backdrop = re.sub(r'@\..+?.(\w{3}$)', r'@.\1', getbackdrop[0])
            else: backdrop = poster
            title = replaceHTMLCodes(striphtml(self.get_data(imdb_title, content)[0]))
            try: original_title = self.get_data(imdb_title_orig, content)[0]
            except: original_title = ''
            try: production_countries = ", ".join(self.get_data(imdb_country, self.get_data(imdb_country_container, content)[0]))
            except: production_countries = ''
            getcast = self.get_data(imdb_cast_container, content)
            if getcast:
                castc = []
                for actor, role in self.get_data(imdb_castandchar, getcast[0]):
                    actor = replaceHTMLCodes(striphtml(actor))
                    role = replaceHTMLCodes(striphtml(role))
                    castc.append("%s%s" % (actor, (' [COLOR lime]as %s[/COLOR]' % role) if role else ''))
                castandchar = ", ".join(castc)
                castandchar = " ".join(castandchar.split())
            else: castandchar = ''
            try: genres = ", ".join(self.get_data(imdb_genre, self.get_data(imdb_info_container, content)[0]))
            except: genres = ''
            try: production_companies = ", ".join(self.get_data(imdb_company, self.get_data(imdb_company_container, content)[0]))
            except: production_companies = ''
            try: tagline = self.get_data(imdb_tagline, content)[0].strip()
            except: tagline = ''
            try: rating = self.get_data(imdb_rating, content)[0].strip()
            except: rating = ''
            try: votes = self.get_data(imdb_votes, content)[0].strip()
            except: votes = ''
            try: release_date = self.get_data(imdb_release_date, self.get_data(imdb_info_container, content)[0])[0]
            except: release_date = ''
            try: overview =self.get_data(imdb_plot, content)[0].strip()
            except: overview = ''
            try: aka = self.get_data(imdb_aka_container, content)[0]
            except: aka = ''
            try: spoken_languages = ", ".join(self.get_data(imdb_language, self.get_data(imdb_language_container, content)[0]))
            except: spoken_languages = ''
            try: writers = ", ".join(self.get_data(imdb_writer, self.get_data(imdb_writer_container, content)[0]))
            except: writers = ''
            try: runtime = self.get_data(imdb_runtime, self.get_data(imdb_info_container, content)[0])[0].strip()
            except: runtime = ''
            try: directors = ", ".join(self.get_data(imdb_director, self.get_data(imdb_director_container, content)[0]))
            except: directors = ''
            try: seasons = self.get_data(imdb_seasons, content)[0]
            except: seasons = ''
            if seasons:
                try: created = self.get_data(imdb_created, content)[0]
                except: pass
            try: episodes = self.get_data(imdb_episodes, content)[0]
            except: episodes = ''
            try: 
                trailer = self.get_data(imdb_trailer_first, content)
                trailer.extend(self.get_data(imdb_trailer, content))
                #x = requests.head('https://www.imdb.com/%s' % trailer)
                #if x.status_code == 404:
                    #trailer = self.get_data(imdb_trailer, content)[1]
            except: trailer = ''
            #traktwatch = self.get_data(imdb_id, content)[0] if self.get_data(imdb_id, content) else ''
            meta = {
                'poster_path': poster,
                'backdrop_path': backdrop,
                'Title': title,
                'original_title': original_title,
                'Country': production_countries,
                'castandchar': castandchar,
                'Genre': genres,
                'Company': production_companies,
                'overview': overview if overview else tagline,
                'Language': spoken_languages,
                'IMdb Rating': ('%s from %s votes' % (rating, votes)) if rating else '',
                'Released': release_date,
                'Tagline': tagline,
                'AKA': aka,
                'Writer': writers,
                'Director': directors,
                'Runtime': runtime,
                'Trailer': trailer,
                'Seasons': seasons,
                'First Episode': created,
                'Total aired': episodes}
            if imdb:
                meta['imdb'] = imdb
            data = ['poster_path', 'backdrop_path', 'castandchar', 'Title', 'original_title']
            if meta.get('backdrop_path'):
                back = meta.get('backdrop_path')
                self.back = xbmcgui.ControlImage(0, 0, 1280, 720, back)
                self.addControl(self.back)
            self.background = xbmcgui.ControlImage(0, 0, 1280, 720, fundal)
            self.addControl(self.background)
            if meta.get('poster_path'):
                self.poster = meta.get('poster_path')
                self.fanart = xbmcgui.ControlImage(50, 100, 270, 380, self.poster, aspectRatio=2)
                self.addControl(self.fanart)
            if meta.get('Title'):
                self.nume = meta.get('Title')
                self.title = xbmcgui.ControlLabel(500, 35, 1030, 30, ('Titlu: %s' % self.nume))
                self.addControl(self.title)
            if meta.get('original_title') :
                self.nume_original = meta.get('original_title')
                self.title_original = xbmcgui.ControlLabel(500, 65, 1030, 30, ('Titlul original: %s' % self.nume_original))
                self.addControl(self.title_original)
            if meta.get('castandchar'):
                self.cast = '[COLOR yellow]Cast:[/COLOR] %s' % meta.get('castandchar')
            self.title_site = xbmcgui.ControlLabel(100, 10, 1030, 30, ('Titlul pe site: %s' % nameorig))
            self.addControl(self.title_site)
            self.list = xbmcgui.ControlList (300, 110, 1030, 700)
            self.addControl(self.list)
            for info in meta:
                if info in data : continue
                if info == 'imdb':
                    #if meta.get(info) and __settings__.getSetting('trakt.user'):
                        #self.traktwatch = meta.get(info)
                    continue
                
                if info == 'Trailer':
                    if meta.get(info):
                        self.trailer = meta.get(info)
                    continue
                elif info == 'overview':
                    try: self.plot = '[COLOR yellow]Plot:[/COLOR] %s' % meta.get('overview').decode('utf-8')
                    except: self.plot = '[COLOR yellow]Plot:[/COLOR] %s' % meta.get('overview')
                    continue
                #elif info == 'number_of_seasons':
                    #meta[info] = '%s with a total of %s episodes' % (str(meta.get(info)), str(meta.get('number_of_episodes')))
                if meta.get(info): self.list.addItem ("[COLOR yellow]%s[/COLOR]: %s" % (info, meta.get(info)))
        self.detalii = xbmcgui.ControlTextBox(50, 527, 1200, 140)
        self.addControl(self.detalii)
        self.detalii.setText(self.plot)
        self.detalii.autoScroll(5000, 10000, 10000)
        self.button = xbmcgui.ControlButton(100, 670, 100, 30, 'Cast', focusedColor='0xFFFFFF00', focusTexture='')
        self.addControl(self.button)
        self.setFocus(self.button)
        self.buttont = xbmcgui.ControlButton(700, 670, 100, 30, 'Trailer', focusedColor='0xFFFFFF00', focusTexture='')
        self.addControl(self.buttont)
        #self.buttontrakt = xbmcgui.ControlButton(900, 670, 100, 30, 'Watch in Trakt', focusedColor='0xFFFFFF00', focusTexture='')
        #self.addControl(self.buttontrakt)
        if self.trailer: self.buttont.setEnabled(True)
        else: self.buttont.setEnabled(False)
        #if self.traktwatch: self.buttontrakt.setEnabled(True)
        #else: self.buttontrakt.setEnabled(False)
    
    def onControl(self, control):
        try:
            if control.getLabel() == 'Cast':
                self.button.setLabel('Plot')
                self.detalii.setText(self.cast)
            elif control.getLabel() == 'Plot':
                self.button.setLabel('Cast')
                self.detalii.setText(self.plot)
            elif control.getLabel() == 'Trailer':
                params = {'nume' : self.nume, 'plot': self.plot, 'poster': self.poster, 'link': self.trailer}
                self.close()
                playTrailerImdb(params)
            else:
                log(control.getLabel())
        except: pass
            
    def onClick(self, control):
        log(control)
    
    def onAction(self, action):
        #log(str(action.getId()))
        #log(str(self.buttont.getId()))
        #if not self.nume: self.close()
        if action.getId() == 92 or action.getId() == 10 or action.getId() == 11:
            self.close()
        if self.trailer:
            if (action.getId() == 1 or action.getId() == 3) and not (self.getFocus() == self.button):
                    self.setFocusId(self.getFocusId() - (1 if self.trailer else 2))
            if (action.getId() == 2 or action.getId() == 4) and not (self.getFocus() == (self.buttont if self.trailer else self.button)):
                    self.setFocusId(self.getFocusId() + (1 if self.trailer else 2))

    def get_data(self, regex, content):
        try: s = re.findall(regex, content, re.DOTALL | re.IGNORECASE)
        except: s = re.findall(regex, content.decode('utf-8'), re.DOTALL | re.IGNORECASE)
        return s

    def cleanstring(self, string):
        rep = {'Full summary &raquo;': '',
               'Full summary&nbsp;&raquo;': '',
               'Full synopsis &raquo;': '',
               'Full synopsis&nbsp;&raquo;': '',
               ' | ': '',
               'Add summary &raquo;': '',
               'Add summary&nbsp;&raquo;': '',
               'Add synopsis &raquo;': '',
               'Add synopsis&nbsp;&raquo;': '',
               'See more &raquo;': '',
               'See more&nbsp;&raquo;': '',
               'See why on IMDbPro.': '',
               '... (more)': ''}
        try: repiter = rep.iteritems()
        except: repiter = rep.items()
        rep = dict((re.escape(k), v) for k, v in repiter)
        pattern = re.compile("|".join(rep.keys()))
        string = pattern.sub(lambda m: rep[re.escape(m.group(0))], string)
        return string

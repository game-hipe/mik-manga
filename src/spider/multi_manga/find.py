from ...core.abstract.find import BaseFindEngine

class MultiMangaFindEngine(BaseFindEngine):
    FIND_URL = "https://multi-manga.today/index.php?do=search&subaction=search&search_start={page}&full_search=1&story={query}"
    GENRES_URL = "https://multi-manga.today/f/n.m.tags={query}/sort=date/order=desc/page/{page}/"
    
    @classmethod
    async def find(cls, query, engine, base_url, parser):
        instance = cls(
            query = query,
            engine = engine,
            base_url = base_url,
            parser = parser,
            find_method = 'query'
        )
        
        markup = await instance.engine.get(instance._build_page(), 'read')
        instance.max_page = instance.get_max_page(markup)
        
        instance.cashe[instance.page_now] = instance.parser.parse_page(markup)
        
        return instance
        
    @classmethod
    async def find_genres(cls, query, engine, base_url, parser):
        instance = cls(
            query = query,
            engine = engine,
            base_url = base_url,
            parser = parser,
            find_method = 'genres'
        )
        
        markup = await instance.engine.get(instance._build_page(), 'read')
        instance.max_page = instance.get_max_page(markup)
        
        instance.cashe[instance.page_now] = instance.parser.parse_page(markup)
        
        return instance
        
    def get_max_page(self, markup):
        soup = self.parser.build_soup(markup)
        try:
            return max(
                int(x.get_text(strip=True)) for x in soup.select('section.pagination a')
                if x.get_text(strip=True).isdigit()
            )
        except:
            return 1
        
    def _build_page(self):
        if self.find_method == 'query':
            return self.FIND_URL.format(
                page = self.page_now,
                query = self.query
            )
            
        return self.GENRES_URL.format(
            page = self.page_now,
            query = ','.join(self.query)
        )
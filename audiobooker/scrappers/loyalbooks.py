import feedparser
from audiobooker.scrappers import AudioBook, BookAuthor, BookGenre, \
    AudioBookSource


class LoyalBooksAudioBook(AudioBook):
    """
    """

    def __init__(self, title="", authors=None, description="", genres=None,
                 book_id="", runtime=0, url="", rss_url="", img="", rating=0,
                 language='english', from_data=None):
        """

        Args:
            title:
            authors:
            description:
            genres:
            book_id:
            runtime:
            url:
            rss_url:
            language:
            from_data:
        """
        AudioBook.__init__(self, title, authors, description, genres,
                           book_id, runtime, url, img, language)
        self.rss_url = rss_url or url + "/feed"
        self.rating = rating
        if not self.book_id and self.url:
            self.book_id = self.url.split("/")[-1]
        if from_data:
            self.from_json(from_data)
        self.raw = from_data or {}
        self.from_rss()

    def parse_page(self):
        soup = self.soup
        return {}

    @property
    def rss_data(self):
        """

        Returns:

        """
        return feedparser.parse(self.rss_url)

    @property
    def streamer(self):
        """

        """
        for stream in self.rss_data["entries"]:
            try:
                for url in stream["links"]:
                    if url["type"] == 'audio/mpeg':
                        yield url["href"]
            except Exception as e:
                print(e)
                continue

    @property
    def authors(self):
        """

        Returns:

        """
        return [BookAuthor(from_data=a) for a in self._authors]

    @property
    def genres(self):
        """

        Returns:

        """
        return [BookGenre(from_data=a) for a in self._genres]

    def from_json(self, json_data):
        """

        Args:
            json_data:
        """
        AudioBook.from_json(self, json_data)
        self.rss_url = json_data.get("url_rss", self.rss_url)
        self.rating = json_data.get("rating", self.rating)
        if not self.book_id and self.url:
            self.book_id = self.url.split("/")[-1]

    def calc_runtime(self, rss=None):
        rss = rss or self.rss_data["entries"]
        for rss_data in rss:
            runtime = rss_data["itunes_duration"].split(":")
            if len(runtime) == 1:  # seconds
                self.runtime += int(runtime[0])
            elif len(runtime) == 2:  # minutes : seconds
                self.runtime += int(runtime[1]) + (int(runtime[0]) * 60)
            elif len(runtime) == 3:  # hours : minutes : seconds
                self.runtime += int(runtime[2]) + (int(runtime[1]) * 60) + \
                                (int(runtime[0]) * 120)

    def from_rss(self):
        rss = self.rss_data["entries"]

        if self.runtime < 1:
            self.calc_runtime()

        if not self.url:
            self.url = rss[0]["link"]

        for rss_data in rss:
            last_name = ""
            first_name = rss_data["author"]
            names = last_name.split(" ")
            if len(names) > 1:
                first_name = names[0]
                last_name = " ".join(names[1:])
            author = {"first_name": first_name,
                      "last_name": last_name,
                      "id": ""}
            if author not in self._authors:
                self._authors.append(author)

    @property
    def as_json(self):
        bucket = self.raw
        bucket["url"] = self.url
        bucket["rss_url"] = self.rss_url
        bucket["img"] = self.img
        bucket["title"] = self.title
        bucket["authors"] = self._authors
        bucket["description"] = self._description
        bucket["genres"] = self._genres
        bucket["id"] = self.book_id
        bucket["runtime"] = self.runtime
        bucket["language"] = self.lang
        bucket["rating"] = self.rating
        return bucket

    def __repr__(self):
        """

        Returns:

        """
        return "LoyalBooksAudioBook(" + str(self) + ", " + self.book_id + ")"


class LoyalBooks(AudioBookSource):
    base_url = "http://www.loyalbooks.com"
    genres_url = "http://www.loyalbooks.com/genre-menu"
    _genres = None
    _genre_pages = None

    @staticmethod
    def scrap_genres():
        soup = LoyalBooks._get_soup(
            LoyalBooks._get_html(LoyalBooks.genres_url))
        urls = soup.find("div", {"class": "left"}).find_all("a")
        bucket = {}
        for url in urls:
            genre = url.text
            url = url["href"]
            if url.startswith("/genre"):
                url = "http://www.loyalbooks.com" + url
                bucket[genre] = url
        return bucket

    @staticmethod
    def get_genre(genre_id):
        """

        Args:
            genre_id:

        Returns:
            BookGenre

        """
        genre = ""
        if LoyalBooks._genres is not None:
            if genre_id <= len(LoyalBooks._genres):
                genre = LoyalBooks._genres[genre_id]
        else:
            genres = []
            for genre in LoyalBooks.scrap_genres():
                genres.append(genre)
            genres = sorted(genres)
            genre = genres[genre_id]
        return BookGenre(genre_id=genre_id, name=genre)

    def genre_id(self, genre):
        return str(self.genres.index(genre))

    @property
    def genre_pages(self):
        if LoyalBooks._genre_pages is None:
            try:
                LoyalBooks._genre_pages = LoyalBooks.scrap_genres()
            except Exception as e:
                LoyalBooks._genre_pages = {
                    'Adventure': 'http://www.loyalbooks.com/genre/Adventure',
                    'Advice': 'http://www.loyalbooks.com/genre/Advice',
                    'Ancient Texts': 'http://www.loyalbooks.com/genre/Ancient_Texts',
                    'Animals': 'http://www.loyalbooks.com/genre/Animals',
                    'Art': 'http://www.loyalbooks.com/genre/Art',
                    'Biography': 'http://www.loyalbooks.com/genre/Biography',
                    'Children': 'http://www.loyalbooks.com/genre/Children',
                    'Classics (antiquity)': 'http://www.loyalbooks.com/genre/Classics_antiquity',
                    'Comedy': 'http://www.loyalbooks.com/genre/Comedy',
                    'Cookery': 'http://www.loyalbooks.com/genre/Cookery',
                    'Dramatic Works': 'http://www.loyalbooks.com/genre/Dramatic_Works',
                    'Economics': 'http://www.loyalbooks.com/genre/Economics_Political_Economy',
                    'Epistolary fiction': 'http://www.loyalbooks.com/genre/Epistolary_fiction',
                    'Essay/Short nonfiction': 'http://www.loyalbooks.com/genre/Essay_Short_nonfiction',
                    'Fairy tales': 'http://www.loyalbooks.com/genre/Fairy_tales',
                    'Fantasy': 'http://www.loyalbooks.com/genre/Fantasy',
                    'Fiction': 'http://www.loyalbooks.com/genre/Fiction',
                    'Historical Fiction': 'http://www.loyalbooks.com/genre/Historical_Fiction',
                    'History': 'http://www.loyalbooks.com/genre/History',
                    'Holiday': 'http://www.loyalbooks.com/genre/Holiday',
                    'Horror/Ghost stories': 'http://www.loyalbooks.com/genre/Horror_Ghost_stories',
                    'Humor': 'http://www.loyalbooks.com/genre/Humor',
                    'Instruction': 'http://www.loyalbooks.com/genre/Instruction',
                    'Languages': 'http://www.loyalbooks.com/genre/Languages',
                    'Literature': 'http://www.loyalbooks.com/genre/Literature',
                    'Memoirs': 'http://www.loyalbooks.com/genre/Memoirs',
                    'Music': 'http://www.loyalbooks.com/genre/Music',
                    'Mystery': 'http://www.loyalbooks.com/genre/Mystery',
                    'Myths/Legends': 'http://www.loyalbooks.com/genre/Myths_Legends',
                    'Nature': 'http://www.loyalbooks.com/genre/Nature',
                    'Non-fiction': 'http://www.loyalbooks.com/genre/Non-fiction',
                    'Philosophy': 'http://www.loyalbooks.com/genre/Philosophy',
                    'Play': 'http://www.loyalbooks.com/genre/Play',
                    'Poetry': 'http://www.loyalbooks.com/genre/Poetry',
                    'Politics': 'http://www.loyalbooks.com/genre/Politics',
                    'Psychology': 'http://www.loyalbooks.com/genre/Psychology',
                    'Religion': 'http://www.loyalbooks.com/genre/Religion',
                    'Romance': 'http://www.loyalbooks.com/genre/Romance',
                    'Satire': 'http://www.loyalbooks.com/genre/Satire',
                    'Science': 'http://www.loyalbooks.com/genre/Science',
                    'Science fiction': 'http://www.loyalbooks.com/genre/Science_fiction',
                    'Sea stories': 'http://www.loyalbooks.com/genre/Sea_stories',
                    'Self Published': 'http://www.loyalbooks.com/genre/Self-Published',
                    'Short stories': 'http://www.loyalbooks.com/genre/Short_stories',
                    'Spy stories': 'http://www.loyalbooks.com/genre/Spy_stories',
                    'Teen/Young adult': 'http://www.loyalbooks.com/genre/Teen_Young_adult',
                    'Tragedy': 'http://www.loyalbooks.com/genre/Tragedy',
                    'Travel': 'http://www.loyalbooks.com/genre/Travel',
                    'War stories': 'http://www.loyalbooks.com/genre/War_stories',
                    'Westerns': 'http://www.loyalbooks.com/genre/Westerns'}
        return self._genre_pages or {}

    @property
    def genres(self):
        if LoyalBooks._genres is None:
            try:
                LoyalBooks._genres = list(LoyalBooks.genre_pages.keys())
            except Exception as e:
                LoyalBooks._genres = ['Advice', 'Instruction', 'Ancient ' \
                                                               'Texts',
                                      'Biography', 'Memoirs', 'Languages',
                                      'Myths/Legends', 'Holiday', 'Art',
                                      'Politics', 'Short stories', 'Romance',
                                      'Essay/Short nonfiction', 'Fiction',
                                      'Epistolary fiction', 'Science',
                                      'Nature', 'Dramatic Works',
                                      'Spy stories', 'History', 'Non-fiction',
                                      'Historical Fiction', 'Play', 'Children',
                                      'Satire', 'Humor',
                                      'Classics (antiquity)', 'Travel',
                                      'Religion', 'Adventure', 'Animals',
                                      'Psychology', 'Sea stories',
                                      'Horror/Ghost stories', 'Fantasy',
                                      'Cookery', 'Poetry', 'Self Published',
                                      'Westerns', 'Comedy', 'Music',
                                      'Economics', 'Fairy tales', 'Tragedy',
                                      'Teen/Young adult', 'Literature',
                                      'War stories', 'Science fiction',
                                      'Philosophy', 'Mystery']
        return sorted(self._genres) or []

    def scrap_by_genre(self, genre, start_page=1, max_pages=-1):
        url = self.genre_pages[genre] + "?page=" + str(start_page)
        max_pages = int(max_pages)
        soup = self._get_soup(self._get_html(url))
        el = soup.find("table", {"class": "layout2-blue"})
        if el is None:
            el = soup.find("table", {"class": "layout3"})

        books = el.find_all("td", {"class": "layout2-blue"})
        if not len(books):
            books = el.find_all("td", {"class": "layout3"})

        for book in books:
            try:
                url = self.base_url + book.find("a")[
                    "href"].strip()
                img = book.find("img")
                if img:
                    img = self.base_url + img["src"].strip()
                name = book.find("b")
                if name:
                    name = name.text.strip()
                    author = book.text.replace(name, "").strip()
                else:
                    name, author = book.find("div", {"class": "s-left"}) \
                        .text.split(" By: ")
                if book.find(id="star1") is not None:
                    rating = 1
                elif book.find(id="star2") is not None:
                    rating = 2
                elif book.find(id="star3") is not None:
                    rating = 3
                elif book.find(id="star4") is not None:
                    rating = 4
                elif book.find(id="star5") is not None:
                    rating = 5
                else:
                    rating = 0
                names = author.split(" ")
                if len(names):
                    first_name = names[0].strip()
                    last_name = " ".join(names[1:]).strip()
                else:
                    first_name = ""
                    last_name = author.strip()
                yield LoyalBooksAudioBook(title=name.strip(), url=url,
                                          img=img or "", rating=rating,
                                          genres=[BookGenre(name=genre,
                                                            genre_id=self.genre_id(
                                                                genre))],
                                          authors=[BookAuthor(
                                              first_name=first_name,
                                              last_name=last_name)])
            except Exception as e:
                pass  # probably an add

        # check if last page reached
        pages = soup.find("div", {"class": "result-pages"}).text
        if ">" not in pages:
            return

        # check if max_pages crawled
        if max_pages > 0 and int(start_page) > max_pages:
            return

        # crawl next page
        for book in self.scrap_by_genre(genre, start_page + 1, max_pages):
            yield book

    @staticmethod
    def get_audiobook(book_id):
        """

        Args:
            book_id:

        Returns:
            AudioBook

        """
        url = 'http://www.loyalbooks.com/book/' + book_id
        book = LoyalBooksAudioBook(url=url, title=book_id.replace("-", " "))
        return book


if __name__ == "__main__":
    from pprint import pprint

    # book = LoyalBooks.get_audiobook('Short-Science-Fiction-Collection-1')
    # book.play()

    # print(LoyalBooks.get_genre(40))

    scraper = LoyalBooks()
    for book in scraper.scrap_by_genre("Science fiction"):
        for a in book.authors:
            print(a.as_json)
        break

    # pprint(scraper.scrap_genres())
    # pprint(scraper.genres)
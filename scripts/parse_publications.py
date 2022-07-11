import rispy
from typing import List
from yattag import Doc
from selenium import webdriver
import os
import glob


class Scraper:
    def __init__(self) -> None:
        self.script_path = os.path.dirname(os.path.realpath(__file__))

    def download_ris_file(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        prefs = {}
        prefs["download.default_directory"] = self.script_path
        options.add_experimental_option("prefs", prefs)

        wd = webdriver.Chrome("chromedriver", options=options)
        wd.get(
            "https://opus4.kobv.de/opus4-bam/export/index/ris/searchtype/collection/id/16360/rows/100"
        )

    def remove_ris_file(self):
        for f in glob.glob(f"{self.script_path}/export*.ris"):
            os.remove(f)


class Reader:
    """Reader for ris file containing publications."""

    keys_to_keep = ["first_authors", "primary_title", "year"]

    def __init__(self, filepath: str):
        with open(filepath, "r") as bibliography_file:
            self.publications = rispy.load(bibliography_file)

    def filter(self, keys_to_keep: List[str] = None):
        if keys_to_keep == None:
            keys_to_keep = self.keys_to_keep
        self.publications = [
            {key: publication[key] for key in keys_to_keep}
            for publication in self.publications
        ]


class Writer:
    """Class that wraps the functionality of writing a given list of publications into an html file."""

    def __init__(self, publications: List[dict]):
        self._publications = publications
        self._years = list(set([int(pub["year"]) for pub in self._publications]))
        self._years.sort(
            reverse=True
        )  # We want to list publication years in descending order

    def write(self):
        text = self._create_html()
        with open("../publications.html", "w") as f:
            f.write(text)

    def _create_html(self) -> str:
        # Create header
        html = self._create_header()

        # Create body
        for year in self._years:
            html += self._create_year_content(year, self._publications)
            html += "\n\n"
        return html

    def _create_header(self):
        # Header for Jekyll purposes
        header = """---\ntitle: Publications\n---\n"""
        return header

    def _create_year_content(self, year: int, publications: list):
        doc, tag, text = Doc().tagtext()
        with tag("div", klass="publication-content"):
            with tag("h3", id=f"{year}"):
                text(f"{year}")
            with tag("ul", klass="publication-list"):
                for pub in publications:
                    if pub["year"] == str(year):
                        with tag("li"):
                            text(f"""{pub["primary_title"]}""")
                            doc.stag("br")
                            text(f"""Authors: {"; ".join(pub["first_authors"])}""")
                            doc.stag("br")
                            doc.stag("br")

        return doc.getvalue()


def main():
    scraper = Scraper()
    scraper.download_ris_file()
    reader = Reader("export.ris")
    reader.filter()
    publications = reader.publications
    writer = Writer(publications)
    writer.write()
    scraper.remove_ris_file()


if __name__ == "__main__":
    main()

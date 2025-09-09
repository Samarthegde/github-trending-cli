# -*- coding: utf-8 -*-
import click
import requests
import webbrowser
from lxml import etree

from . import writers

TRENDING_REPO_URL = "http://github.com/trending"
TRENDING_DEV_URL = "http://github.com/trending/developers"
HOME_PAGE = "https://github.com"

requests.packages.urllib3.disable_warnings()


def replace_new_lines_and_strip(s):
    return s.strip()


def replace_new_lines_and_multiple_spaces(s):
    return " ".join(s.replace("\n", "").split())


def read_page(url, timeout=5):

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0"
    }
    try:
        response = requests.get(url, timeout=timeout, headers=headers)
    except requests.exceptions.ConnectionError as e:  # noqa
        return (None, False)

    return (response, response.status_code)


def make_etree(url):
    response, status_code = read_page(url)
    if status_code == 200:
        response = etree.HTML(response.text)
    return (response, status_code)


def get_trending_repos(**kwargs):
    repos = []
    language = kwargs.get("language", None)
    timespan = kwargs.get("timespan", None)
    url = TRENDING_REPO_URL
    if language:
        url = url + "/" + language
    if timespan:
        url = url + "?since={}".format(timespan)
    tree, status_code = make_etree(url)
    if status_code == 200:
        repo_elements = tree.xpath('//article[@class="Box-row"]')
        for repo_element in repo_elements:
            repo_name_element = repo_element.xpath(
                './/h2[@class="h3 lh-condensed"]/a/@href'
            )
            repo_name = repo_name_element[0] if repo_name_element else "N/A"

            desc_element = repo_element.xpath(
                './/p[@class="col-9 color-fg-muted my-1 pr-4"]'
            )
            description = (
                " ".join(desc_element[0].itertext()).strip() if desc_element else "N/A"
            )

            lang_element = repo_element.xpath(
                './/span[@itemprop="programmingLanguage"]/text()'
            )
            lang = lang_element[0].strip() if lang_element else "N/A"

            stars_element = repo_element.xpath(
                './/a[contains(@href, "stargazers")]/text()'
            )
            stars = "".join(stars_element).strip() if stars_element else "N/A"

            repos.append(
                {
                    "repo_name": repo_name,
                    "description": description,
                    "stars": stars,
                    "language": lang,
                    "url": HOME_PAGE + str(repo_name),
                }
            )
    return repos


def get_trending_devs(**kwargs):
    devs = []
    language = kwargs.get("language", None)
    timespan = kwargs.get("timespan", None)
    url = TRENDING_DEV_URL
    if language:
        url = url + "/" + language
    if timespan:
        url = url + "?since={}".format(timespan)
    tree, status_code = make_etree(url)
    if status_code == 200:
        dev_elements = tree.xpath('//article[@class="Box-row d-flex"]')
        for dev_element in dev_elements:
            dev_name_element = dev_element.xpath('.//h1[@class="h3 lh-condensed"]/a')
            dev_name = dev_name_element[0].text.strip() if dev_name_element else "N/A"
            dev_url = dev_name_element[0].get("href") if dev_name_element else ""

            repo_name_element = dev_element.xpath(
                './/h1[@class="h4 lh-condensed"]/a/text()'
            )
            repo_name = repo_name_element[0].strip() if repo_name_element else "N/A"

            desc_element = dev_element.xpath('.//div[@class="f6 color-fg-muted mt-1"]')
            description = (
                " ".join(desc_element[0].itertext()).strip() if desc_element else ""
            )

            devs.append(
                {
                    "dev_name": dev_name,
                    "repo_name": repo_name,
                    "description": description,
                    "url": HOME_PAGE + dev_url,
                }
            )
    return devs


@click.command()
@click.option("--repo", "-r", is_flag=True, help="Lists the trending repositories.")
@click.option("--dev", "-d", is_flag=True, help="Lists the trending developers.")
@click.option("--lang", "-l", help="Specify the language")
@click.option("--week", "timespan", flag_value="weekly")
@click.option("--month", "timespan", flag_value="monthly")
@click.argument("goto", nargs=1, required=False, type=click.INT)
def main(repo, dev, lang, timespan, goto):
    """
    A command line utility to see the trending repositories
    and developers on Github
    """
    language = None
    if lang:
        language = str(lang)
    opts = {
        "language": language,
        "timespan": timespan,
    }
    try:
        if repo:
            repos = get_trending_repos(**opts)
            if goto:
                webbrowser.open(repos[goto - 1]["url"], new=2)
                return
            else:
                writers.print_trending_repos(repos)
        if dev:
            devs = get_trending_devs(**opts)
            if goto:
                webbrowser.open(devs[goto - 1]["url"], new=2)
                return
            else:
                writers.print_trending_devs(devs)
        # if the user does not passes any argument then list the trending repo
        if not repo and not dev:
            repos = get_trending_repos(**opts)
            if goto:
                webbrowser.open(repos[goto - 1]["url"], new=2)
                return
            else:
                writers.print_trending_repos(repos)
        return
    except Exception as e:
        click.secho(e.message, fg="red", bold=True)


if __name__ == "__main__":
    main()

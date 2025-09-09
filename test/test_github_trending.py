import unittest
import re

from click.testing import CliRunner

from githubtrending import trending as githubtrending

from . import data


class TestGithubTrending(unittest.TestCase):

    def test_read_page(self):
        for each in data.READ_PAGE_DATA:
            url = each.get("url")
            expected_status_code = each.get("status_code")
            response, status_code = githubtrending.read_page(url)
            self.assertEqual(status_code, expected_status_code)

    def test_make_etree(self):
        for each in data.READ_PAGE_DATA:
            url = each.get("url")
            expected_status_code = each.get("status_code")
            expected_title = each.get("title").encode("utf8")
            response, status_code = githubtrending.make_etree(url)
            self.assertEqual(status_code, expected_status_code)
            page_title = response.xpath("//title")[0].text.encode("utf8")
            self.assertIn(expected_title, page_title)

    def test_get_trending_repos(self):
        repos = githubtrending.get_trending_repos()
        self.assertGreater(len(repos), 0)  # Ensure some repos are returned
        self.assertEqual(
            data.TRENDING_REPO_COUNT, len(repos)
        )  # Check if the count is as expected

        # Assert structure and content of a sample repository
        if repos:
            sample_repo = repos[0]
            self.assertIn("repo_name", sample_repo)
            self.assertIn("description", sample_repo)
            self.assertIn("stars", sample_repo)
            self.assertIn("language", sample_repo)
            self.assertIn("url", sample_repo)
            self.assertNotEqual(sample_repo["repo_name"], "N/A")
            self.assertNotEqual(sample_repo["url"], "N/A")

    def test_get_trending_devs(self):
        devs = githubtrending.get_trending_devs()
        self.assertGreater(len(devs), 0)  # Ensure some devs are returned
        self.assertEqual(
            data.TRENDING_DEV_COUNT, len(devs)
        )  # Check if the count is as expected

        # Assert structure and content of a sample developer
        if devs:
            sample_dev = devs[0]
            self.assertIn("dev_name", sample_dev)
            self.assertIn("repo_name", sample_dev)
            self.assertIn("description", sample_dev)
            self.assertIn("url", sample_dev)
            self.assertNotEqual(sample_dev["dev_name"], "N/A")
            self.assertNotEqual(sample_dev["url"], "N/A")


class GithubTrendingCliTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        self.runner = CliRunner()
        super(GithubTrendingCliTest, self).__init__(*args, **kwargs)

    def test_github_trending_with_no_args(self):
        result = self.runner.invoke(githubtrending.main, [])
        assert result.exit_code == 0
        self.assertIn("TRENDING REPOSITORIES ON GITHUB", result.output)
        # Check for hyperlinks in output
        self.assertRegex(
            result.output,
            r"\033]8;;https://github.com/[\w\d\-/]+\033\\[\w\d\-/]+\033]8;;\033\\",
        )

    def test_github_trending_with_repo_as_args(self):
        result = self.runner.invoke(githubtrending.main, ["--repo"])
        assert result.exit_code == 0
        self.assertIn("TRENDING REPOSITORIES ON GITHUB", result.output)
        # Check for description truncation (e.g., "...")
        self.assertRegex(
            result.output, r"\.{3}"
        )  # Checks for "..." anywhere in the output
        # Check for hyperlinks in output
        self.assertRegex(
            result.output,
            r"\033]8;;https://github.com/[\w\d\-/]+\033\\[\w\d\-/]+\033]8;;\033\\",
        )

    def test_github_trending_with_dev_as_args(self):
        result = self.runner.invoke(githubtrending.main, ["--dev"])
        assert result.exit_code == 0
        self.assertIn("TRENDING DEVELOPERS ON GITHUB", result.output)
        # Check for description truncation (e.g., "...")
        self.assertRegex(
            result.output, r"\.{3}"
        )  # Checks for "..." anywhere in the output
        # Check for hyperlinks in output
        self.assertRegex(
            result.output,
            r"\033]8;;https://github.com/[\w\d\-/]+\033\\[\w\d\-/]+\033]8;;\033\\",
        )

    def test_github_trending_with_repo_and_lang_as_args(self):
        result = self.runner.invoke(githubtrending.main, ["--repo", "--lang=python"])
        assert result.exit_code == 0
        self.assertIn("TRENDING REPOSITORIES ON GITHUB", result.output)
        self.assertIn("Python", result.output)  # Ensure language filter works
        self.assertRegex(
            result.output,
            r"\033]8;;https://github.com/[\w\d\-/]+\033\\[\w\d\-/]+\033]8;;\033\\",
        )

    def test_github_trending_with_dev_and_timespan_as_args(self):
        result = self.runner.invoke(githubtrending.main, ["--dev", "--week"])
        assert result.exit_code == 0
        self.assertIn("TRENDING DEVELOPERS ON GITHUB", result.output)
        self.assertRegex(
            result.output,
            r"\033]8;;https://github.com/[\w\d\-/]+\033\\[\w\d\-/]+\033]8;;\033\\",
        )

    def test_github_trending_with_open_first_repo_in_browser(self):
        # This test only verifies the command invocation, not browser behavior
        self.runner.invoke(githubtrending.main, ["--repo", "1"])

    def test_github_trending_with_open_third_dev_in_browser(self):
        # This test only verifies the command invocation, not browser behavior
        self.runner.invoke(githubtrending.main, ["--dev", "3"])

    def test_github_trending_with_open_fifth_repo_in_browser_and_no_args(self):
        # This test only verifies the command invocation, not browser behavior
        self.runner.invoke(githubtrending.main, ["3"])


if __name__ == "__main__":
    unittest.main()

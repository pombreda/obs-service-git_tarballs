# Copyright 2012 SUSE Linux
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from contextlib import contextmanager
import imp
import io
import unittest

import mock

ghb = imp.load_source('ghb', 'git_tarballs')


class TestGitTarballs(unittest.TestCase):

    def test_version_parse(self):
        with mock_open(u"\nVersion: 2012.2.3+git.1355917214.0c8c2a3\n"):
            self.assertEqual('0c8c2a3',
                             ghb.get_commit_from_spec('example_pkg'))

    def test_version_parse_comment(self):
        with mock_open(
                u"\nVersion: 2012.2.3+git.1355917214.0c8c2a3 # oi comment\n"):
            self.assertEqual('0c8c2a3',
                             ghb.get_commit_from_spec('example_pkg'))

    def test_version_parse_plain(self):
        with mock_open(u"\nVersion: 2013.1.a110.g975c5ac\n"):
            self.assertEqual('975c5ac',
                             ghb.get_commit_from_spec('example_pkg',
                                                      plain_version=True))

    def test_version_parse_plain_from_custom(self):
        with mock_open(
                u"\nVersion: 2013.1.a110.g975c5ac+git.1363479139.975c5ac\n"):
            self.assertEqual('975c5ac',
                             ghb.get_commit_from_spec('example_pkg',
                                                      plain_version=True))


class TestGitParseUpdateSpec(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(
            "\nVersion: 14.0\n%setup -n bar\nSource: bar-14.0.tar.gz\n",
            ghb.parse_update_spec_file(
            "\nVersion: 13.14\n%setup -n foo\nSource: foo-13.14.tar.gz\n",
            "14.0", "bar", "bar-14.0.tar.gz"))

    def test_source_zero(self):
        self.assertEqual(
            "\nVersion: 14.0\n%setup -n bar\nSource: bar-14.0.tar.gz\n",
            ghb.parse_update_spec_file(
            "\nVersion: 13.14\n%setup -n foo\nSource: foo-13.14.tar.gz\n",
            "14.0", "bar", "bar-14.0.tar.gz"))

    def test_tabs(self):
        self.assertEqual(
            "\nVersion:\t14.0\n%setup\t-n bar\nSource:\tbar-14.0.tar.gz\n",
            ghb.parse_update_spec_file(
            "\nVersion:\t13.14\n%setup\t-n foo\nSource:\tfoo-13.14.tar.gz\n",
            "14.0", "bar", "bar-14.0.tar.gz"))

    def test_other_options_in_setup(self):
        self.assertEqual(
            "\nVersion:\t14.0\n"
            "%setup -q -a0 -n bar -f 33\nSource:\tbar-14.0.tar.gz\n",
            ghb.parse_update_spec_file(
            "\nVersion:\t13.14\n"
            "%setup -q -a0 -n foo -f 33\nSource:\tfoo-13.14.tar.gz\n",
            "14.0", "bar", "bar-14.0.tar.gz"))

    def test_no_n_option_in_setup(self):
        self.assertEqual(
            "\nVersion: 14.0\n%setup -q\nSource: bar-14.0.tar.gz\n",
            ghb.parse_update_spec_file(
                "\nVersion: 13.14\n%setup -q\nSource: foo-13.14.tar.gz\n",
                "14.0", "bar", "bar-14.0.tar.gz"))


@contextmanager
def mock_open(contents):
    with mock.patch("__builtin__.open", return_value=io.StringIO(contents)):
        yield
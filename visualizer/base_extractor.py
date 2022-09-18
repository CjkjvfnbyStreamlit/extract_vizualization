import inspect
from abc import ABC, abstractmethod
from typing import Any, BinaryIO, Callable

import streamlit as st

from visualizer.call_tracer import CommandRegister
from visualizer.table_creator import create_table


class ExtractBase(ABC):
    def __init__(self):
        st.set_page_config(layout="wide")

        self._file_names = self.get_file_names()
        self._archive, self._size = self._make_archive()
        self._screen_size = 1000

    @abstractmethod
    def get_title(self) -> str:
        """
        Return page title.
        """

    @abstractmethod
    def get_file_names(self) -> list[str]:
        """
        Return list of files to pack into archive.
        """

    def _make_archive(self) -> tuple[BinaryIO, int]:
        """
        Create a zip archive with files.
        """
        func, args = self.get_create_archive_func_and_args()
        return func(*args)

    @abstractmethod
    def get_create_archive_func_and_args(self) -> tuple[Callable, tuple]:
        """
        Return a function and its argument to create an archive.
        """

    def draw(self) -> None:
        left, right = st.columns(2)
        self.make_extraction_form(right, self._file_names, self._extraction_callback)
        left.markdown(self.get_title())
        with left.expander("Archive creation code"):
            func, _ = self.get_create_archive_func_and_args()
            function_text = inspect.getsource(func)
            text = ["```python", function_text, "```"]
            st.markdown("\n".join(text))

    @abstractmethod
    def extract_archive(self, files: list[str]) -> CommandRegister:
        """
        Extract archive and return list of commands.
        """

    def _extraction_callback(self, files: list[str]) -> None:
        commands = self.extract_archive(files)
        st.container().markdown(
            create_table(self._size, commands), unsafe_allow_html=True
        )

    @abstractmethod
    def make_extraction_form(
        self,
        container: Any,
        file_names: list[str],
        callback: Callable[[list[str]], None],
    ) -> None:
        """Make form to run extraction."""

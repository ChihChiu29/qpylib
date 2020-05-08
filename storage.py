"""Read/write data files.

We have preferred directories for data files for reading/writing. This module
is to help enforce the read/write best practice. Whenever you read/write a data
file, use this module. For directory convention see tools.settings module.
"""

import os
import pandas
import pathlib
import sqlite3

from qpylib import logging
from qpylib import storage
from qpylib.t import *


def GetProjectRootPath() -> str:
  """Gets the directory 2 levels up as the project directory."""
  return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def GetDataDirPath(sub_dir: str = '') -> str:
  return os.path.join(GetProjectRootPath(), 'data', sub_dir)


def GetCacheDirPath(cache_type_id: str) -> str:
  return os.path.join(GetProjectRootPath(), 'cache', cache_type_id)


def GetTmpDirPath(sub_dir: str = '') -> str:
  return os.path.join(GetProjectRootPath(), 'tmp', sub_dir)


def ReadData(filepath: str) -> str:
  """Reads a data file."""
  filepath_full = os.path.join(GetDataDirPath(), filepath)
  return open(filepath_full).read()


def WriteData(filepath: str, content: str) -> None:
  """Writes to a data file.

  Args:
    filepath: the relative path of the file. Subdirectories will be created.
    content: the content to write to the file.
  """
  filepath_full = os.path.join(GetDataDirPath(), filepath)
  directory = os.path.dirname(filepath_full)
  os.makedirs(directory, exist_ok=True)
  open(filepath_full, 'w').write(content)


def ReadByteData(filepath: str) -> bytes:
  """Reads a bytes data file."""
  filepath_full = os.path.join(GetDataDirPath(), filepath)
  return open(filepath_full, 'rb').read()


def WriteByteData(filepath: str, content: bytes) -> None:
  """Writes bytes to a data file.

  Args:
    filepath: the relative path of the file. Subdirectories will be created.
    content: the content to write to the file.
  """
  filepath_full = os.path.join(GetDataDirPath(), filepath)
  directory = os.path.dirname(filepath_full)
  os.makedirs(directory, exist_ok=True)
  open(filepath_full, 'wb').write(content)


class SQLiteConnection:
  """Provides interaction with a SQLite database."""

  def __init__(self, connection: sqlite3.Connection, debug_print: bool = False):
    self._conn = connection
    self._debug_print = debug_print

  def Close(self) -> None:
    """Closes the connection if open."""
    self._conn.close()

  def Execute(self, sql: Text) -> sqlite3.Cursor:
    """Executes a SQL command."""
    if self._debug_print:
      print(sql)
    return self._conn.execute(sql)

  def Commit(self) -> None:
    """Commits changes."""
    self._conn.commit()

  def CreateTable(
      self,
      table_name: Text,
      names_and_types: Iterable[Text]) -> None:
    """Creates a table.

    Args:
      table_name: the name of the table to create.
      names_and_types: an iterable of strings, each describes the name and
        type of a column in the table. For example:
        ["A string", "B string", "C integer"].
    """
    self.Execute('CREATE TABLE %s(%s);' % (
      table_name, ', '.join(names_and_types)))

  def DropTable(self, table_name: Text) -> None:
    """Removes a table."""
    self.Execute('DROP TABLE %s;' % table_name)

  def ListTables(self) -> List[Text]:
    """Returns a list of tables."""
    tables_raw = self.Execute(
      'SELECT name FROM sqlite_master WHERE type="table";').fetchall()
    if tables_raw:
      return [table_raw[0] for table_raw in tables_raw]
    else:
      return []

  def _InsertRowImpl(self, table_name: Text, values: Iterable[Any]) -> None:
    """Inserts a single row to a table.

    Args:
      table_name: the name of the table.
      values: the values in the row, in the same order of the columns as when
        the table was created.
    """
    self.Execute('INSERT INTO %s VALUES(%s);' % (
      table_name, ', '.join(
        '"%s"' % str(v).replace('"', '\'') for v in values)))

  def InsertRow(self, table_name: Text, values: Iterable[Any]) -> None:
    """Inserts a single row to a table.

    Args:
      table_name: the name of the table.
      values: the values in the row, in the same order of the columns as when
        the table was created.
    """
    self._InsertRowImpl(table_name, values)
    self.Commit()

  def InsertRows(self, table_name: Text, rows: Iterable[Iterable[Any]]) -> None:
    """Inserts multiple rows to a table.

    Since there is only one commit after insertion of all rows, calling this
    function is much more efficient than calling InsertRow in a loop.

    Args:
      table_name: the name of the table to write to.
      rows: the rows to write. Each row is an iterable of values in the same
        order of the columns as when the table was created.
    """
    for row in rows:
      self._InsertRowImpl(table_name, row)
    self.Commit()

  def IterRead(
      self,
      table_name: Text,
      columns: List[Text] = None,
      other_clauses: Text = None,
  ) -> Iterable[Tuple]:
    """Reads all rows from the table, returns an iterable.

    Args:
      table_name: the name of the table.
      columns: the names of the columns to read. If empty, all columns will be
        read.
      other_clauses: if set, append this string to the SQL command.

    Returns:
      An iterable of all the rows in the table. Each row is a tuple of all
      columns.
    """
    if not columns:
      columns_command = '*'
    else:
      columns_command = ','.join(columns)

    if not other_clauses:
      other_clauses = ''

    return self.Execute('SELECT %s FROM %s %s;' % (
      columns_command, table_name, other_clauses))

  def Read(
      self,
      table_name: Text,
      columns: List[Text] = None,
      other_clauses: Text = None,
  ) -> List[Tuple]:
    """Reads all rows from the table, returns all content.

    Args:
      table_name: the name of the table.
      columns: the names of the columns to read. If empty, all columns will be
        read.
      other_clauses: if set, append this string to the SQL command.

    Returns:
      An iterable of all the rows in the table. Each row is a tuple of all
      columns.
    """
    return self.IterRead(
      table_name, columns=columns, other_clauses=other_clauses).fetchall()


def OpenSQLiteConnection(
    database_file_name: Text = None,
    debug_print: bool = False) -> SQLiteConnection:
  """Opens a connection to a database file under data folder.

  Args:
    database_file_name: the name of the database file, defaults to a string
      that creates a in-memory database.
    debug_print: whether to print out SQL commands for debugging.

  Returns:
    A connection to the given database.
  """
  if database_file_name:
    database_file_path = GetDataDirPath(database_file_name)
  else:
    database_file_path = ':memory:'
  return SQLiteConnection(
    sqlite3.connect(database_file_path), debug_print=debug_print)


class DataFrameStorage:
  """Helps to read and save data frames for a given project."""
  
  def __init__(self, project_name: Text):
    self._project = project_name
    
    pathlib.Path(storage.GetDataDirPath(self._project)).mkdir(
        parents=True, exist_ok=True)
    
  def Save(self, df: pandas.DataFrame, filename: Text):
    full_path = self._GetFullPath(filename)
    logging.info('saving to: %s', full_path)
    df.to_json(full_path)
    
  
  def Load(self, filename: Text) -> pandas.DataFrame:
    full_path = self._GetFullPath(filename)
    logging.info('reading from: %s', full_path)
    return pandas.read_json(full_path)
  
  
  def Exists(self, filename: Text) -> bool:
    full_path = self._GetFullPath(filename)
    result = os.path.exists(full_path)
    logging.info('%s exists: %s', full_path, result)
    return result


  def _GetFullPath(self, filename: Text) -> Text:
    return storage.GetDataDirPath(os.path.join(self._project, filename))

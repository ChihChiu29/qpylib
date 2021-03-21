"""Read/write data files.

We have preferred directories for data files for reading/writing. This module
is to help enforce the read/write best practice. Whenever you read/write a data
file, use this module. For directory convention see tools.settings module.
"""
import abc
import datetime
import os
import pathlib
import pickle
import sqlite3

import pandas

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


class StringTable:
  """Provides an easy way to store strings in a database."""
  
  TABLE_NAME = 'StringTable'

  def __init__(
      self,
      database_file_name: Optional[str] = None,
      debug_print: bool = False):
    """Constructor.
    
    Args:
      storage_name: name of this storage / table.
    """
    self._conn = OpenSQLiteConnection(
        database_file_name, debug_print=debug_print)
    self._PrepareConnection()

  def Close(self) -> None:
    """Closes the connection if open."""
    self._conn.close()
    
  def _PrepareConnection(self) -> None:
    tables = self._conn.ListTables()
    if self.TABLE_NAME not in tables:
      self._conn.CreateTable(
        self.TABLE_NAME,
        ['ts TIMESTAMP', 'key string', 'content string'])

  def AddValue(
      self,
      content: str, 
      ts: Optional[datetime.datetime] = None,
      key: Optional[str] = '',
      commit: bool = True,
  ) -> None:
    """Adds a string value to the table.
    
    Args:
      content: the value to add.
      ts: timestamp for this value, used for search. If not set, the current
        timestamp is used.
      key: optional key for the value.
    """
    if ts is None:
      ts = datetime.datetime.now()
    self._conn._InsertRowImpl(self.TABLE_NAME, [ts.timestamp(), key, content])
    if commit:
      self._conn.Commit()
    
  def AddValues(self, contents: Iterable[str]) -> None:
    for content in contents:
      self.AddValue(content, commit=False)
    self._comm.Commit()
    
  def AddValueMap(self, contents: Dict[str, str]) -> None:
    for key, value in contents.items():
      self.AddValue(value, key=key, commit=False)
    self._comm.Commit()
    
  def AddValuesFull(self, contents: Iterable[Tuple[datetime.datetime, str, str]]):
    for ts, key, value in contents:
      self.AddValue(value, ts=ts, key=key, commit=False)
    self._conn.Commit()
    
  def ReadIter(
    self,
    since: Optional[datetime.datetime] = None,
    until: Optional[datetime.datetime] = None,
    key: Optional[str] = None,
  ) -> Iterable[str]:
    """Reads multiple values.
    
    Args:
      since: search from this timestamp. If none, search everything.
      until: search until this timestamp. If none, search until now.
      key: search values which keys contain this value. Note that this means
        it is effectively a "subkey", and you can use this to implement "tags".
    
    Returns:
      An iterable of string values.
    """
    if until is None:
      until = datetime.datetime.now()
    if since:
      since_clause = 'AND ts >= %s' % since.timestamp()
    else:
      since_clause = ''
    if key:
      key_clause = 'AND INSTR(key, "%s")' % key
    else:
      key_clause = ''
    query = '''
    SELECT content
    FROM %(table_name)s
    WHERE
      ts <= %(until_timestamp)s
      %(since_clause)s
      %(key_clause)s
    ;
    ''' % {
      'table_name': self.TABLE_NAME,
      'until_timestamp': until.timestamp(),
      'since_clause': since_clause,
      'key_clause': key_clause,
    }
    return self._conn.Execute(query)
    
  def Read(
    self,
    since: Optional[datetime.datetime] = None,
    until: Optional[datetime.datetime] = None,
    key: Optional[str] = None,
  ) -> List[str]:
    return list(self.ReadIter(since=since, until=until, key=key))


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


class AbstractStorage(abc.ABC):
  """Base class for saving and loading data to files."""

  def __init__(self, project_name: Text):
    self._project = project_name

    pathlib.Path(storage.GetDataDirPath(self._project)).mkdir(
      parents=True, exist_ok=True)

  @abc.abstractmethod
  def Save(self, data: Any, filename: Text):
    """Save action; subclass can override data type."""
    pass

  def Load(self, filename: Text) -> Any:
    """Loads from an existing file or None; type depends on subclass."""
    if self.Exists(filename):
      try:
        return self._LoadImpl(filename)
      except EOFError as e:
        logging.warning(e)
        return None
    return None

  @abc.abstractmethod
  def _LoadImpl(self, filename: Text) -> Any:
    """Actual implementation of the load function."""
    pass

  def Exists(self, filename: Text) -> bool:
    full_path = self._GetFullPath(filename)
    result = os.path.exists(full_path)
    logging.info('%s exists: %s', full_path, result)
    return result

  def _GetFullPath(self, filename: Text) -> Text:
    return storage.GetDataDirPath(os.path.join(self._project, filename))


class DataFrameStorage(AbstractStorage):
  """Helps to save and load data frames for a given project."""

  def __init__(self, project_name: Text):
    super().__init__(project_name)

  # @Override
  def Save(self, df: pandas.DataFrame, filename: Text):
    full_path = self._GetFullPath(filename)
    logging.info('saving to: %s', full_path)
    df.to_json(full_path)

  # @Override
  def _LoadImpl(self, filename: Text) -> pandas.DataFrame:
    full_path = self._GetFullPath(filename)
    logging.info('reading from: %s', full_path)
    return pandas.read_json(full_path)


class PickleStorage(AbstractStorage):
  """Helps to save and load objects using pickle."""

  # @Override
  def Save(self, obj: Any, filename: Text):
    full_path = self._GetFullPath(filename)
    logging.info('saving to: %s', full_path)
    pickle.dump(obj, open(full_path, 'wb'))

  # @Override
  def _LoadImpl(self, filename: Text) -> Any:
    full_path = self._GetFullPath(filename)
    logging.info('reading from: %s', full_path)
    return pickle.load(open(full_path, 'rb'))

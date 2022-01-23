# -*- coding: utf-8 -*-
"""Module responsible for executing database operations."""
from psycopg2 import sql, extensions, connect, OperationalError
from configparser import ConfigParser


class DatabaseUser:
    """Class that performs operations on database. Starting point.

    - `db_config` -- parses configuration file
    - `connect_to_db` -- establishing database connection
    """
    def __init__(self):
        """Initiates parsing of the configuration file."""
        self.login_data = self.db_config()

    @staticmethod
    def db_config(filename: str = '../config/database.ini', section: str = 'currency') -> tuple:
        """Parses configuration file.

        Args:
            filename: path to the .ini configuration file
            section: a section in file containing database configurations

        Returns:
            tuple with configuration data
        """
        parser = ConfigParser()
        parser.read(filename)
        if parser.has_section(section):
            db = [param[1] for param in parser.items(section)]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))
        return tuple(db)

    def connect_to_db(self) -> extensions.connection:
        """Database connection.

        Unpacks configuration file and connects to database.

        Returns:
            psycopg2.extensions.connection. A connection thanks which we can perform operations on database.
        """
        try:
            return connect(dbname=self.login_data[0], user=self.login_data[1],
                           host=self.login_data[2], port=self.login_data[3], password=self.login_data[4])
        except OperationalError as e:
            raise OperationalError('Connecting Failed. Check that your database still exists.') from e


class DatabaseReadonlyUser(DatabaseUser):
    """DatabaseUser class extension. Provides an extended method of retrieving data from database.

    - `select_where` -- retrieves currency exchange data from database.
    """
    def select_where(self,
                     currency: tuple | str | None = None,
                     date_from: str | None = None,
                     date_to: str | None = None) -> tuple:
        """Method that retrieves currency exchange data from database.

        Depending on the number of additional arguments, received answer is more precise.

        Args:
            currency: currency that is checked
            date_from: since when we need to check currency exchange rate
            date_to: until when we need to check currency exchange rate
        Returns:
            tuple containing information about the exchange rate
        """
        con = self.connect_to_db()
        cur = con.cursor()
        to_execute = f"""
        SELECT currency, code, bid, ask, date
        FROM currency_rate
        """
        if type(currency) == str:
            to_execute = to_execute + f"""WHERE code = '{currency}'
            """
        elif type(currency) == tuple:
            to_execute = to_execute + f"""WHERE code in {currency}
            """
        elif (currency is None and date_from is not None) | (currency is None and date_to is not None):
            to_execute = to_execute + """WHERE code IS NOT NULL """
        if date_from is not None:
            to_execute = to_execute + f"""AND date >= '{date_from}'
            """
        if date_to is not None:
            to_execute = to_execute + f"""AND date <= '{date_to}'
            """
        to_execute = to_execute + 'ORDER BY date DESC;'
        cur.execute(to_execute)
        content_table = tuple(cur.fetchall())
        con.commit()
        cur.close()
        con.close()
        return content_table


class DatabaseSyncUser(DatabaseUser):
    """DatabaseUser class extension.
    Introduces the basic method for retrieving data and a method for placing data in the database.

    - `download_date` -- retrieves last synchronization date.
    - `insert_data` -- puts data from most recent sync into database.
    """
    def __connect_to_db(self) -> extensions.connection:
        """Database connection.

        Extended method DatabaseUser.connect_to_db, which in case of failure while connecting to the database,
        creates a new database and table.

        Returns:
            psycopg2.extensions.connection. A connection thanks which we can perform operations on database.
        """
        try:
            return connect(dbname=self.login_data[0], user=self.login_data[1],
                           host=self.login_data[2], port=self.login_data[3], password=self.login_data[4])
        except OperationalError:
            print('Connecting Failed. Making a new database...')
            self.__create_currency_db()
            self.__create_new_table()
            return connect(dbname=self.login_data[0], user=self.login_data[1],
                           host=self.login_data[2], port=self.login_data[3], password=self.login_data[4])

    def download_date(self):
        """Retrieves last synchronization date.

        Returns:
            most recent datetime.date object
        """
        con = self.__connect_to_db()
        cur = con.cursor()
        cur.execute(f"""SELECT date FROM currency_rate ORDER BY date DESC;""")
        content_table = cur.fetchall()[0][0]
        con.commit()
        cur.close()
        con.close()
        return content_table

    def insert_data(self, values: tuple) -> None:
        """Puts data from most recent sync into database.

        Args:
            values: tuple with five values: string, string, string, string and date.
        """
        con = self.__connect_to_db()
        cur = con.cursor()
        to_execute = f""" INSERT INTO currency_rate (currency, code, bid, ask, date) VALUES (%s,%s,%s,%s,%s)"""
        cur.execute(to_execute, values)
        con.commit()
        cur.close()
        con.close()

    def __create_currency_db(self) -> None:
        """Creates new database in database.

        Creates a new database in which currency table will be placed.
        """
        try:
            default_con = connect(dbname='postgres', user=self.login_data[1], host=self.login_data[2],
                                  port=self.login_data[3], password=self.login_data[4])
        except OperationalError as e:
            raise OperationalError('Default database could not be found.'
                                   'Check the provided configuration data and try again.') from e
        default_con.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = default_con.cursor()
        cur.execute(sql.SQL("CREATE DATABASE {} ENCODING = 'UTF8'").format(
            sql.Identifier('currency'))
        )
        cur.close()
        default_con.close()

    def __create_new_table(self) -> None:
        """Creates new tables in database.

        Creates a new table in which currency rates will be placed.
        """
        con = self.__connect_to_db()
        cur = con.cursor()
        try:
            cur.execute(f'CREATE TABLE currency_rate (currency TEXT, code TEXT, bid TEXT, ask TEXT, date date);')
            con.commit()
            cur.close()
            con.close()
        except Exception as error:
            print(f'A problem occurred while creating the table: {error}')
            cur.close()
            con.close()


class DatabaseCleaningUser(DatabaseUser):
    """DatabaseUser class extension. Introduces a method that allows to delete records from database.

    - `delete_old_data` -- deletes all sync data that happened before the specified date.
    """
    def delete_old_data(self, date_scope) -> None:
        """Deletes all sync data that happened before the specified date.

        Args:
            date_scope: date from which syncs data should be removed (datetime.date)
        """
        con = self.connect_to_db()
        cur = con.cursor()
        cur.execute(f"""
            DELETE FROM currency_rate
            WHERE date < timestamp '{date_scope}'
        """)
        con.commit()
        cur.close()
        con.close()

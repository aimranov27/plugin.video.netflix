# -*- coding: utf-8 -*-
"""
    Copyright (C) 2017 Sebastian Golasch (plugin.video.netflix)
    Copyright (C) 2019 Stefano Gottardo - @CastagnaIT (original implementation module)
    Functions to create a new SQLite database

    SPDX-License-Identifier: MIT
    See LICENSES/MIT.md for more information.
"""
from contextlib import closing
import sqlite3 as sql

import resources.lib.database.db_utils as db_utils
from resources.lib.utils.logging import LOG


def create_database(db_file_path, db_filename):
    if db_filename not in (db_utils.LOCAL_DB_FILENAME, db_utils.SHARED_DB_FILENAME):
        return
    LOG.debug('Creating missing tables in SQLite database {}', db_filename)
    with closing(sql.connect(db_file_path, timeout=15)) as conn:
        with conn:
            # Kodi can start the service and menu together on first launch.
            # Serialize creators and publish the whole schema in one transaction.
            conn.execute('BEGIN IMMEDIATE')
            cur = conn.cursor()
            if db_filename == db_utils.LOCAL_DB_FILENAME:
                _create_local_database(cur)
            else:
                _create_shared_database(cur)


def _create_local_database(cur):
    """Create missing local tables within the caller's transaction."""

    table = str('CREATE TABLE IF NOT EXISTS app_config ('
                'ID    INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
                'Name  TEXT    UNIQUE NOT NULL,'
                'Value TEXT);')
    cur.execute(table)

    table = str('CREATE TABLE IF NOT EXISTS menu_data ('
                'ContextId TEXT PRIMARY KEY NOT NULL,'
                'Value     TEXT);')
    cur.execute(table)

    table = str('CREATE TABLE IF NOT EXISTS profiles ('
                'ID        INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,'
                'Guid      TEXT    NOT NULL UNIQUE,'
                'IsActive  BOOLEAN DEFAULT (0) NOT NULL,'
                'SortOrder INTEGER NOT NULL);')
    cur.execute(table)

    table = str('CREATE TABLE IF NOT EXISTS profiles_config ('
                'Guid  TEXT NOT NULL,'
                'Name  TEXT NOT NULL,'
                'Value TEXT,'
                'PRIMARY KEY (Guid, Name ),'
                'FOREIGN KEY (Guid)'
                'REFERENCES Profiles (Guid) ON DELETE CASCADE ON UPDATE CASCADE);')
    cur.execute(table)

    table = str('CREATE TABLE IF NOT EXISTS session ('
                'Name  TEXT PRIMARY KEY NOT NULL,'
                'Value TEXT);')
    cur.execute(table)

    table = str('CREATE TABLE IF NOT EXISTS settings_monitor ('
                'Name  TEXT PRIMARY KEY NOT NULL,'
                'Value TEXT);')
    cur.execute(table)

    table = str('CREATE TABLE IF NOT EXISTS search ('
                'ID         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,'
                'Guid       TEXT    NOT NULL REFERENCES profiles (Guid) ON DELETE CASCADE ON UPDATE CASCADE,'
                'Type       TEXT    NOT NULL,'
                'Value      TEXT    NOT NULL,'
                'Parameters TEXT,'
                'LastAccess TEXT);')
    cur.execute(table)


def _create_shared_database(cur):
    """Create missing shared tables within the caller's transaction."""

    table = str('CREATE TABLE IF NOT EXISTS profiles ('
                'ID        INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,'
                'Guid      TEXT    NOT NULL UNIQUE,'
                'SortOrder INTEGER NOT NULL);')
    cur.execute(table)

    table = str('CREATE TABLE IF NOT EXISTS shared_app_config ('
                'ID    INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
                'Name  TEXT    NOT NULL UNIQUE,'
                'Value TEXT);')
    cur.execute(table)

    table = str('CREATE TABLE IF NOT EXISTS stream_continuity ('
                'ProfileGuid      TEXT    NOT NULL,'
                'VideoID          INTEGER NOT NULL,'
                'Value            TEXT,'
                'DateLastModified TEXT    NOT NULL,'
                'PRIMARY KEY (ProfileGuid, VideoID ),'
                'FOREIGN KEY (ProfileGuid)'
                'REFERENCES Profiles (Guid) ON DELETE CASCADE ON UPDATE CASCADE);')
    cur.execute(table)

    table = str('CREATE TABLE IF NOT EXISTS video_lib_episodes ('
                'EpisodeID INTEGER,'
                'SeasonID  INTEGER,'
                'FilePath  TEXT,'
                'PRIMARY KEY (EpisodeID, SeasonID));')
    cur.execute(table)

    table = str('CREATE TABLE IF NOT EXISTS video_lib_movies ('
                'MovieID   INTEGER PRIMARY KEY NOT NULL,'
                'FilePath  TEXT    NOT NULL,'
                'NfoExport TEXT    NOT NULL DEFAULT (\'False\'));')
    cur.execute(table)

    table = str('CREATE TABLE IF NOT EXISTS video_lib_seasons ('
                'TvShowID INTEGER NOT NULL,'
                'SeasonID INTEGER NOT NULL,'
                'PRIMARY KEY (TvShowID, SeasonID));')
    cur.execute(table)

    table = str('CREATE TABLE IF NOT EXISTS video_lib_tvshows ('
                'TvShowID      INTEGER PRIMARY KEY NOT NULL,'
                'ExcludeUpdate TEXT    NOT NULL DEFAULT (\'False\'),'
                'NfoExport     TEXT    NOT NULL DEFAULT (\'False\'));')
    cur.execute(table)

    table = str('CREATE TABLE IF NOT EXISTS watched_status_override ('
                'ProfileGuid      TEXT    NOT NULL,'
                'VideoID          INTEGER NOT NULL,'
                'Value            TEXT,'
                'PRIMARY KEY (ProfileGuid, VideoID ),'
                'FOREIGN KEY (ProfileGuid)'
                'REFERENCES Profiles (Guid) ON DELETE CASCADE ON UPDATE CASCADE);')
    cur.execute(table)

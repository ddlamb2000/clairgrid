'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the Grid Manager for the clairgrid Grid Service.
'''

from ..base_manager import BaseManager

class GridManager(BaseManager):
    """
    Manages grid-related requests.
    """
    def __init__(self, db_manager):
        BaseManager.__init__(self, db_manager)
        self.allGrids = {} # dictionary of grids by uuid
        self.allRows = {} # dictionary of rows by gridUuid and rowUuid

    from ._load_grid import _load_grid
    from ._load_columns import _load_columns
    from ._load_rows import _load_rows
    from .handle_load import handle_load
    from .handle_change import handle_change
    from ._get_grid_column_row import _get_grid_column_row
    from ._add_row import _add_row
    from ._update_row import _update_row
    from ._add_relationship import _add_relationship
    from ._remove_relationship import _remove_relationship
    from .handle_locate import handle_locate
    from .handle_prompt import handle_prompt

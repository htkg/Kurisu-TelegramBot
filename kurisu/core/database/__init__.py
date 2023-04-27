from kurisu.core.database.schema import initialize_tables, prune_db
from kurisu.core.plugins_manager import initalize_plugins

prune_db()
initialize_tables()
initalize_plugins()
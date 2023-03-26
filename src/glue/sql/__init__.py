"""
package containing .sql files with a helper function in __init__ for locating those
files at runtime
"""
import os
from typing import Dict, List

_sql_dir: str = os.path.dirname(__file__)

"""
query_files is a list of full paths of .sql files in the sql directory
"""
query_files: List[str] = [
    os.path.abspath(os.path.join(_sql_dir, filename))
    for filename in os.listdir(_sql_dir)
    if filename.endswith(".sql")
]

"""
queries maps basename:path for the .sql files in the sql directory
for example:
  {"basic_security_users": "some/full/path/glue/sql/basic_security_users.sql"}
"""
queries: Dict[str, str] = {
    os.path.splitext(os.path.basename(filepath))[0]: filepath
    for filepath in query_files
}

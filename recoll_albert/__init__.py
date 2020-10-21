"""Recoll."""
import os
from sys import platform
import traceback
from pathlib import Path
from collections import Counter

# TODO: Check if this fails and return a more comprehensive error message for the user
from recoll import recoll

import albertv0 as v0

__iid__ = "PythonInterface/v0.2"
__prettyname__ = "Recoll"
__version__ = "0.1.0"
# __trigger__ = "rc " # Use this if you want it to be only triggered by rc <query>
__author__ = "Gerard Simons"
__dependencies__ = []
__homepage__ = "https://github.com/gerardsimons/recoll-albert/blob/master/recoll/recoll"

icon_path = str(Path(__file__).parent / "recoll")
cache_path = Path(v0.cacheLocation()) / "recoll"
config_path = Path(v0.configLocation()) / "recoll"
data_path = Path(v0.dataLocation()) / "recoll"
dev_mode = True

# If set to to true it removes duplicate documents hits that share the same URL, such as epubs or other archives.
# Note that this means the number of results returned may be different from the actual recoll results
remove_duplicates = True

# String definitions
OPEN_WITH_DEFAULT_APP = "Open with default application"
REVEAL_IN_FILE_BROWSER = "Reveal in file browser"
OPEN_TERMINAL_AT_THIS_PATH = "Open terminal at this path"
COPY_FILE_CLIPBOARD = "Copy file to clipboard"
COPY_PATH_CLIPBOARD = "Copy path to clipboard"

# plugin main functions -----------------------------------------------------------------------

def initialize():
    """Called when the extension is loaded (ticked in the settings) - blocking."""

    # create plugin locations
    for p in (cache_path, config_path, data_path):
        p.mkdir(parents=False, exist_ok=True)

def query_recoll(query_str, max_results=10, max_chars=80, context_words=4, verbose=False):
    """
    Query recoll index for simple query string and return the filenames in order of relevancy
    :param query_str:
    :param max_results:
    :return:
    """
    if not query_str:
        return []

    db = recoll.connect()
    db.setAbstractParams(maxchars=max_chars, contextwords=context_words)
    query = db.query()
    nres = query.execute(query_str)
    docs = []
    if nres > max_results:
        nres = max_results
    for i in range(nres):
        doc = query.fetchone() # TODO: JUst use fetchall and return the lot?!
        docs.append(doc)

    return docs


def path_from_url(url: str) -> str:
    if not url.startswith('file://'):
        return None
    else:
        return url.replace("file://", "")


def get_open_dir_action(dir: str):
    if platform == "linux" or platform == "linux2":
        return v0.ProcAction(text=REVEAL_IN_FILE_BROWSER, commandline=["xdg-open", dir])
    elif platform == "darwin":
        return v0.ProcAction(text=REVEAL_IN_FILE_BROWSER, commandline=["open", dir])
    elif platform == "win32": # From https://stackoverflow.com/a/2878744/916382
        return v0.FuncAction(text=REVEAL_IN_FILE_BROWSER, callable=lambda : os.startfile(dir))


def doc_to_icon_path(doc) -> str:
    """ Attempts to convert a mime type to a text string that is accepted by """
    mime_str = getattr(doc, "mtype", None)
    if not mime_str:
        return v0.iconLookup("unknown")
    mime_str = mime_str.replace("/", "-")
    icon_path = v0.iconLookup(mime_str)
    if not icon_path:
        icon_path = v0.iconLookup("unknown")
    return icon_path


def remove_duplicate_docs(docs: list):
    """
    Removes Recoll docs that have the same URL but actually refer to different files, for example an epub file
    which contains HTML files will have multiple docs for each but they all refer to the same epub file.
    :param docs: the original list of documents
    :return: the same docs param but with the docs removed that share the same URL attribute
    """
    urls = [x.url for x in docs]
    url_count = Counter(urls)

    duplicates = [k for k in url_count.keys() if url_count[k] > 1]
    # Merge duplicate results, this might happen becase it actually consists of more than 1 file, like an epub
    # We adopt the relevancy rating of the max one
    for dup in duplicates:
        # Just take the one with the highest relevancy
        best_doc = None
        best_rating = -1
        for doc in [x for x in docs if x.url == dup]:
            rating = float(doc.relevancyrating.replace("%", ""))
            if rating > best_rating:
                best_doc = doc
                best_rating = rating

        docs = [x for x in docs if x.url != dup]
        docs.append(best_doc)
    return docs

def recoll_docs_as_items(docs: list):
    """Return an item - ready to be appended to the items list and be rendered by Albert."""

    items = []

    # First we find duplicates if so configured
    if remove_duplicates:
        docs = remove_duplicate_docs(docs)

    for doc in docs:
        path = path_from_url(doc.url) # The path is not always given as an attribute by recoll doc
        dir = os.path.dirname(path)
        dir_open = get_open_dir_action(dir)

        if path:
            actions = [v0.UrlAction(OPEN_WITH_DEFAULT_APP, doc.url)]
            if dir_open:
                actions.append(dir_open)

            actions.extend([
                # NOTE: Termaction requires a commandline arg, if you pass it empty list nothing happens, so we give it empty string
                v0.TermAction(text=OPEN_TERMINAL_AT_THIS_PATH, commandline=[""],
                          behavior=v0.TermAction.CloseBehavior.DoNotClose, cwd=dir),
                # IMPORTANT: FIXME: it should be only read when the user clicks it I feel. A lot of IO could happen just to create these actions
                v0.ClipAction(COPY_FILE_CLIPBOARD, open(path, 'rb').read()),
                v0.ClipAction(COPY_PATH_CLIPBOARD, path)])

            # Add the item
            items.append(v0.Item(
                id=__prettyname__,
                icon=doc_to_icon_path(doc),
                text=doc.filename,
                subtext=dir,
                completion="",
                actions=actions
            ))
    return items


def handleQuery(query) -> list:
    """Hook that is called by albert with *every new keypress*."""  # noqa
    results = []

    try:
        if __trigger__  and not query.isTriggered:
            return []
        # be backwards compatible with v0.2
        if "disableSort" in dir(query):
            query.disableSort()

        results_setup = setup(query)
        if results_setup:
            return results_setup

        docs = query_recoll(query.string)
        results = recoll_docs_as_items(docs)
    except Exception:  # user to report error
        if dev_mode:  # let exceptions fly!
            print(traceback.format_exc())
            raise

        results.insert(
            0,
            v0.Item(
                id=__prettyname__,
                icon=icon_path,
                text="Something went wrong! Press [ENTER] to copy error and report it",
                actions=[
                    v0.ClipAction(
                        f"Copy error - report it to {__homepage__[8:]}",
                        f"{traceback.format_exc()}",
                    )
                ],
            ),
        )

    return results


# supplementary functions ---------------------------------------------------------------------
def save_data(data: str, data_name: str):
    """Save a piece of data in the configuration directory."""
    with open(config_path / data_name, "w") as f:
        f.write(data)


def load_data(data_name) -> str:
    """Load a piece of data from the configuration directory."""
    with open(config_path / data_name, "r") as f:
        data = f.readline().strip().split()[0]

    return data


def setup(query):
    """Setup is successful if an empty list is returned.

    Use this function if you need the user to provide you data
    """

    results = []
    return results

# In case the __trigger__ was not set at all we set it to the empty string
try:
    __trigger__
except NameError:
    __trigger__ = ""
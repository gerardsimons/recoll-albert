"""Recoll."""


import sys
import traceback
from pathlib import Path

# TODO: Check if this fails and return a more comprehensive error message for the user
from recoll import recoll

with open('/home/gerard/Desktop/ALBERT_RECALL_EVIDENCE', 'w') as fp:
    fp.write("Hello, There")

import albertv0 as v0

__iid__ = "PythonInterface/v0.2"
__prettyname__ = "Recoll"
__version__ = "0.1.0"
__trigger__ = "rc "
__author__ = "Gerard Simons"
__dependencies__ = []
__homepage__ = "https://github.com/gerardsimons/recoll-albert/blob/master/recoll/recoll"

icon_path = str(Path(__file__).parent / "recoll")

cache_path = Path(v0.cacheLocation()) / "recoll"
config_path = Path(v0.configLocation()) / "recoll"
data_path = Path(v0.dataLocation()) / "recoll"
dev_mode = True

# plugin main functions -----------------------------------------------------------------------


def initialize():
    """Called when the extension is loaded (ticked in the settings) - blocking."""

    # create plugin locations
    for p in (cache_path, config_path, data_path):
        p.mkdir(parents=False, exist_ok=True)


def finalize():
    pass


def query_recoll(query_str, max_results=10, max_chars=80, context_words=4):
    """
    Query recoll index for simple query string and return the filenames in order of relevancy
    :param query_str:
    :param max_results:
    :return:
    """
    if not query_str:
        print("Empty query string, terminating.")
        return []
    db = recoll.connect()
    db.setAbstractParams(maxchars=max_chars, contextwords=context_words)
    query = db.query()
    print("query_str=", query_str)
    nres = query.execute(query_str)
    # names = list(map(lambda x: x[0], nres.description))
    # print(names)
    docs = []
    # print("Result count: ", nres)
    if nres > max_results:
        nres = max_results
    for i in range(nres):
        doc = query.fetchone() # TODO: JUst use fetchall and return the lot?!
        docs.append(doc)

    return docs


def recoll_docs_as_items(docs):
    """Return an item - ready to be appended to the items list and be rendered by Albert."""

    items = []

    for doc in docs:
        # try:
        items.append(v0.Item(
            id=__prettyname__,
            icon=icon_path,
            text=doc.filename,
            subtext=doc.url,
            completion="",
            actions=[
                v0.UrlAction("Open in whatever URL handler", doc.url),
                # v0.UrlAction("Open in xkcd.com", "https://www.xkcd.com/"),
                v0.ClipAction("Copy URL", f"https://www.xkcd.com/"),
            ],
        ))
    return items


def handleQuery(query) -> list:
    """Hook that is called by albert with *every new keypress*."""  # noqa
    results = []
    print("Query:", query.string)

    # if query.isTriggered:
    try:
        # be backwards compatible with v0.2
        if "disableSort" in dir(query):
            query.disableSort()

        results_setup = setup(query)
        if results_setup:
            return results_setup

        # modify this...
        docs = query_recoll(query.string)
        # print(f"Recoll query {query.string} returned {len(docs)} results: ", ",".join([str(x.rcludi) for x in docs]))
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
def notify(
     msg: str, app_name: str=__prettyname__, image=str(icon_path),
):
    Notify.init(app_name)
    n = Notify.Notification.new(app_name, msg, image)
    n.show()



def sanitize_string(s: str) -> str:
    return s.replace("<", "&lt;")



def get_as_subtext_field(field, field_title=None) -> str:
    """Get a certain variable as part of the subtext, along with a title for that variable."""
    s = ""
    if field:
        s = f"{field} | "
    else:
        return ""

    if field_title:
        s = f"{field_title}: " + s

    return s


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

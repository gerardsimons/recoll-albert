from recoll import recoll
import sys

def query_recoll(query_str, max_results=5):

    db = recoll.connect()
    db.setAbstractParams(maxchars=80, contextwords=4)
    query = db.query()
    print("query_str=", query_str)
    nres = query.execute(query_str)
    # names = list(map(lambda x: x[0], nres.description))
    # print(names)
    print("Result count: ", nres)
    if nres > max_results:
        nres = max_results
    for i in range(nres):
        doc = query.fetchone()
        print("Result #%d" % (query.rownumber,))
        print(dir(doc))
        print(doc.keys())
        print()
        for k in doc.keys():
            print("Doc", k, "=>", getattr(doc, k))
        print()
        for k in ("title", "size"):
            print(k, ":", getattr(doc, k).encode('utf-8'))
        abs = db.makeDocAbstract(doc, query).encode('utf-8')
        print("-"*30)
        # print(abs)
        # print()

def query_recoll_filenames(query_str, max_results=10, max_chars=80, context_words=4):
    """
    Query recoll index for simple query string and return the filenames in order of relevancy
    :param query_str:
    :param max_results:
    :return:
    """
    db = recoll.connect()
    db.setAbstractParams(maxchars=max_chars, contextwords=context_words)
    query = db.query()
    # print("query_str=", query_str)
    nres = query.execute(query_str)
    # names = list(map(lambda x: x[0], nres.description))
    # print(names)
    docs = []
    # print("Result count: ", nres)
    if nres > max_results:
        nres = max_results
    for i in range(nres):
        doc = query.fetchone()
        docs.append(doc)

    docs = sorted(docs, key=lambda x : x['relevancyrating'])
    doc_udi = [x['rcludi'] for x in docs]

        # print("Result #%d" % (query.rownumber,))
        # print(dir(doc))
        # print(doc.keys())
        # print()
        # for k in doc.keys():
        #     print("Doc", k, "=>", getattr(doc, k))
        # print()
        # for k in ("title", "size"):
        #     print(k, ":", getattr(doc, k).encode('utf-8'))
        # abs = db.makeDocAbstract(doc, query).encode('utf-8')
        # print("-"*30)
        # print(abs)
        # print()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Exactly 1 argument expected.")
        sys.exit(1)

    query_recoll(sys.argv[1])
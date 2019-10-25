import os
import sys
from pathlib import Path

from captions import Documents, Lexicon, CaptionIndex
from app.models import Video

def build_index(index_dir):
    doc_path = os.path.join(index_dir, 'docs.list')
    lex_path = os.path.join(index_dir, 'words.lex')
    idx_path = os.path.join(index_dir, 'index.bin')
    documents = Documents.load(doc_path)
    lexicon = Lexicon.load(lex_path)
    index = CaptionIndex(idx_path, lexicon, documents)
    return documents, lexicon, index

DOCUMENTS, LEXICON, INDEX = build_index('/app/data/index10a-new-tokenizer')

def _get_video_name(p):
    """Only the filename without exts"""
    return Path(p).name.split('.')[0]

# THIS INIT IS BORKED PLEASE FIX
def _init_doc_id_to_vid_id():
    video_name_to_id = {_get_video_name(v.path) : v.id for v in Video.objects.all()}
    doc_id_to_vid_id = {}
    num_docs_with_no_videos = 0
    for d in DOCUMENTS:
        video_name = _get_video_name(d.name)
        video_id = video_name_to_id.get(video_name, None)
        if video_id is not None:
            doc_id_to_vid_id[d.id] = video_id
        else:
            num_docs_with_no_videos += 1
    print('Matched {} documents to videos'.format(len(doc_id_to_vid_id)), file=sys.stderr)
    print('{} documents have no videos'.format(num_docs_with_no_videos), file=sys.stderr)
    print('{} videos have no documents'.format(len(video_name_to_id) - len(doc_id_to_vid_id)),
          file=sys.stderr)
    return doc_id_to_vid_id

DOCUMENT_ID_TO_VIDEO_ID = _init_doc_id_to_vid_id()
VIDEO_ID_TO_DOCUMENT_ID = {v: k for k, v in DOCUMENT_ID_TO_VIDEO_ID.items()}


def get_document(video_id: int):
    doc_id = VIDEO_ID_TO_DOCUMENT_ID[video_id]
    return DOCUMENTS[doc_id]


def convert_doc_ids_to_video_ids(results):
    def wrapper(document_results):
        for d in document_results:
            video_id = DOCUMENT_ID_TO_VIDEO_ID.get(d.id, None)
            if video_id is not None:
                yield d._replace(id=video_id)
    return wrapper(results)


def convert_video_ids_to_doc_ids(vid_ids, verbose=False):
    if vid_ids is None:
        return None
    else:
        doc_ids = []
        for v in vid_ids:
            d = VIDEO_ID_TO_DOCUMENT_ID.get(v, None)
            if d is not None:
                doc_ids.append(d)
            elif verbose:
                print('Document not found for video id={}T'.format(v))
        assert len(doc_ids) > 0
        return doc_ids


def text_search(text, video_ids=None):
    documents = convert_video_ids_to_doc_ids(video_ids)
    return convert_doc_ids_to_video_ids(
        INDEX.search(text, documents=documents))


def query_search(query_str, video_ids=None):
    documents = convert_video_ids_to_doc_ids(video_ids)
    query = caption_query.Query(query_str)
    return convert_doc_ids_to_video_ids(
        query.execute(LEXICON, INDEX, documents=documents))



def get_rekall(video_ids):
    from rekall import Interval, IntervalSet, IntervalSetMapping, Bounds3D

    return IntervalSetMapping({
        video_id: IntervalSet([
            Interval(
                Bounds3D(p.start, p.end),
                payload=' '.join([LEXICON.decode(t, 'UNKNOWN') for t in INDEX.tokens(
                VIDEO_ID_TO_DOCUMENT_ID[video_id], p.idx, p.len)])
            )
            for p in INDEX.intervals(VIDEO_ID_TO_DOCUMENT_ID[video_id])
        ])
        for video_id in video_ids if video_id in VIDEO_ID_TO_DOCUMENT_ID
    })

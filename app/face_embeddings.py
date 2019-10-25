import os
import numpy as np
from rs_embed import EmbeddingData

EMB_DIR = '/app/data/face_embs10'
EMB_PATH = os.path.join(EMB_DIR, 'face_embs.bin')
ID_PATH = os.path.join(EMB_DIR, 'face_ids.bin')
EMB_DIM = 128


_EMB_DATA = EmbeddingData(ID_PATH, EMB_PATH, EMB_DIM)


def count():
    return _EMB_DATA.count()

  
def ids(i, n):
    """Get n face ids starting at index i"""
    return _EMB_DATA.ids(i, n)


def get(ids):
    """List of face ids -> List of pairs (id, embedding)"""
    return _EMB_DATA.get(ids)


def mean(ids):
    """List of face ids -> mean embedding"""
    return _EMB_DATA.mean(ids)


def features(ids):
    """List of face ids -> List of embeddings"""
    result = _EMB_DATA.get(ids)
    assert len(result) == len(ids)
    return [np.array(v) for _, v in result]


def sample(k):
    """Returns list of face_ids, uniformly random with replacement"""
    return _EMB_DATA.sample(k)


def exists(ids):
    """List of face ids -> List of bools"""
    return _EMB_DATA.exists(ids)


def dist(ids, targets=None, target_ids=None):
    """
    Computes the distance from each face in ids to the closest target
    
    Args:
        ids: List of faces to compute distances for
        targets: List of embeddings
        target_ids: List of face_ids
    
    Returns:
        List of distances in same order as as ids
    """
    if targets is not None:
        targets = [
            [float(z) for z in x.tolist()] 
            if not isinstance(x, list) else x for x in targets
        ]
        return _EMB_DATA.dist(targets, ids)
    elif target_ids is not None:
        return _EMB_DATA.dist_by_id(target_ids, ids)
    else:
        raise ValueError('No targets given')


def knn(targets=None, ids=None, k=2 ** 31, max_threshold=100., **kwargs):
    """
    Computes distance of all faces to the targets 
    (specified by targets or ids)
    
    Args:
        targets: List of embeddings (i.e., list of floats)
        ids: List of face ids (another way to specify targets
        max_threshold: largest distance
        
    Returns:
        List of (face_id, distance) pairs by asending distance
    """
    if targets is not None:
        targets = [
            [float(z) for z in x.tolist()] 
            if not isinstance(x, list) else x for x in targets
        ]
        return _EMB_DATA.nn(targets, k, max_threshold, **kwargs)
    elif ids is not None:
        return _EMB_DATA.nn_by_id(ids, k, max_threshold, **kwargs)
    else:
        raise ValueError('No targets given')


def kmeans(ids, k=25):
    """
    Run kmeans on all face_ids in ids.
    
    Args:
        ids: List of face_ids
    
    Returns:
        List of (face_id, cluster number) pairs
    """
    return _EMB_DATA.kmeans(ids, k)


def logreg(ids, labels, **kwargs):
    """
    Args:
        ids: List of face_ids
        labels: List of 0, 1 labels
    Returns:
        weights
    """
    return _EMB_DATA.logreg(
        ids, labels, **kwargs)


def logreg_predict(weights, **kwargs):
    """Returns: List of (face_id, score) pairs by ascending score)"""
    return _EMB_DATA.logreg_predict(weights, **kwargs)


def knn_predict(train_ids, train_labels, k, **kwargs):
    """Returns: List of (face_id, score) pairs by ascending score)"""
    return _EMB_DATA.knn_predict(train_ids, train_labels, k, **kwargs)
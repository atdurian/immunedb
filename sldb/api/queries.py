import datetime
import json
import math
from sqlalchemy import desc, inspect
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import DeclarativeMeta

import sldb.util.lookups as lookups
from sldb.common.models import *
from sldb.common.mutations import MutationType, Mutations


def _clone_to_dict(clone):
    return {
        'id': clone.id,
        'subject': {
            'study': {
                'id': clone.subject.study.id,
                'name': clone.subject.study.name
            },
            'identifier': clone.subject.identifier,
        },
        'v_gene': clone.v_gene,
        'j_gene': clone.j_gene,
        'cdr3_aa': clone.cdr3_aa,
        'cdr3_nt': clone.cdr3_nt,
        'cdr3_num_nts': clone.cdr3_num_nts,
        'germline': clone.germline
    }

def _model_to_dict(inst):
    ret = {}
    for c in inspect(inst).attrs:
        if isinstance(c.value, (str, long, int, bool, type(None))):
            ret[c.key] = c.value
        if isinstance(c.value, datetime.date):
            ret[c.key] = c.value.strftime('%Y-%m-%d')
    return ret


def get_all_clones(session, paging=None):
    """Gets a list of all clones"""
    res = []
    clone_q = session.query(Clone).order_by(Clone.v_gene, Clone.j_gene,
                                            Clone.cdr3_aa, Clone.subject_id)

    if paging is not None:
        page, per_page = paging
        clone_q = clone_q.offset((page - 1) * per_page).limit(per_page)

    for c in clone_q:
        stats_comb = []
        for stat in session.query(CloneFrequency)\
                           .filter(CloneFrequency.clone_id == c.id,
                                   CloneFrequency.filter_type == 'clones_all')\
                           .order_by(desc(CloneFrequency.total_sequences)):
                stats_comb.append({
                    'sample': {
                        'id': stat.sample.id,
                        'name': stat.sample.name
                    },
                    'unique_sequences': stat.unique_sequences,
                    'total_sequences': stat.total_sequences
                })

        clone_json = _clone_to_dict(c)
        clone_json['stats'] = stats_comb
        res.append(clone_json)

    return res


def compare_clones(session, uids):
    """Compares sequences within clones by determining their mutations"""
    clones = {}
    for clone_id, sample_id in uids:
        clone = session.query(Clone).filter(Clone.id == clone_id).first()
        germline = clone.germline[:309] + clone.cdr3_nt + \
            clone.germline[309 + clone.cdr3_num_nts:]
        mutations = Mutations(germline, clone.cdr3_num_nts)
        if clone_id not in clones:
            clone_json = _clone_to_dict(clone)
            clone_json['germline'] = germline
            clones[clone_id] = {
                'clone': clone_json,
                'mutation_stats': {},
                'seqs': []
            }

        for s in session.query(Sequence)\
                        .filter(Sequence.sample_id == sample_id,
                                Sequence.clone_id == clone_id):
            clones[clone_id]['seqs'].append({
                'seq_id': s.seq_id,
                'sample': {
                    'id': s.sample.id,
                    'name': s.sample.name
                },
                'junction_nt': s.junction_nt,
                'sequence': s.sequence,
                'mutations': mutations.add_sequence(s.sequence),
            })

        region_stats, pos_stats = mutations.get_aggregate()
        clones[clone_id]['mutation_stats']['regions'] = region_stats
        clones[clone_id]['mutation_stats']['positions'] = pos_stats

    return clones


def get_clone_overlap(session, filter_type, samples, paging=None):
    """Gets a list of clones and the samples in `samples` which they appear"""
    res = []
    q = session.query(
        CloneFrequency,
        func.sum(CloneFrequency.unique_sequences).label('unique_sequences'),
        func.sum(CloneFrequency.total_sequences).label('total_sequences'),
        func.group_concat(CloneFrequency.sample_id)
        .label('samples'))\
        .filter(CloneFrequency.sample_id.in_(samples),
                CloneFrequency.filter_type == filter_type)\
        .group_by(CloneFrequency.clone_id)\
        .order_by(desc(func.sum(CloneFrequency.total_sequences)))

    if paging is not None:
        page, per_page = paging
        q = q.offset((page - 1) * per_page).limit(per_page)
        num_pages = math.ceil(len(q.all()) / per_page)

    for r in q:
        samples = ','.join(map(str, sorted(map(int, r.samples.split(',')))))
        freq = r.CloneFrequency
        res.append({
            'samples': samples,
            'unique_sequences': int(r.unique_sequences),
            'total_sequences': int(r.total_sequences),
            'clone': _clone_to_dict(freq.clone)
        })

    if paging:
        return res, num_pages
    return res


def get_v_usage(session, filter_type, samples):
    """Gets the V-Gene usage percentages for samples"""
    data = {}
    headers = []
    for s in session.query(SampleStats)\
            .filter(SampleStats.filter_type == filter_type,
                    SampleStats.sample_id.in_(samples)):
        dist = json.loads(s.v_call_dist)
        data[s.sample.name] = {}
        total = 0
        for v in dist:
            total += v[1]

        for v in dist:
            name, occ = v
            if name in lookups.v_gene_ties:
                name = lookups.v_gene_ties[name]
            else:
                name = name.replace('/', '|').split('|')[0]
            if name not in headers:
                headers.append(name)

            data[s.sample.name][name] = round(100 * occ / float(total), 2)

    return data, headers

def get_sequence(session, sample_id, seq_id):
    seq = session.query(Sequence).filter(Sequence.sample_id == sample_id,
                                         Sequence.seq_id == seq_id).first()
    
    ret = _model_to_dict(seq)
    ret['subject'] = {
        'study': {
            'id': seq.subject.study.id,
            'name': seq.subject.study.name
        },
        'identifier': seq.subject.identifier,
    }
    ret['sample'] = {
        'id': seq.sample.id,
        'name': seq.sample.name,
    }

    if seq.clone == None:
        ret['clone'] = None
    else:
        ret['clone'] = _clone_to_dict(seq.clone)

    return ret
import re
import distance

from Bio.Seq import Seq
import sldb.identification.anchors as anchors
import sldb.identification.germlines as germlines
import sldb.util.lookups as lookups


class VDJSequence(object):
    CDR3_OFFSET = 309

    def __init__(self, id, seq):
        self._id = id
        self._seq = seq
        self._j = None
        self._j_anchor_pos = None
        self._v = None
        self._v_anchor_pos = None
        self._mutation_frac = None
        self._germline = None
        self._cdr3_len = 0

        self._find_j()
        if self._j is not None:
            self._find_v_position()
            if self.v_anchor_pos is not None:
                self._find_v()

    @property
    def id(self):
        return self._id

    @property
    def j_gene(self):
        return self._j

    @property
    def v_gene(self):
        return self._v

    @v_gene.setter
    def v_gene(self, v):
        self._v = v

    @property
    def j_anchor_pos(self):
        return self._j_anchor_pos

    @property
    def v_anchor_pos(self):
        return self._v_anchor_pos

    @property
    def cdr3(self):
        return self.sequence[self.CDR3_OFFSET:self._cdr3_len]

    @property
    def sequence(self):
        return self._seq

    @property
    def germline(self):
        return self._germline

    @property
    def mutation_fraction(self):
        return self._mutation_frac

    def _find_j(self):
        '''Finds the location and type of J gene'''
        self._compare(False)
        if self._j is None:
            self._compare(True)

    def _compare(self, rev_comp):
        '''Finds an exact J gene anchor match at the amino acid level'''
        if rev_comp:
            seq = self._seq.reverse_complement()
        else:
            seq = self._seq

        for match, j_gene in anchors.all_j_anchors():
            i = seq.find(match)
            if i >= 0:
                if rev_comp:
                    self._j_anchor_pos = i
                else:
                    self._j_anchor_pos = len(self._seq) - i
                self._j = j_gene
                if rev_comp:
                    self._seq = self._seq.reverse_complement()
                return

    def _find_v_position(self):
        '''Tries to find the end of the V gene region'''
        # Try to find DxxxyzC
        dc = self._find_dc()
        if dc is not None:
            dc_seq = Seq(dc.group(0))
            # Make sure yz in ['YY', 'YC', 'YH']
            if str(dc_seq.translate()[-2:]) in anchors.dc_final_aas:
                self._v_anchor = dc_seq
                self._v_anchor_pos = dc.end() - 2
                return

        # If DxxyzC isn't found, try to find 'YYC', 'YCC', or 'YHC'
        yxc = self._find_yxc()
        if yxc is not None:
            self._v_anchor = Seq(yxc.group(0))
            self._v_anchor_pos = yxc.end() - 2

    def _find_v(self):
        '''Finds the V gene closest to that of the sequence'''
        v_best = []
        v_score = None
        for v, germ in germlines.v.iteritems():
            # Strip the gaps
            germ = Seq(germ.replace('.', ''))
            # Get the last occurrence of 'TGT', the germline anchor
            germ_pos = germ.rfind(anchors.germline_anchor)
            # Align and cut the germline to match the sequence
            v_seq = germ[germ_pos - self.v_anchor_pos + 1:germ_pos + 1]
            s_seq = self.sequence[:self.v_anchor_pos]
            # Determine the distance between the germline and sequence
            dist = distance.hamming(str(v_seq), str(s_seq))
            # Record this germline if it is has the lowest distance
            if v_score is None or dist < v_score:
                v_best = [v]
                v_score = dist
            elif dist == v_score:
                v_best.append(v)

        self._v = v_best
        # TODO: is this padding correct for multiple v_bests
        # Determine pad length of the sequence to
        pad_len = germlines.v[v_best[0]].replace('-', '').rfind(
            anchors.germline_anchor) - self.v_anchor_pos + 1
        self._seq = 'N' * pad_len + self._seq
        # Mutation ratio is the distance divided by the length of overlap
        self._mutation_frac = v_score / float(self.v_anchor_pos)
        self._j_anchor_pos += pad_len
        self._v_anchor_pos += pad_len

        # Get the germline with gaps up to CDR3
        self._germline = germlines.v[sorted(self._v)[0]][:self.CDR3_OFFSET]
        # Add germline gaps to sequence before CDR3 and update anchor positions
        for i, c in enumerate(self._germline):
            if c == '-':
                self._seq = self._seq[:i] + '-' + self._seq[i:]
                self._j_anchor_pos += 1
                self._v_anchor_pos += 1
        # Find the J anchor in the germline J gene
        j_anchor_in_germline = germlines.j[self.j_gene].rfind(
            str(anchors.j_anchors[self.j_gene]))
        # Calculate the length of the CDR3
        self._cdr3_len = self.j_anchor_pos - self.CDR3_OFFSET - \
            j_anchor_in_germline
        # Fill germline CDR3 with gaps
        self._germline += '-' * self._cdr3_len
        self._germline += germlines.j[self.j_gene]
        self._seq = self._seq[:len(self._germline)]

    def _find_dc(self):
        '''Finds the first occurrence of the amino-acid sequence DxxxxxC'''
        for d in lookups.aa_to_all_nts('D'):
            for c in lookups.aa_to_all_nts('C'):
                find = re.search(d + '([ATCG]{15})' + c, str(self.sequence))
                if find is not None:
                    return find
        return None

    def _find_yxc(self):
        for aas in ['YYC', 'YCC', 'YHC']:
            for nts in lookups.aa_to_all_nts(aas):
                find = re.search(nts, str(self.sequence))
                if find is not None:
                    return find
        return None

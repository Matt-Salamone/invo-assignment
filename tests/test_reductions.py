import json
from tests.support import WorkspaceTestCase


class ReductionTests(WorkspaceTestCase):
    def test_summary_requires_retained_evidence_and_usable_source(self):
        self.run_cli(self.root / 'assignment', 'init')
        source = self.root / 'lecture.txt'
        source.write_text('Synthetic source definition', encoding='utf-8')
        state = self.operation('intake-save', {'deliverables': ['Example'], 'constraints': [], 'grading_criteria': [], 'uncertainties': [], 'assumptions': [], 'sources': [{'id': 'lecture', 'kind': 'course', 'status': 'conversion-needed', 'reference': 'Lecture', 'path': str(source)}]})
        payload = {'id': 'summary', 'source': state['intake']['sources'][0]['original'], 'source_id': 'lecture', 'source_reference': 'Lecture', 'mode': 'summary', 'pages': [1], 'assessment': {'basis': 'One page', 'relevance': 'Definition', 'uncertainty': 'Unknown limits'}, 'content': 'definition', 'method': 'Planner summarized page 1', 'critical_details': [{'detail': 'Definition', 'evidence': 'definition'}], 'omissions': [], 'limitations': []}
        self.operation('reduction-save', payload, ok=False)
        # A usable independently prepared text context may be summarized routinely.
        usable = self.root / 'assignment/materials/usable.txt'
        usable.write_text('Synthetic source definition', encoding='utf-8')
        payload['source'] = 'materials/usable.txt'
        payload['critical_details'][0]['evidence'] = 'missing definition'
        self.operation('reduction-save', payload, ok=False)
        payload['critical_details'][0]['evidence'] = 'definition'
        state = self.operation('reduction-save', payload)
        self.assertEqual(state['reductions']['summary']['method'], 'Planner summarized page 1')

    def test_selected_pages_keep_critical_content_and_snapshot_provenance(self):
        self.prepare_plan()
        source = self.root / 'assignment/materials/originals/lecture.txt'
        source.parent.mkdir(parents=True, exist_ok=True)
        original = 'PAGE ONE: denominator defines equal parts\fPAGE TWO: advanced exception\fPAGE THREE: numerator counts parts'
        source.write_text(original, encoding='utf-8')
        payload = {'id': 'fractions', 'source': 'materials/originals/lecture.txt', 'source_id': 'lecture', 'source_reference': 'Synthetic lecture', 'mode': 'text-pages', 'pages': [1, 3], 'assessment': {'basis': 'Three pages, only two needed', 'relevance': 'Equal parts objective', 'uncertainty': 'Unknown chatbot limit'}, 'critical_details': [{'detail': 'Denominator definition', 'evidence': 'denominator defines equal parts'}], 'omissions': ['Page 2 advanced exception relevant to a later lesson'], 'limitations': []}
        state = self.operation('reduction-save', payload)
        reduction = state['reductions']['fractions']
        derivative = self.root / 'assignment' / reduction['path']
        self.assertEqual(derivative.read_text(), 'PAGE ONE: denominator defines equal parts\n\nPAGE THREE: numerator counts parts')
        self.assertEqual(source.read_text(), original)
        packet = self.packet_payload()
        packet['context'] = [{'path': reduction['path'], 'reference': 'Lecture pages 1, 3'}]
        state = self.operation('packet-issue', packet)
        issued = state['packets'][state['active_packet']]
        manifest = json.loads((self.root / 'assignment' / issued['path'] / 'manifest.json').read_text())
        saved = manifest['included'][-1]
        self.assertEqual(saved['derivation']['pages'], [1, 3])
        self.assertIn('advanced exception', saved['derivation']['omissions'][0])
        derivative.write_text('Regenerated later', encoding='utf-8')
        self.assertIn('denominator defines equal parts', (self.root / 'assignment' / issued['path'] / saved['path']).read_text())

import json
from tests.support import WorkspaceTestCase


class IntakeTests(WorkspaceTestCase):
    def test_capture_requirements_and_trace_supplied_original(self):
        target = self.root / 'assignment'
        self.run_cli(target, 'init')
        original = self.root / 'lecture.txt'
        original.write_text('Synthetic lecture: equivalent fractions', encoding='utf-8')
        intake = {'deliverables': ['Worked fractions'], 'constraints': ['Show reasoning'],
                  'grading_criteria': ['Correct arithmetic'], 'uncertainties': [],
                  'assumptions': ['Use exact fractions'],
                  'sources': [{'id': 'lecture', 'kind': 'course', 'path': str(original), 'status': 'usable', 'reference': 'Lecture 1'}]}
        state = self.operation('intake-save', intake)
        saved = state['intake']['sources'][0]
        self.assertEqual((target / saved['original']).read_text(), original.read_text())
        self.assertEqual(self.run_cli(target, 'status')['intake']['deliverables'], ['Worked fractions'])
        self.assertEqual(state['next_action'], 'create-worked-solution')

    def test_conversion_requires_explained_decision_and_keeps_provenance(self):
        self.run_cli(self.root / 'assignment', 'init')
        source = self.root / 'slides.txt'
        source.write_text('Slide 1: halves', encoding='utf-8')
        self.operation('intake-save', {'deliverables': ['Example'], 'constraints': [], 'grading_criteria': [], 'uncertainties': [], 'assumptions': [], 'sources': [{'id': 'slides', 'kind': 'course', 'status': 'conversion-needed', 'reference': 'Slide 1', 'path': str(source)}]})
        proposal = {'id': 'text', 'source_id': 'slides', 'tool': 'manual text transcription', 'output': 'materials/derived/slide.txt', 'fidelity_limits': 'No layout', 'source_reference': 'Slide 1'}
        self.operation('conversion-propose', proposal)
        self.operation('conversion-decide', {'id': 'text', 'decision': 'approved'}, ok=False)
        derivative = self.root / 'derivative.txt'
        derivative.write_text('Halves', encoding='utf-8')
        self.operation('conversion-complete', {'id': 'text', 'artifact': str(derivative)}, ok=False)
        self.operation('conversion-decide', {'id': 'text', 'decision': 'approved', 'decision_record': 'Student: yes, transcribe slide 1 after explanation'})
        state = self.operation('conversion-complete', {'id': 'text', 'artifact': str(derivative)})
        self.assertEqual(state['conversions']['text']['status'], 'complete')
        self.assertEqual((self.root / 'assignment/materials/derived/slide.txt').read_text(), 'Halves')
        self.assertEqual(source.read_text(), 'Slide 1: halves')


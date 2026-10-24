from tests.support import WorkspaceTestCase


class PacketTests(WorkspaceTestCase):
    def test_issue_requires_approval_request_and_one_active_packet(self):
        self.prepare_solution()
        payload = self.packet_payload()
        self.operation('packet-issue', payload, ok=False)
        self.operation('plan-propose', {'scope': 'Explain example', 'pacing': 'Ten minutes', 'lessons': [{'id': 'instructions', 'kind': 'instructions', 'title': 'Understand task', 'objectives': ['Explain required example'], 'prerequisites': [], 'minutes': 10}]})
        self.operation('packet-issue', payload, ok=False)
        self.operation('plan-approve', {'version': 1, 'decision_record': 'Student approved'})
        self.operation('packet-issue', dict(payload, request_record=''), ok=False)
        state = self.operation('packet-issue', payload)
        packet_id = state['active_packet']
        packet = state['packets'][packet_id]
        self.assertEqual(packet['assignment_id'], state['assignment_id'])
        folder = self.root / 'assignment' / packet['path']
        saved = (folder / 'context/0-answer.txt').read_bytes()
        (self.root / 'assignment/solution/answer.txt').write_text('Later working edit', encoding='utf-8')
        self.assertEqual((folder / 'context/0-answer.txt').read_bytes(), saved)
        self.assertTrue((folder / 'tutor.md').exists())
        self.assertTrue((folder / 'report-template.json').exists())
        self.operation('packet-issue', payload, ok=False)
        resumed = self.operation('packet-resume', {'packet_id': packet_id})
        self.assertEqual(resumed['active_packet'], packet_id)
        (self.root / 'assignment/solution/answer.txt').write_bytes(saved)
        replaced = self.operation('packet-replace', dict(payload, packet_id=packet_id, decision_record='Student chooses replacement'))
        self.assertNotEqual(replaced['active_packet'], packet_id)
        self.assertEqual(replaced['packets'][packet_id]['status'], 'replaced')
        self.assertTrue(folder.exists())
        abandoned = self.operation('packet-abandon', {'packet_id': replaced['active_packet'], 'decision_record': 'Student stops lesson'})
        self.assertIsNone(abandoned['active_packet'])
        self.assertEqual(self.run_cli(self.root / 'assignment', 'status')['active_packet'], None)

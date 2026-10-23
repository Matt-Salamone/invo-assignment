"""Traceable text-page selections and planner-authored summaries."""
import hashlib


def save(root, state, payload, safe_path, save_state):
    needed = ('id', 'source', 'source_id', 'source_reference', 'mode', 'pages', 'assessment', 'critical_details', 'omissions', 'limitations')
    if not isinstance(payload, dict) or any(key not in payload for key in needed):
        raise ValueError('Reduction needs source provenance, assessment, critical details and omissions')
    rid = payload['id']
    records = state.setdefault('reductions', {})
    if not isinstance(rid, str) or not rid or not all(c.isalnum() or c in '-_' for c in rid) or rid in records:
        raise ValueError('Reduction requires a unique simple ID')
    for key in ('source', 'source_id', 'source_reference'):
        if not isinstance(payload[key], str) or not payload[key].strip():
            raise ValueError('Source identity and reference are required')
    source = safe_path(root, payload['source'])
    original = source.read_bytes()
    # An original still awaiting intake conversion is not usable packet context.
    sources = state.get('intake', {}).get('sources', [])
    for entry in sources:
        if entry.get('original') == payload['source']:
            if entry['id'] != payload['source_id'] or entry['status'] != 'usable':
                raise ValueError('Reduce usable sources; obtain intake conversion permission first')
    assessment = payload['assessment']
    if not isinstance(assessment, dict) or any(not isinstance(assessment.get(k), str) or not assessment[k].strip() for k in ('basis', 'relevance', 'uncertainty')):
        raise ValueError('Assess actual size, relevance and chatbot-limit uncertainty')
    if any(not isinstance(payload[k], list) or any(not isinstance(x, str) or not x.strip() for x in payload[k]) for k in ('omissions', 'limitations')):
        raise ValueError('Omissions and limitations must be explicit lists of text')
    pages = payload['pages']
    if not isinstance(pages, list) or not pages or any(type(p) is not int or p < 1 for p in pages) or len(set(pages)) != len(pages):
        raise ValueError('Record unique positive source page/slide references')
    if payload['mode'] == 'text-pages':
        try:
            source_pages = original.decode('utf-8').split('\f')
        except UnicodeError:
            raise ValueError('Text-page trimming requires usable UTF-8 text; follow intake conversion first')
        if max(pages) > len(source_pages):
            raise ValueError('Selected page is outside the source')
        content = '\n\n'.join(source_pages[p - 1] for p in pages)
        method = 'Select form-feed-delimited UTF-8 pages in specified order'
    elif payload['mode'] == 'summary':
        content = payload.get('content')
        method = payload.get('method')
        if not isinstance(content, str) or not content.strip() or not isinstance(method, str) or not method.strip():
            raise ValueError('A summary needs planner-authored content and derivation method')
    else:
        raise ValueError('Supported reduction modes: text-pages, summary')
    details = payload['critical_details']
    if not isinstance(details, list) or not details:
        raise ValueError('Verify lesson-critical details against the derivative')
    for detail in details:
        if not isinstance(detail, dict) or not isinstance(detail.get('detail'), str) or not detail['detail'].strip() or not isinstance(detail.get('evidence'), str) or not detail['evidence'].strip() or detail['evidence'] not in content:
            raise ValueError('Each critical detail requires an actual retained evidence passage')
    relative = 'materials/derived/reduction-' + rid + '.txt'
    destination = safe_path(root, relative)
    if destination.exists() or destination == source:
        raise ValueError('Preserve original and existing derivatives; use a new ID')
    encoded = content.encode('utf-8')
    record = dict(payload, path=relative, method=method, source_sha256=hashlib.sha256(original).hexdigest(), sha256=hashlib.sha256(encoded).hexdigest(), bytes=len(encoded))
    record.pop('content', None)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(encoded)
    records[rid] = record
    save_state(root, state)
    return state

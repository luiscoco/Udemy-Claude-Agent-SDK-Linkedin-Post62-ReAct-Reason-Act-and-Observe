"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

async def run(agent, data):
    docs = agent.output / 'docs'
    docs.mkdir()
    for document in data['documents']:
        path = contained_path(docs, document['id'] + '.txt')
        path.write_text(document['text'], encoding='utf8')
    observations = [doc for doc in data['documents'] if 'refund' in doc['text'].lower()]
    agent.event('local_observation', matches=len(observations), source='bundled documents')
    answer = await agent.ask('tool_cycle', 'Search the supplied document folder using tools; cite the matching document. Do not invent observations.',
        {'question': data['question'], 'folder': str(docs)}, 'refunds.txt states a 30-day refund request window.',
        sdk={'tools': ['Read', 'Grep', 'Glob'], 'allowed_tools': ['Read', 'Grep', 'Glob']})
    return {'reference_observations': observations, 'answer': answer, 'iteration_limit': agent.max_turns}

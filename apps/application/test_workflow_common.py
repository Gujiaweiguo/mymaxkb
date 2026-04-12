from typing import Any
from unittest.mock import patch

from django.test import SimpleTestCase

from application.flow.common import Edge, Node, Workflow
from common.exception.app_exception import AppApiException


def _make_node(node_id: str, node_type: str, *, step_name: str = 'Step', node_data: dict[str, Any] | None = None):
    return Node(
        node_id,
        node_type,
        0,
        0,
        {
            'stepName': step_name,
            'node_data': node_data or {},
        },
    )


def _make_edge(edge_id: str, source: str, target: str, **kwargs: Any):
    if 'sourceAnchorId' not in kwargs:
        kwargs['sourceAnchorId'] = None
    return Edge(edge_id, 'default-edge', source, target, **kwargs)


class WorkflowCommonTests(SimpleTestCase):
    def test_get_node_and_start_node_use_node_map(self):
        workflow = Workflow(
            [
                _make_node('start-node', 'start-node', step_name='Start'),
                _make_node('base-node', 'base-node', step_name='Base'),
                _make_node('reply-node', 'reply-node', step_name='Reply'),
            ],
            [
                _make_edge('edge-start-base', 'start-node', 'base-node'),
                _make_edge('edge-base-reply', 'base-node', 'reply-node'),
            ],
        )

        self.assertEqual(set(workflow.node_map.keys()), {'start-node', 'base-node', 'reply-node'})
        base_node = workflow.get_node('base-node')
        start_node = workflow.get_start_node()

        self.assertIsNotNone(base_node)
        self.assertIsNotNone(start_node)
        self.assertEqual(base_node.properties['stepName'], 'Base')
        self.assertEqual(start_node.id, 'start-node')
        self.assertIsNone(workflow.get_node('missing-node'))

    def test_get_up_and_next_nodes_follow_edges(self):
        workflow = Workflow(
            [
                _make_node('start-node', 'start-node', step_name='Start'),
                _make_node('base-node', 'base-node', step_name='Base'),
                _make_node('reply-node', 'reply-node', step_name='Reply'),
            ],
            [
                _make_edge('edge-start-base', 'start-node', 'base-node'),
                _make_edge('edge-base-reply', 'base-node', 'reply-node'),
            ],
        )

        up_edge_nodes = workflow.get_up_edge_nodes('base-node')
        next_edge_nodes = workflow.get_next_edge_nodes('base-node')

        self.assertEqual(len(up_edge_nodes), 1)
        self.assertEqual(up_edge_nodes[0].edge.sourceNodeId, 'start-node')
        self.assertEqual(up_edge_nodes[0].node.id, 'start-node')
        self.assertEqual(len(next_edge_nodes), 1)
        self.assertEqual(next_edge_nodes[0].edge.targetNodeId, 'reply-node')
        self.assertEqual(next_edge_nodes[0].node.id, 'reply-node')
        self.assertEqual([node.id for node in workflow.get_up_nodes('reply-node')], ['base-node'])
        self.assertEqual([node.id for node in workflow.get_next_nodes('start-node')], ['base-node'])
        self.assertEqual(workflow.get_up_nodes('start-node'), [])
        self.assertEqual(workflow.get_next_nodes('reply-node'), [])
        self.assertIsNone(workflow.get_up_edge_nodes('missing-node'))
        self.assertIsNone(workflow.get_next_edge_nodes('missing-node'))

    def test_new_instance_builds_workflow_from_dict(self):
        workflow = Workflow.new_instance(
            {
                'nodes': [
                    {
                        'id': 'start-node',
                        'type': 'start-node',
                        'x': 0,
                        'y': 0,
                        'properties': {'stepName': 'Start', 'node_data': {}},
                    },
                    {
                        'id': 'base-node',
                        'type': 'base-node',
                        'x': 0,
                        'y': 0,
                        'properties': {'stepName': 'Base', 'node_data': {}},
                    },
                    {
                        'id': 'reply-node',
                        'type': 'reply-node',
                        'x': 0,
                        'y': 0,
                        'properties': {'stepName': 'Reply', 'node_data': {}},
                    },
                ],
                'edges': [
                    {
                        'id': 'edge-start-base',
                        'type': 'default-edge',
                        'sourceNodeId': 'start-node',
                        'targetNodeId': 'base-node',
                    },
                    {
                        'id': 'edge-base-reply',
                        'type': 'default-edge',
                        'sourceNodeId': 'base-node',
                        'targetNodeId': 'reply-node',
                    },
                ],
            }
        )

        self.assertEqual([node.id for node in workflow.get_next_nodes('start-node')], ['base-node'])
        self.assertEqual([node.id for node in workflow.get_next_nodes('base-node')], ['reply-node'])

    def test_get_search_node_returns_only_search_dataset_nodes(self):
        workflow = Workflow(
            [
                _make_node('start-node', 'start-node', step_name='Start'),
                _make_node('search-node', 'search-dataset-node', step_name='Search'),
                _make_node('reply-node', 'reply-node', step_name='Reply'),
            ],
            [
                _make_edge('edge-start-search', 'start-node', 'search-node'),
                _make_edge('edge-search-reply', 'search-node', 'reply-node'),
            ],
        )

        self.assertEqual([node.id for node in workflow.get_search_node()], ['search-node'])

    def test_is_valid_start_node_requires_exactly_one_start_node(self):
        workflow_without_start = Workflow(
            [_make_node('base-node', 'base-node', step_name='Base')],
            [],
        )
        workflow_with_duplicate_start = Workflow(
            [
                _make_node('start-node', 'start-node', step_name='Start A'),
                _make_node('start-node', 'start-node', step_name='Start B'),
            ],
            [],
        )

        with self.assertRaisesMessage(AppApiException, 'starting node is required'):
            workflow_without_start.is_valid_start_node()
        with self.assertRaisesMessage(AppApiException, 'only be one starting node'):
            workflow_with_duplicate_start.is_valid_start_node()

    def test_is_valid_base_node_requires_exactly_one_base_node(self):
        workflow_without_base = Workflow(
            [_make_node('start-node', 'start-node', step_name='Start')],
            [],
        )
        workflow_with_duplicate_base = Workflow(
            [
                _make_node('base-node', 'base-node', step_name='Base A'),
                _make_node('base-node', 'base-node', step_name='Base B'),
            ],
            [],
        )

        with self.assertRaisesMessage(AppApiException, 'Basic information node is required'):
            workflow_without_base.is_valid_base_node()
        with self.assertRaisesMessage(AppApiException, 'only be one basic information node'):
            workflow_with_duplicate_base.is_valid_base_node()

    @patch.object(Workflow, 'is_valid_node_params', return_value=None)
    def test_is_valid_node_rejects_non_end_nodes_without_outgoing_edges(self, _mock_is_valid_node_params):
        workflow = Workflow(
            [
                _make_node('start-node', 'start-node', step_name='Start'),
                _make_node('base-node', 'base-node', step_name='Base'),
            ],
            [
                _make_edge('edge-start-base', 'start-node', 'base-node'),
            ],
        )

        base_node = workflow.get_node('base-node')

        self.assertIsNotNone(base_node)
        with self.assertRaisesMessage(AppApiException, 'Base Nodes cannot be considered as end nodes'):
            workflow.is_valid_node(base_node)

    @patch.object(Workflow, 'is_valid_node_params', return_value=None)
    def test_is_valid_work_flow_allows_reply_end_nodes_without_outgoing_edges(self, _mock_is_valid_node_params):
        workflow = Workflow(
            [
                _make_node('start-node', 'start-node', step_name='Start'),
                _make_node('base-node', 'base-node', step_name='Base'),
                _make_node('reply-node', 'reply-node', step_name='Reply'),
            ],
            [
                _make_edge('edge-start-base', 'start-node', 'base-node'),
                _make_edge('edge-base-reply', 'base-node', 'reply-node'),
            ],
        )

        workflow.is_valid_work_flow()

    @patch.object(Workflow, 'is_valid_node_params', return_value=None)
    def test_is_valid_node_requires_condition_branches_to_be_connected(self, _mock_is_valid_node_params):
        workflow = Workflow(
            [
                _make_node('start-node', 'start-node', step_name='Start'),
                _make_node(
                    'condition-node',
                    'condition-node',
                    step_name='Condition',
                    node_data={
                        'branch': [
                            {'id': 'if-branch', 'type': 'IF'},
                            {'id': 'else-branch', 'type': 'ELSE'},
                        ]
                    },
                ),
                _make_node('reply-node', 'reply-node', step_name='Reply'),
            ],
            [
                _make_edge('edge-start-condition', 'start-node', 'condition-node'),
                _make_edge(
                    'edge-condition-if',
                    'condition-node',
                    'reply-node',
                    sourceAnchorId='condition-node_if-branch_right',
                ),
            ],
        )

        condition_node = workflow.get_node('condition-node')

        self.assertIsNotNone(condition_node)
        with self.assertRaisesMessage(AppApiException, 'branch ELSE of the Condition node needs to be connected'):
            workflow.is_valid_node(condition_node)

    @patch.object(Workflow, 'is_valid_node_params', return_value=None)
    def test_is_valid_node_accepts_condition_nodes_when_all_branches_are_connected(self, _mock_is_valid_node_params):
        workflow = Workflow(
            [
                _make_node('start-node', 'start-node', step_name='Start'),
                _make_node(
                    'condition-node',
                    'condition-node',
                    step_name='Condition',
                    node_data={
                        'branch': [
                            {'id': 'if-branch', 'type': 'IF'},
                            {'id': 'else-branch', 'type': 'ELSE'},
                        ]
                    },
                ),
                _make_node('reply-node', 'reply-node', step_name='Reply'),
                _make_node('reply-node-else', 'reply-node', step_name='Reply Else'),
            ],
            [
                _make_edge('edge-start-condition', 'start-node', 'condition-node'),
                _make_edge(
                    'edge-condition-if',
                    'condition-node',
                    'reply-node',
                    sourceAnchorId='condition-node_if-branch_right',
                ),
                _make_edge(
                    'edge-condition-else',
                    'condition-node',
                    'reply-node-else',
                    sourceAnchorId='condition-node_else-branch_right',
                ),
            ],
        )

        condition_node = workflow.get_node('condition-node')

        self.assertIsNotNone(condition_node)
        workflow.is_valid_node(condition_node)

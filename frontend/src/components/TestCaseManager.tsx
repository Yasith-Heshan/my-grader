import React, { useState } from 'react';
import { Card, Button, Table, Space, Tag, Modal, Typography, Empty } from 'antd';
import { PlusOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import { useTestCasesByAssignment, useDeleteTestCase } from '../hooks/useTestCases';
import { SingleCellTestCase } from '../api/testCaseApi';
import TestCaseFunctionForm from './TestCaseFunctionForm';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text, Paragraph } = Typography;

interface TestCaseManagerProps {
    assignmentId: string;
}

const TestCaseManager: React.FC<TestCaseManagerProps> = ({ assignmentId }) => {
    const [formVisible, setFormVisible] = useState(false);
    const [viewModalVisible, setViewModalVisible] = useState(false);
    const [selectedTestCase, setSelectedTestCase] = useState<SingleCellTestCase | null>(null);

    const { data: testcases, isLoading } = useTestCasesByAssignment(assignmentId);
    const deleteMutation = useDeleteTestCase();

    const handleDelete = (testcase: SingleCellTestCase) => {
        Modal.confirm({
            title: 'Delete Test Case',
            content: `Are you sure you want to delete "${testcase.testcase_name}"?`,
            okText: 'Delete',
            okType: 'danger',
            onOk: () => {
                deleteMutation.mutate(testcase._id);
            },
        });
    };

    const handleView = (testcase: SingleCellTestCase) => {
        setSelectedTestCase(testcase);
        setViewModalVisible(true);
    };

    const columns: ColumnsType<SingleCellTestCase> = [
        {
            title: 'Test Case Name',
            dataIndex: 'testcase_name',
            key: 'testcase_name',
            render: (name) => <Text strong>{name}</Text>,
        },
        {
            title: 'Question',
            dataIndex: 'question_number',
            key: 'question_number',
            width: 100,
            sorter: (a, b) => a.question_number - b.question_number,
        },
        {
            title: 'Cell ID',
            dataIndex: 'cell_id',
            key: 'cell_id',
            width: 120,
            render: (cellId) => <Tag color="blue">{cellId}</Tag>,
        },
        {
            title: 'Points',
            dataIndex: 'points',
            key: 'points',
            width: 100,
            render: (points) => <Tag color="green">{points}</Tag>,
        },
        {
            title: 'Timeout',
            dataIndex: 'timeout',
            key: 'timeout',
            width: 100,
            render: (timeout) => `${timeout}s`,
        },
        {
            title: 'Actions',
            key: 'actions',
            width: 150,
            render: (_, record) => (
                <Space>
                    <Button
                        type="text"
                        icon={<EyeOutlined />}
                        onClick={() => handleView(record)}
                        size="small"
                    >
                        View
                    </Button>
                    <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={() => handleDelete(record)}
                        size="small"
                    >
                        Delete
                    </Button>
                </Space>
            ),
        },
    ];

    return (
        <>
            <Card
                title={<Title level={4}>Test Cases</Title>}
                extra={
                    <Button
                        type="primary"
                        icon={<PlusOutlined />}
                        onClick={() => setFormVisible(true)}
                    >
                        Add Test Case
                    </Button>
                }
            >
                {testcases && testcases.length > 0 ? (
                    <Table
                        columns={columns}
                        dataSource={testcases}
                        rowKey="_id"
                        loading={isLoading}
                        pagination={false}
                    />
                ) : (
                    <Empty
                        description="No test cases yet"
                        image={Empty.PRESENTED_IMAGE_SIMPLE}
                    >
                        <Button
                            type="primary"
                            icon={<PlusOutlined />}
                            onClick={() => setFormVisible(true)}
                        >
                            Add First Test Case
                        </Button>
                    </Empty>
                )}
            </Card>

            <TestCaseFunctionForm
                visible={formVisible}
                onClose={() => setFormVisible(false)}
                assignmentId={assignmentId}
            />

            <Modal
                title="Test Case Details"
                open={viewModalVisible}
                onCancel={() => setViewModalVisible(false)}
                width={800}
                footer={[
                    <Button key="close" onClick={() => setViewModalVisible(false)}>
                        Close
                    </Button>,
                ]}
            >
                {selectedTestCase && (
                    <Space direction="vertical" style={{ width: '100%' }} size="large">
                        <div>
                            <Text strong>Name:</Text> {selectedTestCase.testcase_name}
                        </div>
                        <div>
                            <Text strong>Question:</Text> {selectedTestCase.question_number} |
                            <Text strong> Cell:</Text> <Tag color="blue">{selectedTestCase.cell_id}</Tag> |
                            <Text strong> Points:</Text> <Tag color="green">{selectedTestCase.points}</Tag>
                        </div>
                        {selectedTestCase.description && (
                            <div>
                                <Text strong>Description:</Text>
                                <Paragraph>{selectedTestCase.description}</Paragraph>
                            </div>
                        )}
                        <div>
                            <Text strong>Test Function:</Text>
                            <pre style={{
                                background: '#1e1e1e',
                                color: '#d4d4d4',
                                padding: '16px',
                                borderRadius: '4px',
                                overflow: 'auto',
                                maxHeight: '400px',
                            }}>
                                {selectedTestCase.testcase_function}
                            </pre>
                        </div>
                    </Space>
                )}
            </Modal>
        </>
    );
};

export default TestCaseManager;

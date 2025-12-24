import React, { useState } from 'react';
import { Layout, Card, Button, Typography, Space, Tag, Divider, Alert, Spin, Modal, Table } from 'antd';
import { useParams, useNavigate } from 'react-router-dom';
import { CalendarOutlined, SendOutlined, PlayCircleOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { useAssignment } from '../hooks/useAssignments';
import { useCreateSubmission } from '../hooks/useSubmissions';
import CodeEditor from '../components/CodeEditor';
import axiosInstance from '../api/axiosInstance';
import { toast } from 'react-toastify';

const { Content } = Layout;
const { Title, Text } = Typography;

interface TestResult {
  testcase_name: string;
  cell_id: string;
  score: number;
  max_score: number;
  feedback: string;
  passed: boolean;
}

const AssignmentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [code, setCode] = useState<string>('# Write your Python code here\n\n');
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [testing, setTesting] = useState(false);
  const [showResults, setShowResults] = useState(false);

  const { data: assignment, isLoading } = useAssignment(id || '');
  const submitMutation = useCreateSubmission();

  const handleTest = async () => {
    if (!id) return;

    setTesting(true);
    try {
      const response = await axiosInstance.post('/api/student/evaluate-cell', {
        assignment_id: id,
        cell_id: 'cell_1', // Default cell ID
        student_code: code,
      });

      setTestResults(response.data.results || []);
      setShowResults(true);

      const totalScore = response.data.score || 0;
      const maxScore = response.data.max_score || 0;

      if (totalScore === maxScore) {
        toast.success(`Perfect! Score: ${totalScore}/${maxScore}`);
      } else if (totalScore > 0) {
        toast.info(`Score: ${totalScore}/${maxScore}`);
      } else {
        toast.error(`Score: ${totalScore}/${maxScore}`);
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to test code');
    } finally {
      setTesting(false);
    }
  };

  const handleSubmit = () => {
    if (!id) return;

    submitMutation.mutate(
      {
        assignment_id: id,
        code,
      },
      {
        onSuccess: () => {
          navigate('/student');
        },
      }
    );
  };

  if (isLoading) {
    return (
      <Content style={{ padding: '24px' }}>
        <Spin size="large" />
      </Content>
    );
  }

  if (!assignment) {
    return (
      <Content style={{ padding: '24px' }}>
        <Alert message="Assignment not found" type="error" />
      </Content>
    );
  }

  const dueDate = new Date(assignment.due_date);
  const isOverdue = dueDate < new Date();

  return (
    <Content style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      <Button onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>
        ← Back
      </Button>

      <Space direction="vertical" size="large" style={{ width: '100%', display: 'flex' }}>
        <Card>
          <Title level={2}>{assignment.title}</Title>
          <Space>
            <CalendarOutlined />
            <Text type={isOverdue ? 'danger' : 'secondary'}>
              Due: {dueDate.toLocaleString()}
            </Text>
            {isOverdue && <Tag color="red">Overdue</Tag>}
          </Space>
          <Divider />

          <Title level={4}>Description</Title>
          <div style={{
            padding: '16px',
            background: '#f5f5f5',
            borderRadius: '8px',
            marginBottom: '24px',
          }}>
            <ReactMarkdown>{assignment.description}</ReactMarkdown>
          </div>

          <Divider />

          <Title level={4}>Your Code</Title>
          <Alert
            message="Write your Python code below"
            description="Your code will be tested against the test cases. Make sure to follow the requirements carefully."
            type="info"
            style={{ marginBottom: 16 }}
          />

          <CodeEditor
            value={code}
            onChange={(value) => setCode(value || '')}
            height="500px"
          />

          <div style={{ marginTop: 16, display: 'flex', gap: 16, justifyContent: 'flex-end' }}>
            <Button
              size="large"
              icon={<PlayCircleOutlined />}
              onClick={handleTest}
              loading={testing}
            >
              Test Code
            </Button>
            <Button
              type="primary"
              size="large"
              icon={<SendOutlined />}
              onClick={handleSubmit}
              loading={submitMutation.isPending}
            >
              Submit Assignment
            </Button>
          </div>
        </Card>
      </Space>

      <Modal
        title="Test Results"
        open={showResults}
        onCancel={() => setShowResults(false)}
        footer={[
          <Button key="close" onClick={() => setShowResults(false)}>
            Close
          </Button>,
        ]}
        width={800}
      >
        <Table
          dataSource={testResults}
          rowKey="testcase_name"
          pagination={false}
          columns={[
            {
              title: 'Test Case',
              dataIndex: 'testcase_name',
              key: 'testcase_name',
            },
            {
              title: 'Status',
              dataIndex: 'passed',
              key: 'passed',
              render: (passed: boolean) => (
                <Tag color={passed ? 'green' : 'red'}>
                  {passed ? 'Passed' : 'Failed'}
                </Tag>
              ),
            },
            {
              title: 'Score',
              key: 'score',
              render: (_: any, record: TestResult) => `${record.score}/${record.max_score}`,
            },
            {
              title: 'Feedback',
              dataIndex: 'feedback',
              key: 'feedback',
              ellipsis: true,
            },
          ]}
        />
      </Modal>
    </Content>
  );
};

export default AssignmentDetail;

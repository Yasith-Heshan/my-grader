import React, { useState } from 'react';
import { Layout, Card, Button, Typography, Space, Tag, Divider, Alert, Spin } from 'antd';
import { useParams, useNavigate } from 'react-router-dom';
import { CalendarOutlined, SendOutlined, CheckCircleOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { useAssignment } from '../hooks/useAssignments';
import { useCreateSubmission } from '../hooks/useSubmissions';
import CodeEditor from '../components/CodeEditor';

const { Content } = Layout;
const { Title, Text, Paragraph } = Typography;

const AssignmentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [code, setCode] = useState<string>('# Write your Python code here\n\n');

  const { data: assignment, isLoading } = useAssignment(id || '');
  const submitMutation = useCreateSubmission();

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
    <Content style={{ padding: '24px' }}>
      <Button onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>
        ← Back
      </Button>

      <Space direction="vertical" size="large" style={{ width: '100%' }}>
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
            marginBottom: '16px'
          }}>
            <ReactMarkdown>{assignment.description}</ReactMarkdown>
          </div>

          <Title level={4}>Test Cases ({assignment.test_cases.length})</Title>
          <Space direction="vertical" style={{ width: '100%' }}>
            {assignment.test_cases.map((testCase, index) => (
              <Card key={testCase.id} size="small" type="inner">
                <Space>
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                  <Text strong>{testCase.name}</Text>
                  <Tag color="blue">{testCase.points} points</Tag>
                </Space>
              </Card>
            ))}
          </Space>

          <Divider />
          <Text strong>Total Points: {assignment.max_score}</Text>
        </Card>

        <Card title="Your Code">
          <Alert
            message="Write your Python code below"
            description="Your code will be tested against the test cases above. Make sure to follow the requirements carefully."
            type="info"
            style={{ marginBottom: 16 }}
          />

          <CodeEditor
            value={code}
            onChange={(value) => setCode(value || '')}
            height="500px"
          />

          <div style={{ marginTop: 16, textAlign: 'right' }}>
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
    </Content>
  );
};

export default AssignmentDetail;

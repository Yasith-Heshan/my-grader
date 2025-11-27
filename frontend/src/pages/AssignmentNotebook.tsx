import React, { useState, useEffect } from 'react';
import { Layout, Card, Button, Typography, Space, Tag, Divider, Alert, Spin, Modal, Table } from 'antd';
import { useParams, useNavigate } from 'react-router-dom';
import { CalendarOutlined, SendOutlined, PlayCircleOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { useAssignment } from '../hooks/useAssignments';
import { useCreateSubmission } from '../hooks/useSubmissions';
import CodeEditor from '../components/CodeEditor';
import axiosInstance from '../api/axiosInstance';
import { toast } from 'react-toastify';
import { Question } from '../api/assignmentApi';

const { Content } = Layout;
const { Title, Text, Paragraph } = Typography;

interface CellAnswer {
  cell_id: string;
  code: string;
}

interface TestResult {
  testcase_name: string;
  cell_id: string;
  score: number;
  max_score: number;
  feedback: string;
  passed: boolean;
}

interface QuestionCellProps {
  question: Question;
  code: string;
  onCodeChange: (code: string) => void;
  onTest: () => void;
  testing: boolean;
}

const QuestionCell: React.FC<QuestionCellProps> = ({
  question,
  code,
  onCodeChange,
  onTest,
  testing,
}) => {
  return (
    <Card 
      style={{ marginBottom: 24, border: '1px solid #e8e8e8' }}
      bodyStyle={{ padding: 0 }}
    >
      {/* Markdown Cell */}
      <div style={{
        padding: '16px 24px',
        background: '#fafafa',
        borderBottom: '1px solid #e8e8e8',
      }}>
        <Space direction="vertical" style={{ width: '100%' }} size="small">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Title level={5} style={{ margin: 0, color: '#1890ff' }}>
              Question {question.question_number}: {question.title}
            </Title>
            <Tag color="blue">{question.points} points</Tag>
          </div>
          <div style={{
            padding: '12px',
            background: 'white',
            borderRadius: '4px',
            border: '1px solid #d9d9d9',
          }}>
            <ReactMarkdown>{question.description}</ReactMarkdown>
          </div>
        </Space>
      </div>

      {/* Code Cell */}
      <div style={{ padding: '16px 24px' }}>
        <div style={{
          marginBottom: 8,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <Text type="secondary" style={{ fontFamily: 'monospace', fontSize: 12 }}>
            In [{question.question_number}]:
          </Text>
          <Button
            size="small"
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={onTest}
            loading={testing}
          >
            Run Tests
          </Button>
        </div>
        <div style={{
          border: '1px solid #d9d9d9',
          borderRadius: '4px',
          overflow: 'hidden',
        }}>
          <CodeEditor
            value={code}
            onChange={(value) => onCodeChange(value || '')}
            height="200px"
          />
        </div>
      </div>
    </Card>
  );
};

const AssignmentNotebook: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [answers, setAnswers] = useState<Map<string, string>>(new Map());
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [testing, setTesting] = useState(false);
  const [testingCell, setTestingCell] = useState<string | null>(null);
  const [showResults, setShowResults] = useState(false);

  const { data: assignment, isLoading } = useAssignment(id || '');
  const submitMutation = useCreateSubmission();

  // Initialize answers with starter code
  useEffect(() => {
    if (assignment?.questions && assignment.questions.length > 0) {
      const initialAnswers = new Map<string, string>();
      assignment.questions.forEach(q => {
        initialAnswers.set(q.cell_id, q.starter_code || '# Write your code here\n');
      });
      setAnswers(initialAnswers);
    }
  }, [assignment]);

  const handleCodeChange = (cellId: string, code: string) => {
    setAnswers(new Map(answers.set(cellId, code)));
  };

  const handleTestCell = async (cellId: string) => {
    if (!id) return;

    setTestingCell(cellId);
    setTesting(true);
    
    try {
      const response = await axiosInstance.post('/api/student/evaluate-cell', {
        assignment_id: id,
        cell_id: cellId,
        student_code: answers.get(cellId) || '',
      });

      const results = response.data.results || [];
      setTestResults(results);
      setShowResults(true);

      const totalScore = response.data.score || 0;
      const maxScore = response.data.max_score || 0;

      if (totalScore === maxScore) {
        toast.success(`✓ All tests passed! Score: ${totalScore}/${maxScore}`);
      } else if (totalScore > 0) {
        toast.info(`Partial score: ${totalScore}/${maxScore}`);
      } else {
        toast.error(`Tests failed: ${totalScore}/${maxScore}`);
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to test code');
    } finally {
      setTesting(false);
      setTestingCell(null);
    }
  };

  const handleSubmitAll = () => {
    if (!id) return;

    // Convert answers map to array format
    const answerArray: CellAnswer[] = Array.from(answers.entries()).map(([cell_id, code]) => ({
      cell_id,
      code,
    }));

    submitMutation.mutate(
      {
        assignment_id: id,
        answers: answerArray,
      },
      {
        onSuccess: () => {
          toast.success('Assignment submitted successfully!');
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
  const totalPoints = assignment.questions?.reduce((sum, q) => sum + q.points, 0) || 0;

  const testResultColumns = [
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
        <Tag color={passed ? 'success' : 'error'}>
          {passed ? 'PASSED' : 'FAILED'}
        </Tag>
      ),
    },
    {
      title: 'Score',
      key: 'score',
      render: (record: TestResult) => `${record.score}/${record.max_score}`,
    },
    {
      title: 'Feedback',
      dataIndex: 'feedback',
      key: 'feedback',
    },
  ];

  return (
    <Content style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Button onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>
        ← Back
      </Button>

      {/* Header Card */}
      <Card style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="small">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <Title level={2} style={{ margin: 0 }}>{assignment.title}</Title>
              <Space style={{ marginTop: 8 }}>
                <CalendarOutlined />
                <Text type={isOverdue ? 'danger' : 'secondary'}>
                  Due: {dueDate.toLocaleString()}
                </Text>
                {isOverdue && <Tag color="red">Overdue</Tag>}
              </Space>
            </div>
            <div style={{ textAlign: 'right' }}>
              <Text strong style={{ fontSize: 24, color: '#1890ff' }}>
                {totalPoints}
              </Text>
              <Text type="secondary"> points</Text>
            </div>
          </div>

          {assignment.description && (
            <>
              <Divider style={{ margin: '12px 0' }} />
              <div style={{
                padding: '12px',
                background: '#f5f5f5',
                borderRadius: '4px',
              }}>
                <ReactMarkdown>{assignment.description}</ReactMarkdown>
              </div>
            </>
          )}
        </Space>
      </Card>

      {/* Notebook-style Questions */}
      {!assignment.questions || assignment.questions.length === 0 ? (
        <Alert
          message="No questions available"
          description="This assignment doesn't have any questions yet."
          type="warning"
          showIcon
        />
      ) : (
        <>
          {assignment.questions.map((question) => (
            <QuestionCell
              key={question.cell_id}
              question={question}
              code={answers.get(question.cell_id) || ''}
              onCodeChange={(code) => handleCodeChange(question.cell_id, code)}
              onTest={() => handleTestCell(question.cell_id)}
              testing={testing && testingCell === question.cell_id}
            />
          ))}

          {/* Submit Button */}
          <Card>
            <div style={{ textAlign: 'center' }}>
              <Button
                type="primary"
                size="large"
                icon={<SendOutlined />}
                onClick={handleSubmitAll}
                loading={submitMutation.isPending}
                disabled={answers.size === 0}
              >
                Submit All Answers
              </Button>
              <Paragraph type="secondary" style={{ marginTop: 8, marginBottom: 0 }}>
                Make sure to test your code before submitting!
              </Paragraph>
            </div>
          </Card>
        </>
      )}

      {/* Test Results Modal */}
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
          columns={testResultColumns}
          rowKey="testcase_name"
          pagination={false}
        />
      </Modal>
    </Content>
  );
};

export default AssignmentNotebook;

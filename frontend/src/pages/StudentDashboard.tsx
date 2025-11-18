import React from 'react';
import { Layout, Card, List, Button, Typography, Tag, Empty, Space } from 'antd';
import { CalendarOutlined, FileTextOutlined, TrophyOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAssignments } from '../hooks/useAssignments';
import { useMySubmissions } from '../hooks/useSubmissions';

const { Content } = Layout;
const { Title, Text, Paragraph } = Typography;

const StudentDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { data: assignments, isLoading: assignmentsLoading } = useAssignments();
  const { data: submissions, isLoading: submissionsLoading } = useMySubmissions();

  const getSubmissionStatus = (assignmentId: string) => {
    const submission = submissions?.find((s) => s.assignment_id === assignmentId);
    if (!submission) return { status: 'not_submitted', color: 'default', text: 'Not Submitted' };
    if (!submission.graded) return { status: 'pending', color: 'orange', text: 'Pending Grade' };
    return { status: 'graded', color: 'green', text: 'Graded' };
  };

  const getScore = (assignmentId: string) => {
    const submission = submissions?.find((s) => s.assignment_id === assignmentId);
    if (submission && submission.graded) {
      return `${submission.score}/${submission.max_score}`;
    }
    return 'N/A';
  };

  return (
    <Content style={{ padding: '24px' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Card>
          <Title level={2}>
            <FileTextOutlined /> Available Assignments
          </Title>
          {assignmentsLoading ? (
            <Text>Loading assignments...</Text>
          ) : assignments && assignments.length > 0 ? (
            <List
              dataSource={assignments}
              renderItem={(assignment) => {
                const status = getSubmissionStatus(assignment.id);
                const score = getScore(assignment.id);
                const dueDate = new Date(assignment.due_date);
                const isOverdue = dueDate < new Date();

                return (
                  <List.Item
                    key={assignment.id}
                    actions={[
                      <Button
                        type="primary"
                        onClick={() => navigate(`/assignment/${assignment.id}`)}
                      >
                        {status.status === 'not_submitted' ? 'Start' : 'View'}
                      </Button>,
                    ]}
                  >
                    <List.Item.Meta
                      title={
                        <Space>
                          <span>{assignment.title}</span>
                          {isOverdue && status.status === 'not_submitted' && (
                            <Tag color="red">Overdue</Tag>
                          )}
                        </Space>
                      }
                      description={
                        <Space direction="vertical" size="small">
                          <Text type="secondary">{assignment.description.substring(0, 100)}...</Text>
                          <Space>
                            <CalendarOutlined />
                            <Text type={isOverdue ? 'danger' : 'secondary'}>
                              Due: {dueDate.toLocaleString()}
                            </Text>
                          </Space>
                          <Space>
                            <Text>Status:</Text>
                            <Tag color={status.color}>{status.text}</Tag>
                            {status.status === 'graded' && (
                              <>
                                <TrophyOutlined />
                                <Text strong>{score}</Text>
                              </>
                            )}
                          </Space>
                        </Space>
                      }
                    />
                  </List.Item>
                );
              }}
            />
          ) : (
            <Empty description="No assignments available" />
          )}
        </Card>

        <Card>
          <Title level={3}>My Recent Submissions</Title>
          {submissionsLoading ? (
            <Text>Loading submissions...</Text>
          ) : submissions && submissions.length > 0 ? (
            <List
              dataSource={submissions.slice(0, 5)}
              renderItem={(submission) => {
                const assignment = assignments?.find((a) => a.id === submission.assignment_id);
                return (
                  <List.Item key={submission.id}>
                    <List.Item.Meta
                      title={assignment?.title || 'Unknown Assignment'}
                      description={
                        <Space>
                          <Text type="secondary">
                            Submitted: {new Date(submission.submitted_at).toLocaleString()}
                          </Text>
                          {submission.graded ? (
                            <>
                              <Tag color="green">Graded</Tag>
                              <Text strong>
                                Score: {submission.score}/{submission.max_score}
                              </Text>
                            </>
                          ) : (
                            <Tag color="orange">Pending</Tag>
                          )}
                        </Space>
                      }
                    />
                  </List.Item>
                );
              }}
            />
          ) : (
            <Empty description="No submissions yet" />
          )}
        </Card>
      </Space>
    </Content>
  );
};

export default StudentDashboard;

import React from 'react';
import { Layout, Card, List, Button, Typography, Tag, Empty, Space, Dropdown } from 'antd';
import { CalendarOutlined, FileTextOutlined, TrophyOutlined, UserOutlined, LogoutOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useStudentAssignments } from '../hooks/useAssignments';
import { useMySubmissions } from '../hooks/useSubmissions';
import './StudentDashboard.css';

const { Content } = Layout;
const { Title, Text, Paragraph } = Typography;

const StudentDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { data: assignments, isLoading: assignmentsLoading } = useStudentAssignments();
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
    <Content style={{ padding: '24px', minHeight: '100vh' }}>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2} style={{ margin: 0 }}>Student Dashboard</Title>
        <Dropdown
          menu={{
            items: [
              {
                key: 'profile',
                icon: <UserOutlined />,
                label: `${user?.name} (${user?.email})`,
              },
              {
                type: 'divider',
              },
              {
                key: 'logout',
                icon: <LogoutOutlined />,
                label: 'Logout',
                onClick: () => {
                  logout();
                  navigate('/login');
                },
              },
            ],
          }}
        >
          <Button icon={<UserOutlined />}>{user?.name}</Button>
        </Dropdown>
      </div>

      <Space direction="vertical" size="large" style={{ width: '100%', display: 'flex' }}>
        <Card>
          <div style={{ marginBottom: 24 }}>
            <Title level={3} style={{ margin: 0 }}>
              <FileTextOutlined style={{ marginRight: 8 }} /> Available Assignments
            </Title>
          </div>
          {assignmentsLoading ? (
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <Text>Loading assignments...</Text>
            </div>
          ) : assignments && assignments.length > 0 ? (
            <List
              itemLayout="horizontal"
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
                        size="large"
                        onClick={() => navigate(`/assignment/${assignment.id}`)}
                      >
                        {status.status === 'not_submitted' ? 'Start Assignment' : 'View Details'}
                      </Button>,
                    ]}
                    style={{ padding: '16px 0', alignItems: 'flex-start' }}
                  >
                    <List.Item.Meta
                      style={{ flex: 1, minWidth: 0 }}
                      title={
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', width: '100%' }}>
                          <span style={{ fontSize: 16, fontWeight: 600, whiteSpace: 'normal', wordBreak: 'break-word' }}>{assignment.title}</span>
                          {isOverdue && status.status === 'not_submitted' && (
                            <Tag color="red">Overdue</Tag>
                          )}
                          <Tag color={status.color}>{status.text}</Tag>
                        </div>
                      }
                      description={
                        <div style={{ marginTop: 8, width: '100%' }}>
                          <Paragraph
                            ellipsis={{ rows: 2 }}
                            style={{ marginBottom: 12, color: '#666', whiteSpace: 'normal' }}
                          >
                            {assignment.description}
                          </Paragraph>
                          <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap', alignItems: 'center', width: '100%' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 6, whiteSpace: 'nowrap' }}>
                              <CalendarOutlined />
                              <Text type={isOverdue ? 'danger' : 'secondary'}>
                                Due: {dueDate.toLocaleDateString()} at {dueDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                              </Text>
                            </div>
                            {status.status === 'graded' && (
                              <div style={{ display: 'flex', alignItems: 'center', gap: 6, whiteSpace: 'nowrap' }}>
                                <TrophyOutlined style={{ color: '#faad14' }} />
                                <Text strong style={{ fontSize: 15 }}>Score: {score}</Text>
                              </div>
                            )}
                          </div>
                        </div>
                      }
                    />
                  </List.Item>
                );
              }}
            />
          ) : (
            <Empty
              description="No assignments available"
              style={{ padding: '40px 0' }}
            />
          )}
        </Card>

        <Card>
          <div style={{ marginBottom: 24 }}>
            <Title level={3} style={{ margin: 0 }}>My Recent Submissions</Title>
          </div>
          {submissionsLoading ? (
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <Text>Loading submissions...</Text>
            </div>
          ) : submissions && submissions.length > 0 ? (
            <List
              itemLayout="horizontal"
              dataSource={submissions.slice(0, 5)}
              renderItem={(submission) => {
                const assignment = assignments?.find((a) => a.id === submission.assignment_id);
                return (
                  <List.Item key={submission.id} style={{ padding: '12px 0', alignItems: 'flex-start' }}>
                    <List.Item.Meta
                      style={{ flex: 1, minWidth: 0 }}
                      title={<span style={{ fontSize: 15, whiteSpace: 'normal', wordBreak: 'break-word' }}>{assignment?.title || 'Unknown Assignment'}</span>}
                      description={
                        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'center', marginTop: 4, width: '100%' }}>
                          <Text type="secondary" style={{ whiteSpace: 'nowrap' }}>
                            Submitted: {new Date(submission.submitted_at).toLocaleDateString()} at {new Date(submission.submitted_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </Text>
                          {submission.graded ? (
                            <>
                              <Tag color="green">Graded</Tag>
                              <Text strong style={{ whiteSpace: 'nowrap' }}>
                                Score: {submission.score}/{submission.max_score}
                              </Text>
                            </>
                          ) : (
                            <Tag color="orange">Pending</Tag>
                          )}
                        </div>
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

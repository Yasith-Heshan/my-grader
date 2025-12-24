import React, { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { userApi } from '../api/userApi';
import {
  Table,
  Card,
  Row,
  Col,
  Typography,
  Spin,
  Tag,
  Progress,
  Empty,
  Tabs,
} from 'antd';

const { Title } = Typography;

interface Submission {
  _id: string;
  id: string;
  student_id: string;
  assignment_id: string;
  status: string;
  score: number;
  max_score: number;
  submitted_at: string;
  feedback?: string;
}

const AdminAssignments: React.FC = () => {
  const { data: submissions, isLoading } = useQuery({
    queryKey: ['adminSubmissions'],
    queryFn: userApi.getAdminSubmissions,
    retry: 0,
  });

  // Group submissions by assignment
  const groupedSubmissions = useMemo(() => {
    if (!submissions) return {};

    return submissions.reduce((acc: any, submission: Submission) => {
      const assignmentId = submission.assignment_id;
      if (!acc[assignmentId]) {
        acc[assignmentId] = [];
      }
      acc[assignmentId].push(submission);
      return acc;
    }, {});
  }, [submissions]);

  const getStatusColor = (status: string) => {
    const statusMap: { [key: string]: string } = {
      pending: 'orange',
      graded: 'green',
      submitted: 'blue',
      draft: 'default',
    };
    return statusMap[status.toLowerCase()] || 'default';
  };

  const getSubmissionScore = (submission: Submission) => {
    if (!submission.max_score || submission.max_score === 0) return 0;
    return Math.round((submission.score / submission.max_score) * 100);
  };

  const submissionColumns = [
    {
      title: 'Student ID',
      dataIndex: 'student_id',
      key: 'student_id',
      render: (text: string) => text.substring(0, 8),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>{status}</Tag>
      ),
    },
    {
      title: 'Score',
      dataIndex: 'score',
      key: 'score',
      render: (_score: number, record: Submission) => {
        const percentage = getSubmissionScore(record);
        return (
          <Progress
            type="circle"
            percent={percentage}
            width={50}
            strokeColor={percentage >= 70 ? '#52c41a' : percentage >= 50 ? '#faad14' : '#f5222d'}
          />
        );
      },
    },
    {
      title: 'Submitted',
      dataIndex: 'submitted_at',
      key: 'submitted_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
  ];

  const items = Object.entries(groupedSubmissions).map(([assignmentId, assignmentSubs]: [string, any]) => {
    const totalSubmissions = assignmentSubs.length;
    const gradedSubmissions = assignmentSubs.filter((s: Submission) => s.status === 'graded').length;
    const avgScore =
      assignmentSubs.length > 0
        ? Math.round(
            (assignmentSubs.reduce((sum: number, s: Submission) => sum + getSubmissionScore(s), 0) /
              assignmentSubs.length)
          )
        : 0;

    return {
      key: assignmentId,
      label: `Assignment ${assignmentId.substring(0, 8)}... (${totalSubmissions} submissions)`,
      children: (
        <Card>
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={8}>
              <Card size="small">
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold' }}>{totalSubmissions}</div>
                  <div style={{ color: '#999' }}>Total Submissions</div>
                </div>
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small">
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold' }}>{gradedSubmissions}</div>
                  <div style={{ color: '#999' }}>Graded</div>
                </div>
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small">
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold' }}>{avgScore}%</div>
                  <div style={{ color: '#999' }}>Average Score</div>
                </div>
              </Card>
            </Col>
          </Row>

          <Table
            dataSource={assignmentSubs}
            columns={submissionColumns}
            rowKey={(r) => r.id || r._id}
            pagination={{ pageSize: 10 }}
          />
        </Card>
      ),
    };
  });

  if (isLoading) return <Spin />;

  if (!submissions || submissions.length === 0) {
    return (
      <div style={{ padding: 24 }}>
        <Title level={3}>Assignments & Submissions</Title>
        <Empty description="No submissions yet" />
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <Title level={3}>Assignments & Submissions Overview</Title>
      <p>Monitor all student submissions across assignments.</p>

      {items.length > 0 ? (
        <Tabs items={items} />
      ) : (
        <Empty description="No submissions found" />
      )}
    </div>
  );
};

export default AdminAssignments;

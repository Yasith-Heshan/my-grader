import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { userApi } from '../api/userApi';
import {
  Table,
  Card,
  Typography,
  Spin,
  Tag,
  Progress,
  Empty,
  Space,
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

const AdminSubmissions: React.FC = () => {
  const { data: submissions, isLoading } = useQuery({
    queryKey: ['adminSubmissions'],
    queryFn: userApi.getAdminSubmissions,
    retry: 0,
  });

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

  const columns = [
    {
      title: 'Submission ID',
      dataIndex: '_id',
      key: '_id',
      render: (text: string) => text.substring(0, 8),
      width: 100,
    },
    {
      title: 'Student ID',
      dataIndex: 'student_id',
      key: 'student_id',
      render: (text: string) => text.substring(0, 8),
      width: 100,
    },
    {
      title: 'Assignment ID',
      dataIndex: 'assignment_id',
      key: 'assignment_id',
      render: (text: string) => text.substring(0, 8),
      width: 100,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>{status}</Tag>
      ),
      width: 100,
    },
    {
      title: 'Score',
      dataIndex: 'score',
      key: 'score',
      render: (score: number, record: Submission) => {
        const percentage = getSubmissionScore(record);
        return (
          <Space>
            <Progress
              type="circle"
              percent={percentage}
              width={50}
              strokeColor={
                percentage >= 70
                  ? '#52c41a'
                  : percentage >= 50
                  ? '#faad14'
                  : '#f5222d'
              }
            />
            <span>{score.toFixed(1)}/{record.max_score || 0}</span>
          </Space>
        );
      },
      width: 120,
    },
    {
      title: 'Submitted',
      dataIndex: 'submitted_at',
      key: 'submitted_at',
      render: (date: string) => {
        if (!date) return '-';
        return new Date(date).toLocaleDateString();
      },
      width: 120,
    },
    {
      title: 'Feedback',
      dataIndex: 'feedback',
      key: 'feedback',
      render: (feedback?: string) => feedback || '-',
      width: 200,
    },
  ];

  if (isLoading) return <Spin />;

  if (!submissions || submissions.length === 0) {
    return (
      <div style={{ padding: 24 }}>
        <Title level={3}>All Submissions</Title>
        <Empty description="No submissions found" />
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <Title level={3}>All Student Submissions</Title>
      <p>View and monitor all student submissions across the system.</p>

      <Card style={{ marginTop: 24 }}>
        <Table
          dataSource={submissions}
          columns={columns}
          rowKey={(r) => r.id || r._id}
          pagination={{ pageSize: 20 }}
          scroll={{ x: 1200 }}
        />
      </Card>
    </div>
  );
};

export default AdminSubmissions;

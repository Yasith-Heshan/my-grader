import React from 'react';
import { Table, Tag, Button, Space, Card } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, SyncOutlined } from '@ant-design/icons';
import { Submission } from '../api/submissionApi';
import type { ColumnsType } from 'antd/es/table';

interface SubmissionListProps {
  submissions: Submission[];
  loading?: boolean;
  onGrade?: (submissionId: string) => void;
  onView?: (submission: Submission) => void;
  showActions?: boolean;
}

const SubmissionList: React.FC<SubmissionListProps> = ({
  submissions,
  loading = false,
  onGrade,
  onView,
  showActions = true,
}) => {
  const columns: ColumnsType<Submission> = [
    {
      title: 'Student',
      dataIndex: 'student_name',
      key: 'student_name',
      render: (name: string, record: any) => name || record.student_id || 'Unknown',
      sorter: (a, b) => (a.student_name || a.student_id || '').localeCompare(b.student_name || b.student_id || ''),
    },
    {
      title: 'Submitted At',
      dataIndex: 'submitted_at',
      key: 'submitted_at',
      render: (date: string) => new Date(date).toLocaleString(),
      sorter: (a, b) => new Date(a.submitted_at).getTime() - new Date(b.submitted_at).getTime(),
    },
    {
      title: 'Status',
      key: 'status',
      render: (_, record: any) => {
        // Handle both 'graded' boolean and 'status' string
        const isGraded = record.graded === true || record.status === 'completed';
        return (
          <Tag color={isGraded ? 'green' : 'orange'} icon={isGraded ? <CheckCircleOutlined /> : <SyncOutlined spin />}>
            {isGraded ? 'Graded' : 'Pending'}
          </Tag>
        );
      },
      filters: [
        { text: 'Graded', value: true },
        { text: 'Pending', value: false },
      ],
      onFilter: (value, record: any) => {
        const isGraded = record.graded === true || record.status === 'completed';
        return isGraded === value;
      },
    },
    {
      title: 'Score',
      key: 'score',
      render: (_, record: any) => {
        const isGraded = record.graded === true || record.status === 'completed';
        const score = record.score ?? record.total_score ?? 0;
        const maxScore = record.max_score ?? 0;
        return isGraded 
          ? `${score.toFixed(1)}/${maxScore.toFixed(1)}`
          : 'N/A';
      },
      sorter: (a: any, b: any) => {
        const scoreA = a.score ?? a.total_score ?? 0;
        const scoreB = b.score ?? b.total_score ?? 0;
        return scoreA - scoreB;
      },
    },
    {
      title: 'Pass Rate',
      key: 'pass_rate',
      render: (_, record: any) => {
        const isGraded = record.graded === true || record.status === 'completed';
        if (!isGraded || !record.test_results) return 'N/A';
        const passed = record.test_results.filter((t: any) => t.passed).length;
        const total = record.test_results.length;
        const percentage = Math.round((passed / total) * 100);
        return (
          <Tag color={percentage >= 70 ? 'green' : percentage >= 50 ? 'orange' : 'red'}>
            {passed}/{total} ({percentage}%)
          </Tag>
        );
      },
    },
  ];

  if (showActions) {
    columns.push({
      title: 'Actions',
      key: 'actions',
      render: (_, record: any) => {
        const isGraded = record.graded === true || record.status === 'completed';
        return (
          <Space>
            {onView && (
              <Button type="link" onClick={() => onView(record)}>
                View
              </Button>
            )}
            {onGrade && !isGraded && (
              <Button
                type="primary"
                size="small"
                onClick={() => onGrade(record.id)}
                icon={<SyncOutlined />}
              >
                Grade
              </Button>
            )}
          </Space>
        );
      },
    });
  }

  return (
    <Card>
      <Table
        columns={columns}
        dataSource={submissions}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />
    </Card>
  );
};

export default SubmissionList;

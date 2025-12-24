import React from 'react';
import { Table, Tag, Button, Space, Card } from 'antd';
import { CheckCircleOutlined, SyncOutlined } from '@ant-design/icons';
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
      sorter: (a, b) => a.student_name.localeCompare(b.student_name),
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
      key: 'graded',
      dataIndex: 'graded',
      render: (graded: boolean) => (
        <Tag color={graded ? 'green' : 'orange'} icon={graded ? <CheckCircleOutlined /> : <SyncOutlined spin />}>
          {graded ? 'Graded' : 'Pending'}
        </Tag>
      ),
      filters: [
        { text: 'Graded', value: true },
        { text: 'Pending', value: false },
      ],
      onFilter: (value, record) => record.graded === value,
    },
    {
      title: 'Score',
      key: 'score',
      render: (_, record) =>
        record.graded && record.score !== undefined
          ? `${record.score}/${record.max_score}`
          : 'N/A',
      sorter: (a, b) => (a.score || 0) - (b.score || 0),
    },
    {
      title: 'Pass Rate',
      key: 'pass_rate',
      render: (_, record) => {
        if (!record.graded || !record.test_results) return 'N/A';
        const passed = record.test_results.filter((t) => t.passed).length;
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
      render: (_, record) => (
        <Space>
          {onView && (
            <Button type="link" onClick={() => onView(record)}>
              View
            </Button>
          )}
          {onGrade && !record.graded && (
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
      ),
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

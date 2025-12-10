import React, { useState } from 'react';
import { Layout, Card, Button, Space, Table, Modal, Typography, Spin, Empty, Tabs, Dropdown } from 'antd';
import { PlusOutlined, EyeOutlined, DeleteOutlined, UserOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useAssignments, useDeleteAssignment, useCreateAssignment } from '../hooks/useAssignments';
import { useSubmissions, useGradeSubmission } from '../hooks/useSubmissions';
import AssignmentForm from '../components/AssignmentForm';
import SubmissionList from '../components/SubmissionList';
import ResultChart from '../components/ResultChart';
import TestCaseManager from '../components/TestCaseManager';
import { Assignment, CreateAssignmentDTO } from '../api/assignmentApi';
import type { ColumnsType } from 'antd/es/table';

const { Content } = Layout;
const { Title } = Typography;

const TeacherDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [selectedAssignment, setSelectedAssignment] = useState<Assignment | null>(null);
  const [viewSubmissions, setViewSubmissions] = useState(false);

  const { data: assignments, isLoading } = useAssignments();
  const createMutation = useCreateAssignment();
  const deleteMutation = useDeleteAssignment();
  const gradeMutation = useGradeSubmission();
  const { data: submissions, isLoading: submissionsLoading } = useSubmissions(
    selectedAssignment?.id || ''
  );

  const handleCreateAssignment = (values: CreateAssignmentDTO) => {
    createMutation.mutate(values, {
      onSuccess: () => {
        setIsModalVisible(false);
      },
    });
  };

  const handleDeleteAssignment = (id: string) => {
    Modal.confirm({
      title: 'Are you sure you want to delete this assignment?',
      content: 'This action cannot be undone.',
      okText: 'Delete',
      okType: 'danger',
      onOk: () => {
        deleteMutation.mutate(id);
      },
    });
  };

  const handleViewSubmissions = (assignment: Assignment) => {
    setSelectedAssignment(assignment);
    setViewSubmissions(true);
  };

  const handleGradeSubmission = (submissionId: string) => {
    gradeMutation.mutate(submissionId);
  };

  const columns: ColumnsType<Assignment> = [
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      sorter: (a, b) => a.title.localeCompare(b.title),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
      sorter: (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    },
    {
      title: 'Due Date',
      dataIndex: 'due_date',
      key: 'due_date',
      render: (date: string) => new Date(date).toLocaleDateString(),
      sorter: (a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            icon={<EyeOutlined />}
            onClick={() => handleViewSubmissions(record)}
          >
            View Submissions
          </Button>
          <Button
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteAssignment(record.id)}
          >
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  if (viewSubmissions && selectedAssignment) {
    return (
      <Content style={{ padding: '24px' }}>
        <Button onClick={() => setViewSubmissions(false)} style={{ marginBottom: 16 }}>
          ← Back to Assignments
        </Button>
        <Title level={2}>{selectedAssignment.title}</Title>

        <Tabs
          defaultActiveKey="submissions"
          items={[
            {
              key: 'submissions',
              label: 'Submissions',
              children: (
                <Space direction="vertical" size="large" style={{ width: '100%' }}>
                  {submissionsLoading ? (
                    <Spin />
                  ) : submissions && submissions.length > 0 ? (
                    <>
                      <SubmissionList
                        submissions={submissions}
                        onGrade={handleGradeSubmission}
                      />
                      <ResultChart submissions={submissions} type="bar" />
                      <ResultChart submissions={submissions} type="pie" />
                    </>
                  ) : (
                    <Empty description="No submissions yet" />
                  )}
                </Space>
              ),
            },
            {
              key: 'testcases',
              label: 'Cell Test Cases',
              children: <TestCaseManager assignmentId={selectedAssignment.id} />,
            },
          ]}
        />
      </Content>
    );
  }

  return (
    <Content style={{ padding: '24px' }}>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={3} style={{ margin: 0 }}>Teacher Dashboard</Title>
      </div>
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Title level={2} style={{ margin: 0 }}>
              My Assignments
            </Title>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setIsModalVisible(true)}
              size="large"
            >
              Create Assignment
            </Button>
          </div>

          <Table
            columns={columns}
            dataSource={assignments || []}
            rowKey="id"
            loading={isLoading}
            pagination={{ pageSize: 10 }}
          />
        </Space>
      </Card>

      <Modal
        title="Create New Assignment"
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
        width={800}
      >
        <AssignmentForm
          onSubmit={handleCreateAssignment}
          loading={createMutation.isPending}
        />
      </Modal>
    </Content>
  );
};

export default TeacherDashboard;

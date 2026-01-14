import React from 'react';
import { Layout, Card, Button, Typography, Space, Tag, Divider, Spin, Alert, Descriptions, Table } from 'antd';
import { useParams, useNavigate } from 'react-router-dom';
import {
  CalendarOutlined,
  ArrowLeftOutlined,
  DockerOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined
} from '@ant-design/icons';
import { useAssignment } from '../hooks/useAssignments';
import DescriptionViewer from '../components/DescriptionViewer';
import type { ColumnsType } from 'antd/es/table';
import type { Question } from '../api/assignmentApi';

const { Content } = Layout;
const { Title, Text, Paragraph } = Typography;

const TeacherAssignmentDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: assignment, isLoading } = useAssignment(id || '');

  if (isLoading) {
    return (
      <Content style={{ padding: '24px' }}>
        <Spin size="large" tip="Loading assignment..." />
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

  const dueDate = assignment.due_date ? new Date(assignment.due_date) : null;
  const isOverdue = dueDate ? dueDate < new Date() : false;

  const questionColumns: ColumnsType<Question> = [
    {
      title: '#',
      dataIndex: 'question_number',
      key: 'question_number',
      width: 60,
      sorter: (a, b) => a.question_number - b.question_number,
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: 'Cell ID',
      dataIndex: 'cell_id',
      key: 'cell_id',
      render: (cellId: string) => <Tag color="blue">{cellId}</Tag>,
    },
    {
      title: 'Points',
      dataIndex: 'points',
      key: 'points',
      width: 100,
      render: (points: number) => <Tag color="green">{points} pts</Tag>,
    },
  ];

  return (
    <Content style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      <Button
        icon={<ArrowLeftOutlined />}
        onClick={() => navigate(-1)}
        style={{ marginBottom: 16 }}
      >
        Back to Dashboard
      </Button>

      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Assignment Header */}
        <Card>
          <Title level={2}>{assignment.title}</Title>
          <Space>
            <CalendarOutlined />
            <Text type={isOverdue ? 'danger' : 'secondary'}>
              Due: {dueDate ? dueDate.toLocaleString() : 'No due date'}
            </Text>
            {isOverdue && <Tag color="red">Overdue</Tag>}
          </Space>
          <Divider />

          {/* Assignment Description */}
          <Title level={4}>Description</Title>
          <div style={{
            padding: '16px',
            background: '#f5f5f5',
            borderRadius: '8px',
            marginBottom: '16px',
          }}>
            <DescriptionViewer content={assignment.description || 'No description provided'} />
          </div>
        </Card>

        {/* Docker Image Information */}
        {assignment.docker_image && (
          <Card
            title={
              <Space>
                <DockerOutlined style={{ fontSize: '20px', color: '#0db7ed' }} />
                <span>Custom Docker Image</span>
              </Space>
            }
          >
            <Descriptions bordered column={2}>
              <Descriptions.Item label="Image Name" span={2}>
                <Space>
                  <Text strong>{assignment.docker_image.name}</Text>
                  {assignment.docker_image.status === 'uploaded' ? (
                    <Tag icon={<CheckCircleOutlined />} color="success">
                      Uploaded
                    </Tag>
                  ) : (
                    <Tag icon={<CloseCircleOutlined />} color="error">
                      {assignment.docker_image.status}
                    </Tag>
                  )}
                </Space>
              </Descriptions.Item>

              <Descriptions.Item label="Description" span={2}>
                {assignment.docker_image.description}
              </Descriptions.Item>

              <Descriptions.Item label="Docker Hub Tag">
                <Text code>{assignment.docker_image.full_image_name}</Text>
              </Descriptions.Item>

              <Descriptions.Item label="Base Image">
                <Text code>{assignment.docker_image.base_image}</Text>
              </Descriptions.Item>

              {assignment.docker_image.size_mb && (
                <Descriptions.Item label="Image Size">
                  {assignment.docker_image.size_mb.toFixed(2)} MB
                </Descriptions.Item>
              )}

              <Descriptions.Item label="Created">
                {new Date(assignment.docker_image.created_at).toLocaleString()}
              </Descriptions.Item>

              <Descriptions.Item label="Installed Packages" span={2}>
                <Space wrap>
                  {assignment.docker_image.packages.length > 0 ? (
                    assignment.docker_image.packages.map((pkg) => (
                      <Tag key={pkg} color="purple">{pkg}</Tag>
                    ))
                  ) : (
                    <Text type="secondary">No additional packages</Text>
                  )}
                </Space>
              </Descriptions.Item>
            </Descriptions>
          </Card>
        )}

        {!assignment.docker_image && assignment.custom_docker_image_id && (
          <Card>
            <Alert
              message="Custom Docker Image Not Found"
              description="This assignment references a custom Docker image that no longer exists or could not be loaded."
              type="warning"
              showIcon
            />
          </Card>
        )}

        {!assignment.custom_docker_image_id && (
          <Card>
            <Alert
              message="Using Default Docker Image"
              description="This assignment uses the default Python environment for grading student submissions."
              type="info"
              showIcon
            />
          </Card>
        )}

        {/* Questions Table */}
        <Card title={<Title level={4} style={{ margin: 0 }}>Questions</Title>}>
          {assignment.questions && assignment.questions.length > 0 ? (
            <Table
              dataSource={assignment.questions}
              columns={questionColumns}
              rowKey="question_number"
              pagination={false}
              expandable={{
                expandedRowRender: (record) => (
                  <div style={{ padding: '16px' }}>
                    <Paragraph>
                      <Text strong>Description:</Text>
                    </Paragraph>
                    <div style={{
                      padding: '12px',
                      background: '#f5f5f5',
                      borderRadius: '4px',
                      marginBottom: '12px'
                    }}>
                      <DescriptionViewer content={record.description} />
                    </div>
                    {record.starter_code && (
                      <>
                        <Paragraph>
                          <Text strong>Starter Code:</Text>
                        </Paragraph>
                        <pre style={{
                          padding: '12px',
                          background: '#f5f5f5',
                          borderRadius: '4px',
                          overflow: 'auto'
                        }}>
                          <code>{record.starter_code}</code>
                        </pre>
                      </>
                    )}
                  </div>
                ),
              }}
            />
          ) : (
            <Alert
              message="No questions added yet"
              type="info"
              showIcon
            />
          )}
        </Card>

        {/* Assignment Metadata */}
        <Card title={<Title level={4} style={{ margin: 0 }}>Assignment Information</Title>}>
          <Descriptions bordered column={2}>
            <Descriptions.Item label="Created">
              {new Date(assignment.created_at).toLocaleString()}
            </Descriptions.Item>
            <Descriptions.Item label="Last Updated">
              {new Date(assignment.updated_at).toLocaleString()}
            </Descriptions.Item>
            <Descriptions.Item label="Assignment ID" span={2}>
              <Text code>{assignment.id}</Text>
            </Descriptions.Item>
            <Descriptions.Item label="Teacher ID" span={2}>
              <Text code>{assignment.teacher_id}</Text>
            </Descriptions.Item>
          </Descriptions>
        </Card>
      </Space>
    </Content>
  );
};

export default TeacherAssignmentDetails;

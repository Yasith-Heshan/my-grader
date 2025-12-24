import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Row, Col, Button, Typography, Space } from 'antd';
import {
  TeamOutlined,
  BookOutlined,
  FileTextOutlined,
} from '@ant-design/icons';

const { Title } = Typography;

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();

  const dashboardItems = [
    {
      title: 'User Management',
      description: 'Manage all teachers and students',
      icon: <TeamOutlined style={{ fontSize: 32, color: '#1890ff' }} />,
      action: () => navigate('/admin/users'),
      stats: 'View & Create',
    },
    {
      title: 'Assignments',
      description: 'View all assignments and submissions',
      icon: <BookOutlined style={{ fontSize: 32, color: '#52c41a' }} />,
      action: () => navigate('/admin/assignments'),
      stats: 'Overview',
    },
    {
      title: 'Submissions',
      description: 'Review student submissions',
      icon: <FileTextOutlined style={{ fontSize: 32, color: '#faad14' }} />,
      action: () => navigate('/admin/submissions'),
      stats: 'Monitor',
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>Admin Dashboard</Title>
      <p>Welcome Admin! Manage the system from here.</p>

      <Row gutter={24} style={{ marginTop: 24 }}>
        {dashboardItems.map((item, index) => (
          <Col span={8} key={index}>
            <Card
              hoverable
              onClick={item.action}
              style={{ textAlign: 'center', cursor: 'pointer' }}
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>{item.icon}</div>
                <Title level={4}>{item.title}</Title>
                <p>{item.description}</p>
                <Button type="primary" onClick={item.action}>
                  {item.stats}
                </Button>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
};

export default AdminDashboard;

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { userApi } from '../api/userApi';
import { Table, Card, Row, Col, Typography, Spin } from 'antd';

const { Title } = Typography;

const UserManagement: React.FC = () => {
  const { data: teachers, isLoading: loadingTeachers } = useQuery({
    queryKey: ['teachers'],
    queryFn: userApi.getTeachers,
    retry: 0,
  });
  const { data: students, isLoading: loadingStudents } = useQuery({
    queryKey: ['students'],
    queryFn: userApi.getStudents,
    retry: 0,
  });

  const teacherColumns = [
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Email', dataIndex: 'email', key: 'email' },
    { title: 'Created', dataIndex: 'created_at', key: 'created_at' },
  ];

  const studentColumns = [
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Email', dataIndex: 'email', key: 'email' },
    { title: 'Student Number', dataIndex: 'student_number', key: 'student_number' },
    { title: 'Created', dataIndex: 'created_at', key: 'created_at' },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Title level={3}>User Management</Title>

      <Row gutter={16}>
        <Col span={12}>
          <Card title="Teachers">
            {loadingTeachers ? <Spin /> : <Table dataSource={teachers || []} columns={teacherColumns} rowKey={(r) => r._id || r.id || r.email} pagination={false} />}
          </Card>
        </Col>

        <Col span={12}>
          <Card title="Students">
            {loadingStudents ? <Spin /> : <Table dataSource={students || []} columns={studentColumns} rowKey={(r) => r._id || r.id || r.email} pagination={false} />}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default UserManagement;

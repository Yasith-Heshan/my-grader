import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { userApi } from '../api/userApi';
import {
  Table,
  Card,
  Typography,
  Spin,
  Button,
  Modal,
  Form,
  Input,
  message,
  Tabs,
  Space,
} from 'antd';
import { PlusOutlined } from '@ant-design/icons';

const { Title } = Typography;

const AdminUsers: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [userType, setUserType] = useState<'teacher' | 'student'>('teacher');
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const { data: teachers, isLoading: loadingTeachers, refetch: refetchTeachers } = useQuery({
    queryKey: ['adminTeachers'],
    queryFn: userApi.getAdminTeachers,
    retry: 0,
  });

  const { data: students, isLoading: loadingStudents, refetch: refetchStudents } = useQuery({
    queryKey: ['adminStudents'],
    queryFn: userApi.getAdminStudents,
    retry: 0,
  });

  const handleCreateUser = async (values: any) => {
    try {
      setLoading(true);
      if (userType === 'teacher') {
        await userApi.createTeacher({
          name: values.name,
          email: values.email,
          password: values.password,
        });
        message.success('Teacher created successfully!');
        refetchTeachers();
      } else {
        await userApi.createStudent({
          name: values.name,
          email: values.email,
          password: values.password,
          student_number: values.student_number,
        });
        message.success('Student created successfully!');
        refetchStudents();
      }
      form.resetFields();
      setIsModalVisible(false);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to create user');
    } finally {
      setLoading(false);
    }
  };

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

  const items = [
    {
      key: 'teachers',
      label: `Teachers (${teachers?.length || 0})`,
      children: (
        <Card title="Teachers">
          {loadingTeachers ? (
            <Spin />
          ) : (
            <Table
              dataSource={teachers || []}
              columns={teacherColumns}
              rowKey={(r) => r.id}
              pagination={false}
            />
          )}
        </Card>
      ),
    },
    {
      key: 'students',
      label: `Students (${students?.length || 0})`,
      children: (
        <Card title="Students">
          {loadingStudents ? (
            <Spin />
          ) : (
            <Table
              dataSource={students || []}
              columns={studentColumns}
              rowKey={(r) => r.id}
              pagination={false}
            />
          )}
        </Card>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={3}>User Management</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setUserType('teacher');
            setIsModalVisible(true);
          }}
        >
          Create User
        </Button>
      </div>

      <Tabs items={items} />

      <Modal
        title={`Create ${userType === 'teacher' ? 'Teacher' : 'Student'} Account`}
        open={isModalVisible}
        onCancel={() => {
          setIsModalVisible(false);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateUser}
        >
          <Form.Item
            name="type"
            label="User Type"
            initialValue={userType}
          >
            <div style={{ marginBottom: 16 }}>
              <Space>
                <Button
                  type={userType === 'teacher' ? 'primary' : 'default'}
                  onClick={() => {
                    setUserType('teacher');
                    form.setFieldValue('type', 'teacher');
                  }}
                >
                  Teacher
                </Button>
                <Button
                  type={userType === 'student' ? 'primary' : 'default'}
                  onClick={() => {
                    setUserType('student');
                    form.setFieldValue('type', 'student');
                  }}
                >
                  Student
                </Button>
              </Space>
            </div>
          </Form.Item>

          <Form.Item
            name="name"
            label="Full Name"
            rules={[{ required: true, message: 'Please enter name' }]}
          >
            <Input placeholder="Enter full name" />
          </Form.Item>

          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Please enter email' },
              { type: 'email', message: 'Please enter valid email' },
            ]}
          >
            <Input placeholder="Enter email" />
          </Form.Item>

          {userType === 'student' && (
            <Form.Item
              name="student_number"
              label="Student Number (Optional)"
            >
              <Input placeholder="Enter student number" />
            </Form.Item>
          )}

          <Form.Item
            name="password"
            label="Password"
            rules={[
              { required: true, message: 'Please enter password' },
              { min: 6, message: 'Password must be at least 6 characters' },
            ]}
          >
            <Input.Password placeholder="Enter password" />
          </Form.Item>

          <Form.Item>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button onClick={() => setIsModalVisible(false)}>Cancel</Button>
              <Button type="primary" htmlType="submit" loading={loading}>
                Create {userType === 'teacher' ? 'Teacher' : 'Student'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AdminUsers;

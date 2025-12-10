import React, { useState } from 'react';
import { Card, Form, Input, Button, Radio, Typography, Space } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useRegister } from '../hooks/useUser';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';

const { Title, Text } = Typography;

const RegisterPage: React.FC = () => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);
    const registerMutation = useRegister();
    const navigate = useNavigate();

    const handleRegister = async (values: any) => {
        setLoading(true);
        try {
            await registerMutation.mutateAsync(values);
            toast.success('Registration successful');
            setLoading(false);
            // Redirect by role
            if (values.role === 'teacher') navigate('/teacher');
            else navigate('/student');
        } catch (err: any) {
            toast.error(err.response?.data?.detail || err.message || 'Registration failed');
            setLoading(false);
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        }}>
            <Card style={{ width: 480, boxShadow: '0 10px 40px rgba(0,0,0,0.1)' }}>
                <Space direction="vertical" size="large" style={{ width: '100%', textAlign: 'center' }}>
                    <div>
                        <Title level={2} style={{ marginBottom: 8 }}>Create Account</Title>
                        <Text type="secondary">Register as a teacher or a student</Text>
                    </div>

                    <Form form={form} onFinish={handleRegister} layout="vertical" initialValues={{ role: 'student' }} size="large">
                        <Form.Item name="name" label="Full name" rules={[{ required: true, message: 'Please enter your name' }]}>
                            <Input prefix={<UserOutlined />} placeholder="Your full name" />
                        </Form.Item>

                        <Form.Item name="email" label="Email" rules={[{ required: true, message: 'Please enter your email' }, { type: 'email', message: 'Enter a valid email' }]}>
                            <Input prefix={<MailOutlined />} placeholder="you@example.com" />
                        </Form.Item>

                        <Form.Item name="password" label="Password" rules={[{ required: true, message: 'Please enter a password' }, { min: 6, message: 'Password must be at least 6 characters' }]}>
                            <Input.Password prefix={<LockOutlined />} placeholder="Choose a strong password" />
                        </Form.Item>

                        <Form.Item name="role" label="Register as" rules={[{ required: true }]}>
                            <Radio.Group>
                                <Radio.Button value="teacher">Teacher</Radio.Button>
                                <Radio.Button value="student">Student</Radio.Button>
                            </Radio.Group>
                        </Form.Item>

                        <Form.Item name="student_number" label="Student Number (optional)">
                            <Input placeholder="S12345 (students only)" />
                        </Form.Item>

                        <Form.Item>
                            <Button type="primary" htmlType="submit" loading={loading} block>Sign Up</Button>
                        </Form.Item>
                    </Form>
                </Space>
            </Card>
        </div>
    );
};

export default RegisterPage;

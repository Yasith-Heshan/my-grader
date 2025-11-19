import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, Radio, Typography, Space } from 'antd';
import { UserOutlined, LockOutlined, LoginOutlined } from '@ant-design/icons';
import { useAuth } from '../context/AuthContext';

const { Title, Text } = Typography;

const LoginPage: React.FC = () => {
    const [form] = Form.useForm();
    const navigate = useNavigate();
    const { login } = useAuth();
    const [loading, setLoading] = useState(false);

    const handleLogin = (values: { email: string; password: string; role: 'teacher' | 'student' }) => {
        setLoading(true);

        // Simulate API call delay
        setTimeout(() => {
            login(values.email, values.password, values.role);
            setLoading(false);

            // Navigate based on role
            if (values.role === 'teacher') {
                navigate('/teacher');
            } else {
                navigate('/student');
            }
        }, 500);
    };

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        }}>
            <Card
                style={{
                    width: 450,
                    boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
                }}
            >
                <Space direction="vertical" size="large" style={{ width: '100%', textAlign: 'center' }}>
                    <div>
                        <Title level={2} style={{ marginBottom: 8 }}>Welcome Back</Title>
                        <Text type="secondary">Sign in to continue to Grading System</Text>
                    </div>

                    <Form
                        form={form}
                        onFinish={handleLogin}
                        layout="vertical"
                        initialValues={{ role: 'teacher' }}
                        size="large"
                    >
                        <Form.Item
                            name="email"
                            label="Email"
                            rules={[
                                { required: true, message: 'Please enter your email' },
                                { type: 'email', message: 'Please enter a valid email' }
                            ]}
                        >
                            <Input
                                prefix={<UserOutlined />}
                                placeholder="Enter your email"
                            />
                        </Form.Item>

                        <Form.Item
                            name="password"
                            label="Password"
                            rules={[{ required: true, message: 'Please enter your password' }]}
                        >
                            <Input.Password
                                prefix={<LockOutlined />}
                                placeholder="Enter your password"
                            />
                        </Form.Item>

                        <Form.Item
                            name="role"
                            label="Login as"
                            rules={[{ required: true }]}
                        >
                            <Radio.Group>
                                <Radio.Button value="teacher">Teacher</Radio.Button>
                                <Radio.Button value="student">Student</Radio.Button>
                            </Radio.Group>
                        </Form.Item>

                        <Form.Item style={{ marginBottom: 0 }}>
                            <Button
                                type="primary"
                                htmlType="submit"
                                icon={<LoginOutlined />}
                                loading={loading}
                                block
                            >
                                Sign In
                            </Button>
                        </Form.Item>
                    </Form>

                    <div style={{ marginTop: 16 }}>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                            Demo Mode: No backend validation required
                        </Text>
                    </div>
                </Space>
            </Card>
        </div>
    );
};

export default LoginPage;
